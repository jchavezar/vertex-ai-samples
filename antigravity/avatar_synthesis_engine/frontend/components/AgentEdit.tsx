/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/
import { useRef } from 'react';
import {
  Agent,
  AGENT_COLORS,
  INTERLOCUTOR_VOICE,
  INTERLOCUTOR_VOICES,
} from '@/lib/presets/agents';
import Modal from './Modal';
import c from 'classnames';
import { useAgent, useUI } from '@/lib/state';

export default function EditAgent() {
  const agent = useAgent(state => state.current);
  const updateAgent = useAgent(state => state.update);
  const nameInput = useRef(null);
  const { setShowAgentEdit } = useUI();

  function onClose() {
    setShowAgentEdit(false);
  }

  function updateCurrentAgent(adjustments: Partial<Agent>) {
    updateAgent(agent.id, adjustments);
  }

  return (
    <Modal onClose={() => onClose()}>
      <div className="editAgent">
        <div>
          <form>
            <div>
              <input
                className="largeInput"
                type="text"
                placeholder="Name"
                value={agent.name}
                onChange={e => updateCurrentAgent({ name: e.target.value })}
                ref={nameInput}
              />
            </div>

            <div>
              <label>
                Personality
                <textarea
                  value={agent.personality}
                  onChange={e =>
                    updateCurrentAgent({ personality: e.target.value })
                  }
                  rows={7}
                  placeholder="How should I act? Whatʼs my purpose? How would you describe my personality?"
                />
              </label>
            </div>
          </form>
        </div>

        <div>
          <div>
            <ul className="colorPicker">
              {AGENT_COLORS.map((color, i) => (
                <li
                  key={i}
                  className={c({ active: color === agent.bodyColor })}
                >
                  <button
                    style={{ backgroundColor: color }}
                    onClick={() => updateCurrentAgent({ bodyColor: color })}
                  />
                </li>
              ))}
            </ul>
          </div>
          <div className="voicePicker">
            Voice
            <select
              value={agent.voice}
              onChange={e => {
                updateCurrentAgent({
                  voice: e.target.value as INTERLOCUTOR_VOICE,
                });
              }}
            >
              {INTERLOCUTOR_VOICES.map(voice => (
                <option key={voice} value={voice}>
                  {voice}
                </option>
              ))}
            </select>
          </div>
        </div>
        <button onClick={() => onClose()} className="button primary">
          Let’s go!
        </button>
      </div>
    </Modal>
  );
}
