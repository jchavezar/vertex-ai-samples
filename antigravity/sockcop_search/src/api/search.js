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
        includeCitations: true,
        ignoreAdversarialQuery: false,
        ignoreNonAnswerSeekingQuery: false,
        modelSpec: {
          version: "stable"
        }
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
    return resp.data;
  } catch (err) {
    console.error('Search API Error:', err.response?.data || err.message);
    throw err;
  }
};
