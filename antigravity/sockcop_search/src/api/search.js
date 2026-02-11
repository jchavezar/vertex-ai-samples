import axios from 'axios';
import { CONFIG } from './config';

export const executeSearch = async (googleToken, query) => {
  // Base path for the answer service
  const url = `/google-api/v1alpha/projects/${CONFIG.PROJECT_NUMBER}/locations/${CONFIG.LOCATION}/collections/default_collection/engines/${CONFIG.ENGINE_ID}/servingConfigs/default_config:answer`;

  const payload = {
    query: {
      text: query
    },
    answerGenerationSpec: {
      modelSpec: {
        modelVersion: "stable"
      },
      includeCitations: true
    }
  };

  try {
    const resp = await axios.post(url, payload, {
      headers: {
        Authorization: `Bearer ${googleToken}`,
        'Content-Type': 'application/json',
        'X-Goog-User-Project': CONFIG.PROJECT_NUMBER
      }
    });

    const answerData = resp.data.answer;

    // We need to map the new 'answer' payload back to the format the UI is already expecting.
    // The UI expects an object with { answer: String, results: Array }
    // The search results are buried in the steps -> actions -> observation -> searchResults
    let extractedResults = [];
    if (answerData?.steps) {
      answerData.steps.forEach(step => {
        if (step.actions) {
          step.actions.forEach(action => {
            if (action.observation?.searchResults) {
              const mappedResults = action.observation.searchResults.map(sr => ({
                document: {
                  name: sr.document || "",
                  structData: {
                    title: sr.structData?.title || sr.title || "Unknown Document",
                    url: sr.structData?.url || sr.structData?.url_for_connector || sr.uri || "",
                    snippet: sr.snippetInfo?.[0]?.snippet || sr.structData?.description || "",
                    rank: sr.structData?.rank || 0,
                    author: sr.structData?.author || "",
                    file_type: sr.structData?.file_type || ""
                  },
                  derivedStructData: {
                    snippets: sr.snippetInfo || []
                  }
                }
              }));
              extractedResults.push(...mappedResults);
            }
          });
        }
      });
    }

    return {
      answer: answerData?.answerText || "No answer generated.",
      results: extractedResults
    };

  } catch (err) {
    console.error('Search API Error:', err.response?.data || err.message);
    throw err;
  }
};
