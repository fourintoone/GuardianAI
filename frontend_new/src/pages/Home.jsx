import React from 'react';
import { Link } from 'react-router-dom';
import { Card, Button } from '../components/ui/index.jsx';

export const Home = () => {
  const features = [
    {
      path: '/face',
      title: 'Face Recognition',
      description: 'Verify if a person matches a reference image. Supports images and videos.',
      accentFrom: '#6C63FF',
      accentTo: '#5845D4',
    },
    {
      path: '/object',
      title: 'Object Detection',
      description: 'Detect and locate objects in images or videos using YOLOv8.',
      accentFrom: '#FF6584',
      accentTo: '#E84B6B',
    },
    {
      path: '/emotion',
      title: 'Emotion Detection',
      description: 'Analyze emotions from faces in images or videos.',
      accentFrom: '#43E8D8',
      accentTo: '#2FD4C4',
    },
    {
      path: '/audio',
      title: 'Audio Analysis',
      description: 'Detect panic and distress signals in audio files.',
      accentFrom: '#6C63FF',
      accentTo: '#43E8D8',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-[#F7F7FF] to-[#ECFFFC]">
      <div className="max-w-7xl mx-auto px-6 py-14 md:py-16">
        <div className="text-center mb-10 md:mb-12 bg-white border border-[#6C63FF]/15 rounded-2xl p-8 md:p-10 shadow-lg">
          <h1 className="text-4xl md:text-6xl font-bold font-Syne mb-4 bg-gradient-to-r from-[#6C63FF] via-[#43E8D8] to-[#FF6584] bg-clip-text text-transparent">
            GuardianAI
          </h1>
          <p className="text-lg md:text-xl text-slate-700 font-DM_Sans max-w-2xl mx-auto">
            AN UNIFIED AI SAFETY AND RECOVERY SYSTEM FOR MASS GATHERINGS
          </p>
        </div>

        <div className="mb-6">
          <h2 className="text-2xl md:text-3xl font-bold font-Syne text-slate-900 mb-2">Modules</h2>
          <p className="text-slate-600 font-DM_Sans">Choose a module to start analysis.</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {features.map((feature) => (
            <Link key={feature.path} to={feature.path}>
              <Card className="h-full cursor-pointer bg-white border border-slate-200 shadow-md hover:shadow-xl hover:-translate-y-1 transition-all">
                <div
                  className="h-1.5 rounded-full mb-5"
                  style={{
                    background: `linear-gradient(90deg, ${feature.accentFrom} 0%, ${feature.accentTo} 100%)`,
                  }}
                />
                <h3 className="text-2xl font-bold font-Syne mb-3 text-slate-900">
                  {feature.title}
                </h3>
                <p className="text-slate-600 font-DM_Sans mb-6 text-sm leading-relaxed min-h-[44px]">
                  {feature.description}
                </p>
                <Button variant="primary" size="sm" className="w-full">
                  Open Module
                </Button>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};
