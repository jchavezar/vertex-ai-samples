import { useEffect, useState, memo } from 'react';
import { Modality, Tool } from '@google/genai';

import Avatar from '../avatar/Avatar';
import IngredientsBubble, { Ingredient } from './IngredientsBubble';
import TeachingOverlay from './TeachingOverlay';
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

const TEACHING_TOOLS: Tool = {
  functionDeclarations: [
    {
      name: 'update_topics',
      description: 'Update the list of learning topics/steps shown on the left.',
      parameters: {
        type: 'OBJECT' as any,
        properties: {
          topics: {
            type: 'ARRAY' as any,
            items: {
              type: 'OBJECT' as any,
              properties: {
                title: { type: 'STRING' as any },
                status: { type: 'STRING' as any, enum: ['pending', 'active', 'completed'] }
              }
            }
          }
        },
        required: ['topics']
      }
    },
    {
      name: 'show_info',
      description: 'Show an explanation bubble with text.',
      parameters: {
        type: 'OBJECT' as any,
        properties: {
          text: { type: 'STRING' as any },
        },
        required: ['text']
      }
    }
  ]
};

function KeynoteCompanion() {
  const { client, connected, setConfig } = useLiveAPIContext();
  const user = useUser();
  const { current } = useAgent();

  // Chef Shane State
  const [ingredientsData, setIngredientsData] = useState<{
    recipeName: string;
    ingredients: Ingredient[];
  } | null>(null);

  // Friendly Teacher State
  const [topics, setTopics] = useState<{ title: string; status: 'pending' | 'active' | 'completed' }[]>([]);
  const [infoBubble, setInfoBubble] = useState<{ text: string; visible: boolean } | null>(null);

  // Set the configuration for the Live API
  useEffect(() => {
    let tools: Tool[] = [];
    if (current.id === 'chef-shane') tools = [SHOW_INGREDIENTS_TOOL];
    else if (current.id === 'proper-paul') tools = [TEACHING_TOOLS, { googleSearch: {} }];
    else if (current.id === 'news-anchor') tools = [{ googleSearch: {} }];

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
                : '') +
              (current.id === 'proper-paul'
                ? '\n\nYou are an interactive teacher. Use the "update_topics" tool to outline the lesson plan at the start (usually 3-4 steps). Use "show_info" to highlight key concepts or definitions alongside your explanation. GROUND your facts using Google Search when explaining technical topics like Google Cloud.'
                : '')
          },
        ],
      },
      tools,
    });
  }, [setConfig, user, current]);

  // Handle tool calls
  useEffect(() => {
    const onToolCall = (toolCall: any) => {
      const fc = toolCall.functionCalls[0];
      if (!fc) return;

      try {
        if (fc.name === 'show_ingredients') {
          const { recipeName, ingredients } = fc.args;
          setIngredientsData({ recipeName, ingredients });
          client.sendToolResponse({
            functionResponses: [{
              name: 'show_ingredients',
              response: { result: { success: true } },
              id: fc.id
            }]
          });
        } else if (fc.name === 'update_topics') {
          console.log('Tool call update_topics:', fc.args);
          let topics = fc.args?.topics;
          if (!Array.isArray(topics)) {
            console.warn('update_topics: topics is not an array', topics);
            topics = [];
          }
          setTopics(topics.map((t: any) => {
            if (typeof t === 'string') return { title: t, status: 'pending' };
            if (typeof t === 'object' && t) return { title: t.title || 'Untitled', status: t.status || 'pending' };
            return { title: 'Unknown', status: 'pending' };
          }));
          client.sendToolResponse({
            functionResponses: [{
              name: 'update_topics',
              response: { result: { success: true } },
              id: fc.id
            }]
          });
        } else if (fc.name === 'show_info') {
          console.log('Tool call show_info:', fc.args);
          const text = fc.args?.text || '';
          if (text) setInfoBubble({ text, visible: true });
          client.sendToolResponse({
            functionResponses: [{
              name: 'show_info',
              response: { result: { success: true } },
              id: fc.id
            }]
          });
        }
      } catch (e) {
        console.error('Error handling tool call:', e, fc);
        // Attempt to reply success anyway to keep model happy, or fail?
        // Better to fail gracefully
        client.sendToolResponse({
          functionResponses: [{
            response: { name: fc.name, content: { success: false, error: String(e) } },
            id: fc.id
          }]
        });
      }
    };
    client.on('toolcall', onToolCall);
    return () => {
      client.off('toolcall', onToolCall);
    };
  }, [client]);

  // Initiate the session when the Live API connection is established
  useEffect(() => {
    const beginSession = async () => {
      if (!connected) return;
      client.send(
        {
          text: current.id === 'proper-paul'
            ? 'Greet the user enthusiastically and IMMEDIATELY use the "update_topics" tool to show 3-4 beginner-friendly topics about Vertex AI.'
            : 'Greet the user and introduce yourself and your role.',
        },
        true
      );
    };
    beginSession();

    // Expose for debugging/automation
    (window as any).sendDebugMessage = (text: string) => {
      if (!connected) return;
      client.send([{ text }]);
    };
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

      {current.id === 'proper-paul' && (
        <TeachingOverlay
          topics={topics}
          infoBubble={infoBubble}
          onCloseBubble={() => setInfoBubble(null)}
          onSelectTopic={(index) => {
            const topic = topics[index];
            if (topic) {
              // Send a message to the model to explain this topic
              client.send([{ text: `I want to learn about step ${index + 1}: "${topic.title}". Please explain it in detail, using 'show_info' to highlight key terms.` }]);

              // Optimistically set status to active for immediate feedback
              setTopics(prev => prev.map((t, i) => i === index ? { ...t, status: 'active' } : t));
            }
          }}
        />
      )}
    </div>
  );
}

export default memo(KeynoteCompanion);
