import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Navbar, Footer } from './components/layout/index.jsx';
import { Home } from './pages/Home';
import { FaceRecognition } from './pages/FaceRecognition';
import { ObjectDetection } from './pages/ObjectDetection';
import { EmotionDetection } from './pages/EmotionDetection';
import { AudioAnalysis } from './pages/AudioAnalysis';

export default function App() {
  return (
    <Router>
      <div className="flex flex-col min-h-screen">
        <Navbar />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/face" element={<FaceRecognition />} />
            <Route path="/object" element={<ObjectDetection />} />
            <Route path="/emotion" element={<EmotionDetection />} />
            <Route path="/audio" element={<AudioAnalysis />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}
