import { useEffect, useState, memo } from 'react';
import { Modality, Tool } from '@google/genai';

import Avatar from '../avatar/Avatar';
import IngredientsBubble, { Ingredient } from './IngredientsBubble';
import { NewsBubble } from './NewsBubble';
import { useLiveAPIContext } from '../../../contexts/LiveAPIContext';
import { createSystemInstructions } from '@/lib/prompts';
import { useAgent, useUser } from '@/lib/state';

const SHOW_INGREDIENTS_TOOL: Tool = {
  functionDeclarations: [
    {
      name: 'show_ingredients',
      description: 'Show the ingredients for a recipe to the user.',
      parameters: {
        type: 'OBJECT' as any,
        properties: {
          recipeName: {
            type: 'STRING' as any,
            description: 'The name of the recipe.',
          },
          ingredients: {
            type: 'ARRAY' as any,
            description: 'List of ingredients.',
            items: {
              type: 'STRING' as any,
            },
          },
        },
        required: ['recipeName', 'ingredients'],
      },
    },
  ],
};

const DISPLAY_NEWS_HEADLINE_TOOL: Tool = {
  functionDeclarations: [
    {
      name: 'display_news_headline',
      description: 'Display a breaking news headline/summary on the screen.',
      parameters: {
        type: 'OBJECT' as any,
        properties: {
          headline: {
            type: 'STRING' as any,
            description: 'The concise headline or summary of the news story.',
          },
        },
        required: ['headline'],
      },
    },
  ],
};

function KeynoteCompanion() {
  const { client, connected, setConfig } = useLiveAPIContext();
  const user = useUser();
  const { current } = useAgent();
  const [ingredientsData, setIngredientsData] = useState<{
    recipeName: string;
    ingredients: Ingredient[];
  } | null>(null);


  // Clear news when agent changes
  // Clear news when agent changes
  // useEffect(() => {
  //   setNewsHeadline(null);
  // }, [current.id]);

  // Set the configuration for the Live API
  useEffect(() => {
    setConfig({
      responseModalities: [Modality.AUDIO],
      speechConfig: {
        voiceConfig: {
          prebuiltVoiceConfig: { voiceName: current.voice },
        },
      },
      systemInstruction: {
        parts: [
          {
            text:
              createSystemInstructions(current, user) +
              (current.id === 'chef-shane'
                ? '\n\nIMPORTANT: When the user asks for a recipe, IMMEDIATELY call the "show_ingredients" tool with the full list of ingredients BEFORE you start explaining the steps. You do NOT need to ask for permission. Just show it.'
                : '')
          },
        ],
      },
      tools:
        current.id === 'chef-shane'
          ? [SHOW_INGREDIENTS_TOOL]
          : current.id === 'news-anchor'
          ? [{ googleSearch: {} }]
          : [],
    });
  }, [setConfig, user, current]);

  // Handle tool calls
  useEffect(() => {
    const onToolCall = (toolCall: any) => {
      const fc = toolCall.functionCalls.find(
        (fc: any) => fc.name === 'show_ingredients'
      );
      if (fc) {
        const { recipeName, ingredients } = fc.args;
        setIngredientsData({ recipeName, ingredients });
        client.sendToolResponse({
          functionResponses: [
            {
              response: { output: { success: true } },
              id: fc.id,
            },
          ],
        });
      }


    };
    client.on('toolcall', onToolCall);
    return () => {
      client.off('toolcall', onToolCall);
    };
  }, [client]);

  // Initiate the session when the Live API connection is established
  // Instruct the model to send an initial greeting message
  useEffect(() => {
    const beginSession = async () => {
      if (!connected) return;
      client.send(
        {
          text: 'Greet the user and introduce yourself and your role.',
        },
        true
      );
    };
    beginSession();
  }, [client, connected]);

  return (
    <div className="keynote-companion">
      <Avatar />

      {ingredientsData && (
        <IngredientsBubble
          recipeName={ingredientsData.recipeName}
          ingredients={ingredientsData.ingredients}
          onClose={() => setIngredientsData(null)}
        />
      )}
    </div>
  );
}

export default memo(KeynoteCompanion);
