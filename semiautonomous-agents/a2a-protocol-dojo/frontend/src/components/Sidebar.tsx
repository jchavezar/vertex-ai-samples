import { CheckCircle } from 'lucide-react';
import { Lesson } from '../types';

interface Props {
  lessons: Lesson[];
  currentLesson: number;
  completedLessons: Set<number>;
  onSelectLesson: (id: number) => void;
}

export default function Sidebar({ lessons, currentLesson, completedLessons, onSelectLesson }: Props) {
  const total = lessons.length;
  const done = completedLessons.size;

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">A2A Protocol Dojo</div>
        <div className="sidebar-subtitle">道場 &middot; INTERACTIVE TUTORIAL</div>
      </div>
      <nav className="sidebar-nav">
        {lessons.map(lesson => {
          const isActive = lesson.id === currentLesson;
          const isCompleted = completedLessons.has(lesson.id);
          return (
            <div
              key={lesson.id}
              className={`lesson-item${isActive ? ' active' : ''}${isCompleted ? ' completed' : ''}`}
              onClick={() => onSelectLesson(lesson.id)}
            >
              <div className="lesson-number">{isCompleted ? '✓' : lesson.id}</div>
              <div className="lesson-info">
                <div className="lesson-title">{lesson.title}</div>
                <div className="lesson-desc">{lesson.description}</div>
              </div>
              {isCompleted && <CheckCircle size={16} className="lesson-check" />}
            </div>
          );
        })}
      </nav>
      <div className="progress-section">
        <div className="progress-label">{done}/{total} lessons completed</div>
        <div className="progress-bar-bg">
          <div className="progress-bar-fill" style={{ width: `${total ? (done / total) * 100 : 0}%` }} />
        </div>
      </div>
    </aside>
  );
}
