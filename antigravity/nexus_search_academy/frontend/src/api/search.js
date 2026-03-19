import { CONFIG } from './config';

const getHeaders = (googleToken) => ({
  Authorization: `Bearer ${googleToken}`,
  'Content-Type': 'application/json',
  'X-Goog-User-Project': CONFIG.PROJECT_NUMBER
});

export const mapSearchResult = (sr) => {
  const doc = sr.document || sr;
  const structData = doc.structData || sr.structData || {};
  
  const name = doc.name || "";
  const title = structData.title || (typeof name === 'string' && name ? name.split('/').pop() : "Source Material");
  const uri = structData.url || "";
  const snippet = structData.snippet || structData.description || "";

  return {
    document: {
      name,
      structData: { title, url: uri, snippet, rank: structData.rank || 0 }
    }
  };
};

/**
 * streams an answer using the v1alpha streamAssist endpoint.
 */
export const executeStreamAssist = async (googleToken, query, onChunk, onLog) => {
  const url = `/api/stream/assist`;

  const payload = {
    query: query,
    context: [] 
  };

  if (onLog) onLog(`[Assist] POST ${url}`, payload, getHeaders(googleToken));

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
    throw new Error(`StreamAssist API Error: ${response.status} - ${errorBody}`);
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
      if (escaped) { escaped = false; continue; }
      if (char === '\\') { escaped = true; continue; }
      if (char === '"') { inString = !inString; continue; }

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
              if (onLog) onLog(`[Packet] Received Chunk`, parsed);
              processPacket(parsed);
            } catch (e) {
              console.warn('[STREAM_DEBUG] JSON parse error:', e);
            }
            buffer = buffer.substring(i + 1);
            i = -1;
          }
        }
      }
    }
  }

  function processPacket(parsed) {
    let answerText = parsed.answer?.answerText || "";

    if (!answerText && parsed.answer?.replies?.length > 0) {
      const reply = parsed.answer.replies[0];
      const content = reply.groundedContent?.content || {};
      answerText = content.text || "";
      if (!answerText && content.parts?.length > 0) {
        answerText = content.parts[0].text || "";
      }
    }

    // Check if packet contains thoughts or reasoning
    const thoughtText = parsed.answer?.thought || parsed.thought || 
                       parsed.answer?.replies?.[0]?.thought || 
                       parsed.answer?.replies?.[0]?.groundedContent?.content?.thought;

    if (thoughtText && !answerText.includes(thoughtText)) {
      // Wrap thought in custom tags so frontend can isolate it
      if (!fullAnswer.includes(`<thought>${thoughtText}</thought>`)) {
         fullAnswer = `<thought>${thoughtText}</thought>\n\n` + fullAnswer;
      }
    }

    if (answerText) {
      if (answerText.startsWith(fullAnswer)) {
        fullAnswer = answerText;
      } else if (!fullAnswer.endsWith(answerText)) {
        fullAnswer += answerText;
      }
      onChunk(answerText, fullAnswer, extractedResults, citations);
    }

    let foundResults = [];
    const findGrounding = (obj) => {
      if (!obj || typeof obj !== 'object') return;
      if (Array.isArray(obj)) { obj.forEach(findGrounding); return; }
      if (obj.citations) citations.push(...obj.citations);
      if (obj.searchResults) foundResults.push(...obj.searchResults);
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
        const existingIdx = extractedResults.findIndex(er =>
          er.document.name === m.document.name || er.document.structData?.url === m.document.structData?.url
        );
        if (existingIdx === -1) extractedResults.push(m);
      });
      onChunk('', fullAnswer, extractedResults, citations);
    }
  }

  return { answer: fullAnswer, results: extractedResults, citations };
};
