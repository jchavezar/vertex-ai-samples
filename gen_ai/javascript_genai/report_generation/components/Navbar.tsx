
import React from 'react';
import { DowJonesLogo } from './DowJonesLogo';

export const Navbar: React.FC = () => {
  return (
    <nav className="bg-dj-nav-bg shadow-md w-full fixed top-0 left-0 z-50">
      <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
        {/* Left item */}
        <div className="flex items-center">
          <DowJonesLogo />
        </div>
        {/* Right item */}
        <div className="flex items-center">
          <span className="text-2xl text-dj-text-primary font-normal tracking-normal">
            Gemini
          </span>
        </div>
      </div>
    </nav>
  );
};
