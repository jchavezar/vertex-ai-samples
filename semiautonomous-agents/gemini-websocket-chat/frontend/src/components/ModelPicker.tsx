import { useChatStore } from '../stores/chatStore';
import type { ModelKey } from '../types';

const MODELS: { key: ModelKey; label: string }[] = [
  { key: '2.5-flash', label: '[2.5-flash]' },
  { key: '2.5-pro', label: '[2.5-pro]' },
];

function ModelPicker() {
  const model = useChatStore((s) => s.model);
  const setModel = useChatStore((s) => s.setModel);

  return (
    <div className="model-picker">
      {MODELS.map((m) => (
        <button
          key={m.key}
          className={`model-tab ${model === m.key ? 'active' : ''}`}
          onClick={() => setModel(m.key)}
        >
          {m.label}
        </button>
      ))}
    </div>
  );
}

export default ModelPicker;
