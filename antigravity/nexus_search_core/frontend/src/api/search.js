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
 * Method: Answer (Legacy RAG)
 * Returns a generative answer with citations.
 */
export const executeAnswer = async (googleToken, query, previousContext = null) => {
  const url = `/google-api/v1alpha/projects/${CONFIG.PROJECT_NUMBER}/locations/${CONFIG.LOCATION}/collections/default_collection/engines/${CONFIG.ENGINE_ID}/servingConfigs/default_config:answer`;

  let finalQuery = query;
  if (previousContext && previousContext.query && previousContext.answer) {
    finalQuery = `Context:\nQ: ${previousContext.query}\nA: ${previousContext.answer.substring(0, 500)}\n\nCurrent Question: ${query}`;
  }

  const payload = {
    query: { text: finalQuery },
    answerGenerationSpec: {
      modelSpec: { modelVersion: "stable" },
      includeCitations: true
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
    answer: answerData?.answerText || "No answer generated.",
    results: extractedResults
  };
};

/**
 * Method: Classic Search
 * Returns raw search results without a generative answer.
 */
export const executeClassicSearch = async (googleToken, query) => {
  const url = `/google-api/v1alpha/projects/${CONFIG.PROJECT_NUMBER}/locations/${CONFIG.LOCATION}/collections/default_collection/engines/${CONFIG.ENGINE_ID}/servingConfigs/default_config:search`;

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
 * Method: StreamAssist (Modern Agentic)
 * Streams an answer using the v1beta streamAnswer endpoint for better grounding.
 */
export const executeStreamAssist = async (googleToken, query, onChunk) => {
  // Use the agentic streamAssist endpoint as defined in the docs
  const url = `/google-api/v1beta/projects/${CONFIG.PROJECT_NUMBER}/locations/${CONFIG.LOCATION}/collections/default_collection/engines/${CONFIG.ENGINE_ID}/assistants/default_assistant:streamAssist`;

  const payload = {
    query: { text: query }
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
  // ... (reader loop)
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
    console.log('[STREAM_DEBUG_PACKET]', parsed);

    // 1. Extract Answer text
    let answerText = parsed.answerStep?.answerText || parsed.answer?.answerText || parsed.text || "";

    // v1beta assist replies handling
    if (!answerText && parsed.answer?.replies && Array.isArray(parsed.answer.replies)) {
      answerText = parsed.answer.replies.map(r => r.groundedContent?.content?.text || "").join("");
    }

    if (answerText) {
      fullAnswer += answerText;
      // Pass the current state of citations too
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

      // Check for citations in various places
      // v1beta assist replies grounding metadata
      if (obj.replies && Array.isArray(obj.replies)) {
        obj.replies.forEach(reply => {
          const groundedContent = reply.groundedContent;
          if (groundedContent?.citations) {
            citations.push(...groundedContent.citations);
          }
          if (reply.searchResults) foundResults.push(...reply.searchResults);
        });
      }

      // General groundingMetadata (used in streamAnswer)
      if (obj.groundingMetadata?.citations) {
        citations.push(...obj.groundingMetadata.citations);
      }

      // Standard results locations
      if (obj.groundingChunks) foundResults.push(...obj.groundingChunks);
      if (obj.groundingMetadata?.groundingChunks) foundResults.push(...obj.groundingMetadata.groundingChunks);
      if (obj.searchResults) foundResults.push(...obj.searchResults);
      if (obj.observation?.searchResults) foundResults.push(...obj.observation.searchResults);

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
      // Notify parent of new metadata
      onChunk('', fullAnswer, extractedResults, citations);
    }
  }

  // Fallback
  if (extractedResults.length === 0) {
    try {
      console.log('[STREAM_DEBUG] No results in stream, trying fallback...');
      const fallback = await executeClassicSearch(googleToken, query);
      if (fallback.results?.length > 0) {
        extractedResults = fallback.results;
        if (onChunk) onChunk("", fullAnswer, extractedResults, citations);
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
