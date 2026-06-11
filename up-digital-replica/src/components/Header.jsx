import React, { useState, useEffect } from 'react';
import { Menu, X, ChevronDown } from './Icons';

export const Header = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 20) {
        setScrolled(true);
      } else {
        setScrolled(false);
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? 'bg-brand-dark/80 backdrop-blur-md border-b border-white/5 h-16' : 'bg-transparent h-20'} flex items-center`}>
      <nav className="max-w-7xl mx-auto px-6 w-full flex items-center justify-between">
        {/* Logo */}
        <div className="relative group">
          <a href="/" className="flex items-center gap-2 cursor-pointer font-black text-xl tracking-wider text-brand-lime">
            UP DIGITAL.
          </a>
        </div>

        {/* Desktop Nav */}
        <div className="hidden md:flex items-center gap-1">
          <div className="relative group">
            <button className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 text-white/70 hover:text-white">
              Case Studies
              <ChevronDown className="w-4 h-4 transition-transform duration-200 group-hover:rotate-180" />
            </button>
            {/* Dropdown Menu */}
            <div className="absolute top-full left-0 mt-2 w-48 rounded-xl bg-brand-dark-alt border border-white/5 p-2 shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
              <a href="/work/pongbot" className="block px-4 py-2 text-sm text-white/70 hover:text-white hover:bg-white/5 rounded-lg">Pongbot</a>
              <a href="/work/slavista" className="block px-4 py-2 text-sm text-white/70 hover:text-white hover:bg-white/5 rounded-lg">Slavista</a>
              <a href="/work/non-profits" className="block px-4 py-2 text-sm text-white/70 hover:text-white hover:bg-white/5 rounded-lg">Non-Profits</a>
            </div>
          </div>
          <a href="#solutions" className="px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 text-white/70 hover:text-white">Solutions</a>
          <a href="#press" className="px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 text-white/70 hover:text-white">Press</a>
          <a href="#team" className="px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 text-white/70 hover:text-white">Team</a>
          <a href="#ai-employees" className="px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 text-white/70 hover:text-white">AI Employees</a>
          <a href="#contact" className="px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 text-white/70 hover:text-white">Contact</a>
        </div>

        {/* CTA Button */}
        <div className="hidden md:flex items-center">
          <a href="#onboarding" className="px-5 py-2 rounded-lg bg-brand-lime text-brand-dark-alt text-sm font-bold hover:bg-brand-lime-hover transition-colors shadow-lg shadow-brand-lime/10">
            Start Your Project
          </a>
        </div>

        {/* Mobile menu button */}
        <button 
          onClick={() => setIsOpen(!isOpen)}
          className="md:hidden relative z-50 text-white p-2"
          aria-label="Toggle menu"
        >
          {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </nav>

      {/* Mobile Menu Overlay */}
      <div className={`fixed inset-0 bg-brand-dark/95 z-45 md:hidden flex flex-col justify-center items-center gap-6 transition-all duration-300 ${isOpen ? 'opacity-100 visible' : 'opacity-0 invisible'}`}>
        <a href="#solutions" onClick={() => setIsOpen(false)} className="text-xl text-white/80 hover:text-white">Solutions</a>
        <a href="#press" onClick={() => setIsOpen(false)} className="text-xl text-white/80 hover:text-white">Press</a>
        <a href="#team" onClick={() => setIsOpen(false)} className="text-xl text-white/80 hover:text-white">Team</a>
        <a href="#ai-employees" onClick={() => setIsOpen(false)} className="text-xl text-white/80 hover:text-white">AI Employees</a>
        <a href="#contact" onClick={() => setIsOpen(false)} className="text-xl text-white/80 hover:text-white">Contact</a>
        <a href="#onboarding" onClick={() => setIsOpen(false)} className="mt-4 px-6 py-3 rounded-lg bg-brand-lime text-brand-dark-alt text-lg font-bold hover:bg-brand-lime-hover transition-colors">
          Start Your Project
        </a>
      </div>
    </header>
  );
};

export default Header;
