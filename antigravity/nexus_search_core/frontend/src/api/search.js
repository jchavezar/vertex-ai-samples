import axios from 'axios';
import { CONFIG } from './config';

/**
 * Utility to generate standard headers
 */
const getHeaders = (googleToken) => ({
  Authorization: `Bearer ${googleToken}`,
  'Content-Type': 'application/json',
  'X-Goog-User-Project': CONFIG.PROJECT_NUMBER
});

/**
 * Utility to map search results to a standard structure used by the UI
 */
const mapSearchResult = (sr) => {
  // Support multiple structures:
  // 1. { document: { name, structData, ... } }
  // 2. { name, structData, ... }
  // 3. { uri, title, ... }
  // 4. groundedContent/groundingChunks/references

  const doc = sr.document || sr;
  const structData = doc.structData || {};
  const derivedStructData = doc.derivedStructData || {};

  // Extract from the most likely places
  const name = doc.name || doc.id || (typeof sr.document === 'string' ? sr.document : "");

  // v1beta groundingChunks handling
  const chunkText = sr.content || sr.text || sr.retrieval_chunk?.text || "";
  const chunkTitle = sr.title || sr.retrieval_chunk?.title || "";
  const chunkUri = sr.uri || sr.link || sr.retrieval_chunk?.uri || "";

  const title =
    structData.title ||
    structData.name ||
    chunkTitle ||
    derivedStructData.title ||
    (typeof name === 'string' ? name.split('/').pop() : "Source Material");

  const uri =
    structData.url ||
    structData.url_for_connector ||
    chunkUri ||
    "";

  const snippet =
    sr.snippetInfo?.[0]?.snippet ||
    structData.snippet ||
    structData.description ||
    derivedStructData.snippets?.[0]?.snippet ||
    chunkText ||
    "";

  return {
    document: {
      name: name,
      structData: {
        title: title,
        url: uri,
        snippet: snippet,
        rank: structData.rank || sr.relevanceScore || 0,
        author: structData.author || "",
        file_type: structData.file_type || ""
      },
      derivedStructData: {
        snippets: sr.snippetInfo || derivedStructData.snippets || (snippet ? [{ snippet }] : []),
        title: title
      }
    }
  };
};

/**
 * Method: Answer (RAG)
 * Returns a generative answer with citations. Uses v1beta for improved model support.
 */
export const executeAnswer = async (googleToken, query, previousContext = null) => {
  const url = `/google-api/v1alpha/projects/${CONFIG.PROJECT_NUMBER}/locations/${CONFIG.LOCATION}/collections/default_collection/engines/${CONFIG.ENGINE_ID}/servingConfigs/default_search:answer`;

  let finalQuery = query;
  if (previousContext && previousContext.query && previousContext.answer) {
    finalQuery = `Context:\nQ: ${previousContext.query}\nA: ${previousContext.answer.substring(0, 500)}\n\nCurrent Question: ${query}`;
  }

  const payload = {
    query: { text: finalQuery },
    relatedQuestionsSpec: { enable: true },
    answerGenerationSpec: {
      modelSpec: { modelVersion: "stable" },
      includeCitations: true,
      ignoreNonAnswerSeekingQuery: false,
      ignoreLowRelevantContent: false,
      ignoreAdversarialQuery: true
    }
  };

  const resp = await axios.post(url, payload, { headers: getHeaders(googleToken) });
  const answerData = resp.data.answer;

  let extractedResults = [];
  if (answerData?.steps) {
    answerData.steps.forEach(step => {
      step.actions?.forEach(action => {
        if (action.observation?.searchResults) {
          const mappedResults = action.observation.searchResults.map(mapSearchResult);
          extractedResults.push(...mappedResults);
        }
      });
    });
  }

  return {
    answer: answerData?.answerText || "A summary could not be generated. Please check the sources below.",
    results: extractedResults,
    citations: answerData?.citations || []
  };
};

/**
 * Method: Classic Search
 * Returns raw search results without a generative answer.
 */
export const executeClassicSearch = async (googleToken, query) => {
  const url = `/google-api/v1alpha/projects/${CONFIG.PROJECT_NUMBER}/locations/${CONFIG.LOCATION}/collections/default_collection/engines/${CONFIG.ENGINE_ID}/servingConfigs/default_search:search`;

  const payload = {
    query: query,
    pageSize: 10
  };

  const resp = await axios.post(url, payload, { headers: getHeaders(googleToken) });

  const results = resp.data.results?.map(mapSearchResult) || [];

  return {
    answer: "Detailed results found in SharePoint. These documents contain the most relevant information for your query.",
    results: results
  };
};

/**
 * Method: StreamAssist (Modern RAG Streaming)
 * Streams an answer using the v1beta streamAnswer endpoint for perfect grounding.
 * This matches the "Gemini Enterprise" preview experience in Agent Builder.
 */
export const executeStreamAssist = async (googleToken, query, onChunk) => {
  // Use v1alpha streamAnswer on default_search for high-fidelity grounding matching console's "Search method"
  const url = `/google-api/v1alpha/projects/${CONFIG.PROJECT_NUMBER}/locations/${CONFIG.LOCATION}/collections/default_collection/engines/${CONFIG.ENGINE_ID}/servingConfigs/default_search:streamAnswer`;

  const payload = {
    query: { text: query },
    relatedQuestionsSpec: { enable: true },
    answerGenerationSpec: {
      modelSpec: { modelVersion: "stable" },
      includeCitations: true,
      ignoreNonAnswerSeekingQuery: false,
      ignoreLowRelevantContent: false,
      ignoreAdversarialQuery: true,
      promptSpec: {
        preamble: "You are a professional enterprise search assistant. Provide precise, grounded answers. If an employee ID, specific value or technical data is requested, extract it exactly from the provided context sources. NEVER refuse to answer if the information is present in the context."
      }
    }
  };

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      ...getHeaders(googleToken),
      'Accept': 'text/event-stream'
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`StreamAnswer API Error: ${response.status} - ${errorBody}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let fullAnswer = "";
  let extractedResults = [];
  let citations = [];

  let buffer = '';
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    let startIdx = 0;
    let depth = 0;
    let inString = false;
    let escaped = false;

    for (let i = 0; i < buffer.length; i++) {
      const char = buffer[i];

      if (escaped) {
        escaped = false;
        continue;
      }
      if (char === '\\') {
        escaped = true;
        continue;
      }
      if (char === '"') {
        inString = !inString;
        continue;
      }

      if (!inString) {
        if (char === '{') {
          if (depth === 0) startIdx = i;
          depth++;
        } else if (char === '}') {
          depth--;
          if (depth === 0) {
            const jsonStr = buffer.substring(startIdx, i + 1);
            try {
              const parsed = JSON.parse(jsonStr);
              processPacket(parsed);
            } catch (e) {
              console.warn('[STREAM_DEBUG] JSON parse error in segment:', e);
            }
            buffer = buffer.substring(i + 1);
            i = -1;
          }
        }
      }
    }
  }

  function processPacket(parsed) {
    // 1. Extract Answer text from streamAnswer response
    let answerText = parsed.answer?.answerText || "";

    if (answerText) {
      if (answerText.startsWith(fullAnswer)) {
        // If the new chunk is an accumulation of what we already have, replace it
        fullAnswer = answerText;
      } else if (!fullAnswer.endsWith(answerText)) {
      // Otherwise, it's a new delta, so append it (if not already a duplicate)
        fullAnswer += answerText;
      }
      onChunk(answerText, fullAnswer, extractedResults, citations);
    }

    // 2. Extract Results AND Citations
    let foundResults = [];

    const findGrounding = (obj) => {
      if (!obj || typeof obj !== 'object') return;

      if (Array.isArray(obj)) {
        obj.forEach(findGrounding);
        return;
      }

      // v1beta streamAnswer grounding locations
      if (obj.citations) {
        citations.push(...obj.citations);
      }

      if (obj.searchResults) foundResults.push(...obj.searchResults);

      // Standard grounding metadata
      if (obj.groundingMetadata?.groundingChunks) foundResults.push(...obj.groundingMetadata.groundingChunks);

      for (const key of Object.keys(obj)) {
        if (key !== 'answerText' && key !== 'text' && typeof obj[key] === 'object') {
          findGrounding(obj[key]);
        }
      }
    };

    findGrounding(parsed);

    if (foundResults.length > 0 || citations.length > 0) {
      const mapped = foundResults.map(mapSearchResult);
      mapped.forEach(m => {
        const isDup = extractedResults.some(er =>
          er.document.name === m.document.name ||
          (er.document.structData.url === m.document.structData.url && m.document.structData.url !== "")
        );
        if (!isDup) extractedResults.push(m);
      });
      onChunk('', fullAnswer, extractedResults, citations);
    }
  }

  // Fallback to classic search only if the model explicitly refused or no content
  if (fullAnswer.includes("I am sorry") || fullAnswer.includes("could not be generated") || !fullAnswer) {
    try {
      console.log('[STREAM_DEBUG] Quality check failed, trying fallback...');
      const fallback = await executeClassicSearch(googleToken, query);
      if (fallback.results?.length > 0) {
        extractedResults = fallback.results;
        onChunk("", fullAnswer, extractedResults, citations);
      }
    } catch (e) {
      console.error('[STREAM_DEBUG] Fallback failed:', e);
    }
  }

  return { answer: fullAnswer, results: extractedResults, citations };
};


/**
 * Universal Search Wrapper (for backward compatibility or combined logic)
 */
export const executeSearch = async (googleToken, query, previousContext = null, method = 'answer', onChunk = null) => {
  switch (method) {
    case 'search':
      return await executeClassicSearch(googleToken, query);
    case 'stream':
      return await executeStreamAssist(googleToken, query, onChunk);
    case 'answer':
    default:
      return await executeAnswer(googleToken, query, previousContext);
  }
};
