import { useState, useEffect, useCallback } from 'react';
import { Lesson } from './types';
import { lessonsMeta } from './lessons';
import Sidebar from './components/Sidebar';
import LessonView from './components/LessonView';

function App() {
  const [currentLesson, setCurrentLesson] = useState(1);
  const [lessons, setLessons] = useState<Lesson[]>(lessonsMeta as Lesson[]);
  const [lessonContent, setLessonContent] = useState<string>('');
  const [completedLessons, setCompletedLessons] = useState<Set<number>>(() => {
    const saved = localStorage.getItem('a2a-dojo-progress');
    return saved ? new Set(JSON.parse(saved)) : new Set();
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch('/api/lessons')
      .then(r => r.json())
      .then(data => {
        if (Array.isArray(data) && data.length > 0) setLessons(data);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    fetch(`/api/lessons/${currentLesson}`)
      .then(r => r.json())
      .then(data => {
        setLessonContent(data.content || '');
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [currentLesson]);

  const handleComplete = useCallback((id: number) => {
    setCompletedLessons(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      localStorage.setItem('a2a-dojo-progress', JSON.stringify([...next]));
      return next;
    });
  }, []);

  const currentLessonData = lessons.find(l => l.id === currentLesson);

  return (
    <div className="app">
      <Sidebar
        lessons={lessons}
        currentLesson={currentLesson}
        completedLessons={completedLessons}
        onSelectLesson={setCurrentLesson}
      />
      <main className="main-content">
        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner" />
            <p>Loading lesson...</p>
          </div>
        ) : currentLessonData ? (
          <LessonView
            lesson={{ ...currentLessonData, content: lessonContent }}
            isCompleted={completedLessons.has(currentLesson)}
            onComplete={() => handleComplete(currentLesson)}
          />
        ) : (
          <p>Select a lesson to begin.</p>
        )}
      </main>
    </div>
  );
}

export default App;
