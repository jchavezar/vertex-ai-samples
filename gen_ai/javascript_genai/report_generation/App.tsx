
import React from 'react';
import { HomeView } from './views/HomeView';
import { AlertProvider } from './contexts/AlertContext';
import { Navbar } from './components/Navbar'; // Restored Navbar

const App: React.FC = () => {
  return (
    <AlertProvider>
      <div className="flex flex-col min-h-screen">
        <Navbar /> 
        {/* HomeView will now be rendered within a layout that assumes Navbar height */}
        <main className="flex-grow pt-16"> {/* Add padding-top for fixed navbar */}
          <HomeView />
        </main>
      </div>
    </AlertProvider>
  );
};

export default App;