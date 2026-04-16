import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

export const Navbar = () => {
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false);

  const isActive = (path) => location.pathname === path ? 'text-[#6C63FF]' : 'text-slate-700 hover:text-[#6C63FF]';

  return (
    <nav className="bg-white/90 backdrop-blur border-b border-slate-200 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
        <Link to="/" className="flex items-center gap-3">
          <img src="/f1o-logo.png" alt="F1O Logo" className="h-12 w-auto" />
          <span className="text-2xl font-extrabold font-Syne text-[#0F1B4C]">GuardianAI</span>
        </Link>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="md:hidden text-[#6C63FF] text-2xl hover:text-[#FF6584]"
        >
          {isOpen ? '✕' : '☰'}
        </button>

        {/* Desktop Menu */}
        <div className="hidden md:flex gap-8 items-center font-DM_Sans">
          <Link to="/" className={`transition-colors ${isActive('/')}`}>Home</Link>
          <Link to="/face" className={`transition-colors ${isActive('/face')}`}>Face</Link>
          <Link to="/object" className={`transition-colors ${isActive('/object')}`}>Object</Link>
          <Link to="/emotion" className={`transition-colors ${isActive('/emotion')}`}>Emotion</Link>
          <Link to="/audio" className={`transition-colors ${isActive('/audio')}`}>Audio</Link>
        </div>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="md:hidden bg-white border-t border-slate-200 p-4 space-y-3 font-DM_Sans">
          <Link to="/" className="block text-slate-700 hover:text-[#6C63FF]">Home</Link>
          <Link to="/face" className="block text-slate-700 hover:text-[#6C63FF]">Face</Link>
          <Link to="/object" className="block text-slate-700 hover:text-[#6C63FF]">Object</Link>
          <Link to="/emotion" className="block text-slate-700 hover:text-[#6C63FF]">Emotion</Link>
          <Link to="/audio" className="block text-slate-700 hover:text-[#6C63FF]">Audio</Link>
        </div>
      )}
    </nav>
  );
};

export const Footer = () => (
  <footer className="bg-white border-t border-slate-200 py-8 mt-16">
    <div className="max-w-7xl mx-auto px-6 text-center text-slate-600 font-DM_Sans">
      <p>Guardian AI Developed by FOUR INTO ONE</p>
    </div>
  </footer>
);

export const Sidebar = ({ items }) => (
  <aside className="hidden lg:block w-64 bg-white border-r border-slate-200 p-6 sticky top-20 h-[calc(100vh-80px)] overflow-y-auto">
    <div className="space-y-3">
      {items.map((item) => (
        <Link
          key={item.path}
          to={item.path}
          className="block px-4 py-3 rounded-lg bg-slate-50 hover:bg-indigo-50 text-slate-700 hover:text-[#6C63FF] transition-all font-DM_Sans"
        >
          {item.icon} {item.label}
        </Link>
      ))}
    </div>
  </aside>
);
