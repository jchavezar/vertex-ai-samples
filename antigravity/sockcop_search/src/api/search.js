import axios from 'axios';
import { CONFIG } from './config';

export const executeSearch = async (googleToken, query) => {
  // Base path for the search service
  const url = `/google-api/v1alpha/projects/${CONFIG.PROJECT_NUMBER}/locations/${CONFIG.LOCATION}/collections/default_collection/engines/${CONFIG.ENGINE_ID}/servingConfigs/default_search:search`;

  const payload = {
    query: query,
    pageSize: 10,
    spellCorrectionSpec: { mode: "AUTO" },
    languageCode: "en-US",
    relevanceScoreSpec: { returnRelevanceScore: true },
    userInfo: { timeZone: "America/New_York" },
    contentSearchSpec: {
      snippetSpec: {
        returnSnippet: true
      },
      summarySpec: {
        summaryResultCount: 5,
        includeCitations: true
      },
      extractiveContentSpec: {
        maxExtractiveAnswerCount: 1,
        maxExtractiveSegmentCount: 1
      }
    },
    naturalLanguageQueryUnderstandingSpec: { filterExtractionCondition: "ENABLED" }
  };

  try {
    const resp = await axios.post(url, payload, {
      headers: {
        Authorization: `Bearer ${googleToken}`,
        'Content-Type': 'application/json'
      }
    });

    let searchData = resp.data;

    // Check if Discovery Engine skipped the summary (e.g., OUT_OF_DOMAIN_QUERY_IGNORED)
    const skipped = searchData.summary?.summarySkippedReasons?.length > 0;
    const noAnswer = !searchData.answer && (!searchData.summary || searchData.summary.summaryText?.includes("could not be generated"));

    // If Vertex refused to summarize, but DID return SharePoint documents
    if ((skipped || noAnswer) && searchData.results && searchData.results.length > 0) {
      console.log("[\u26A0\uFE0F GEMINI RAG] Vertex strict mode blocked summary. Delegating extracted SharePoint text directly to conversational Gemini 2.5 Flash...");
      try {
        const fallbackAnswer = await generateGeminiFallback(googleToken, query, searchData.results);
        if (fallbackAnswer) {
          // Inject the Gemini Flash answer directly into the UI state
          searchData.answer = fallbackAnswer;
          if (searchData.summary) {
            searchData.summary.summarySkippedReasons = []; // Clear visual errors
          }
        }
      } catch (geminiErr) {
        console.error("[GEMINI RAG] Fallback failed. Reverting to standard Vertex Search Error.", geminiErr);
      }
    }

    return searchData;
  } catch (err) {
    console.error('Search API Error:', err.response?.data || err.message);
    throw err;
  }
};

const generateGeminiFallback = async (googleToken, query, results) => {
  // 1. Compile all successfully retrieved SharePoint contexts into one string
  const contextText = results.slice(0, 5).map((res, i) => {
    const doc = res.document;
    const title = doc.derivedStructData?.title || doc.structData?.title || doc.structData?.name || "Unknown Document";

    let contextChunks = [];

    // Aggressively extract the largest blocks of text we can find
    // Extractive Segments are large paragraphs containing the richest context
    if (doc.derivedStructData?.extractiveSegments?.length > 0) {
      contextChunks.push(...doc.derivedStructData.extractiveSegments.map(s => s.content.replace(/<[^>]+>/g, '')));
    }
    // Extractive Answers are 1-2 sentence direct answers
    if (doc.derivedStructData?.extractiveAnswers?.length > 0) {
      contextChunks.push(...doc.derivedStructData.extractiveAnswers.map(a => a.content.replace(/<[^>]+>/g, '')));
    }
    // Snippets are short context windows
    if (doc.derivedStructData?.snippets?.length > 0) {
      contextChunks.push(...doc.derivedStructData.snippets.map(s => s.snippet.replace(/<[^>]+>/g, '')));
    }
    // Fallback block string content
    if (doc.structData?.snippet) {
      contextChunks.push(doc.structData.snippet.replace(/<[^>]+>/g, ''));
    }
    if (doc.structData?.content) {
      contextChunks.push(doc.structData.content.replace(/<[^>]+>/g, ''));
    }

    // Deduplicate and join all text found for this document
    const uniqueChunks = [...new Set(contextChunks)];
    return `[DOC ${i + 1}: ${title}]\nCONTENT: ${uniqueChunks.join(" ")}`;
  }).join("\n\n---\n\n");

  const promptText = `You are Sockcop Search, an enterprise intelligence assistant.
Your task is to answer the user's question accurately.

RULES:
1. ONLY base your answer on the provided SharePoint context below. 
2. Synthesize the context clearly and professionally.
3. If the answer is not in the documents provided below, say "I could not find information on that in the retrieved documents." Do not guess.

USER QUESTION: ${query}

--- SHAREPOINT CONTEXT ---
${contextText}`;

  // Use the standard Vertex AI GenerateContent endpoint
  // WIF Token seamlessly works here precisely because we set the scope to 'https://www.googleapis.com/auth/cloud-platform'
  const region = "us-central1";
  const geminiUrl = `/aiplatform-api/v1/projects/${CONFIG.PROJECT_NUMBER}/locations/${region}/publishers/google/models/gemini-2.5-flash:generateContent`;

  const payload = {
    contents: [{ role: "user", parts: [{ text: promptText }] }],
    generationConfig: { temperature: 0.1, maxOutputTokens: 2048 }
  };

  const res = await axios.post(geminiUrl, payload, {
    headers: {
      Authorization: `Bearer ${googleToken}`,
      'Content-Type': 'application/json'
    }
  });

  if (res.data?.candidates?.[0]?.content?.parts?.[0]?.text) {
    return res.data.candidates[0].content.parts[0].text;
  }
  return null;
};
