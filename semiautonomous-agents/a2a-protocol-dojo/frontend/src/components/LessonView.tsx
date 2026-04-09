import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { CheckCircle, Circle, Play } from 'lucide-react';
import { Lesson } from '../types';
import CodeBlock from './CodeBlock';
import AgentCardViewer from './AgentCardViewer';
import TaskLifecycle from './TaskLifecycle';
import MessageBuilder from './MessageBuilder';
import StreamViewer from './StreamViewer';
import SkillsBrowser from './SkillsBrowser';
import OrchestrationFlow from './OrchestrationFlow';

interface Props {
  lesson: Lesson;
  isCompleted: boolean;
  onComplete: () => void;
}

const DEMO_COMPONENTS: Record<string, React.FC> = {
  AgentCardViewer,
  TaskLifecycle,
  MessageBuilder,
  StreamViewer,
  SkillsBrowser,
  OrchestrationFlow,
};

export default function LessonView({ lesson, isCompleted, onComplete }: Props) {
  const DemoComponent = lesson.demoComponent ? DEMO_COMPONENTS[lesson.demoComponent] : null;

  return (
    <div className="lesson-view">
      <div className="lesson-header">
        <span className="lesson-header-number">Lesson {lesson.id}</span>
        <h1 className="lesson-header-title">{lesson.title}</h1>
      </div>

      <div className="lesson-content">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            code({ className, children, ...props }) {
              const match = /language-(\w+)/.exec(className || '');
              const code = String(children).replace(/\n$/, '');
              if (match) {
                return <CodeBlock code={code} language={match[1]} />;
              }
              return <code className={className} {...props}>{children}</code>;
            },
          }}
        >
          {lesson.content || ''}
        </ReactMarkdown>
      </div>

      {DemoComponent && (
        <div className="demo-panel">
          <div className="demo-panel-header">
            <Play size={16} /> Interactive Demo
          </div>
          <div className="demo-panel-body">
            <DemoComponent />
          </div>
        </div>
      )}

      <div className="lesson-footer">
        <button
          className={`complete-btn${isCompleted ? ' is-completed' : ''}`}
          onClick={onComplete}
        >
          {isCompleted ? <CheckCircle size={18} /> : <Circle size={18} />}
          {isCompleted ? 'Completed' : 'Mark as Complete'}
        </button>
      </div>
    </div>
  );
}
