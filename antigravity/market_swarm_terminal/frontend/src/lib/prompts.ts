/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/
import { Agent } from './presets/agents';
import { User } from './state';

export const createSystemInstructions = (agent: Agent, user: User) =>
  `Your name is ${agent.name} and you are in a conversation with the user\
${user.name ? ` (${user.name})` : ''}.

Your personality is described like this:
${agent.personality}\
${
  user.info
    ? `\nHere is some information about ${user.name || 'the user'}:
${user.info}

Use this information to make your response more personal.`
    : ''
}

Today's date is ${new Intl.DateTimeFormat(navigator.languages[0], {
    dateStyle: 'full',
  }).format(new Date())} at ${new Date()
    .toLocaleTimeString()
    .replace(/:\d\d /, ' ')}.

Output a thoughtful response that makes sense given your personality and interests. \
Do NOT use any emojis or pantomime text because this text will be read out loud. \
Keep it fairly concise, don't speak too many sentences at once. NEVER EVER repeat \
things you've said before in the conversation!`;
