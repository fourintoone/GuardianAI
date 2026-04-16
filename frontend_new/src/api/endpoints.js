import client from './client';

// Face Recognition
export const analyzeFace = async (inputImage, frameFile) => {
  const formData = new FormData();
  formData.append('input', inputImage);
  formData.append('frame', frameFile);
  return client.post('/analyze/face', formData);
};

// Object Detection
export const analyzeObject = async (inputImage, frameFile) => {
  const formData = new FormData();
  formData.append('input', inputImage);
  formData.append('frame', frameFile);
  return client.post('/analyze/object', formData);
};

// Emotion Detection
export const analyzeEmotion = async (frameFile) => {
  const formData = new FormData();
  formData.append('frame', frameFile);
  return client.post('/analyze/emotion', formData);
};

// Audio Panic Detection
export const analyzeAudio = async (audioFile) => {
  const formData = new FormData();
  formData.append('audio', audioFile);
  return client.post('/analyze/audio', formData);
};

// Health Check
export const checkHealth = () => client.get('/health');

// Test Emotion Detection
export const testEmotion = () => client.get('/test/emotion');
