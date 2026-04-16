import React, { useState } from 'react';
import { Card, Button, FileInput, Badge, Alert, Spinner } from '../components/ui/index.jsx';
import { useApi, useFileUpload } from '../hooks';
import { analyzeEmotion, testEmotion } from '../api/endpoints';

export const EmotionDetection = () => {
  const frameFile = useFileUpload();
  const { data, loading, error, execute } = useApi(analyzeEmotion);
  const { execute: testEmotionExec, loading: testLoading } = useApi(testEmotion);
  const [alert, setAlert] = useState(null);

  const handleAnalyze = async () => {
    if (!frameFile.file) {
      setAlert({ type: 'error', message: 'Please upload an image or video' });
      return;
    }
    try {
      await execute(frameFile.file);
      setAlert({ type: 'success', message: 'Emotion analysis completed!' });
    } catch (err) {
      setAlert({ type: 'error', message: error || 'Analysis failed' });
    }
  };

  const handleTest = async () => {
    try {
      const result = await testEmotionExec();
      setAlert({ type: 'success', message: `Module test passed: ${result.emotion_detection}` });
    } catch (err) {
      setAlert({ type: 'error', message: 'Module test failed' });
    }
  };

  const emotionEmojis = {
    happy: '😊',
    sad: '😢',
    angry: '😠',
    fear: '😨',
    disgust: '🤢',
    surprise: '😲',
    neutral: '😐',
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-[#F7F7FF] to-[#ECFFFC]">
      <div className="max-w-6xl mx-auto px-6 py-12">
        <h1 className="text-4xl font-bold font-Syne mb-2">Emotion Detection</h1>
        <p className="text-slate-600 font-DM_Sans mb-8">
          Analyze facial emotions in images or videos using advanced DeepFace AI technology.
        </p>

        {alert && <Alert {...alert} onClose={() => setAlert(null)} />}

        <div className="grid md:grid-cols-2 gap-8">
          {/* Upload Section */}
          <Card>
            <h2 className="text-2xl font-bold font-Syne mb-6 text-[#43E8D8]">Upload File</h2>

            <div className="space-y-6">
              <div>
                <FileInput
                  label="Image or Video"
                  accept="image/*,video/*"
                  onChange={frameFile.handleFileChange}
                  error={!frameFile.file && loading ? 'Required' : ''}
                />
                {frameFile.preview && frameFile.file.type.startsWith('image') && (
                  <img src={frameFile.preview} alt="Frame" className="w-full h-48 object-contain bg-slate-100 rounded-lg mt-3" />
                )}
              </div>

              <div className="space-y-2">
                <Button
                  onClick={handleAnalyze}
                  loading={loading}
                  className="w-full"
                  disabled={loading || !frameFile.file}
                >
                    {loading ? 'Analyzing...' : 'Analyze'}
                </Button>

                <Button
                  onClick={handleTest}
                  variant="outline"
                  loading={testLoading}
                  className="w-full"
                  disabled={testLoading}
                >
                  {testLoading ? 'Testing...' : '✓ Test Module'}
                </Button>
              </div>
            </div>
          </Card>

          {/* Results Section */}
          <Card>
            <h2 className="text-2xl font-bold font-Syne mb-6 text-[#FF6584]">Results</h2>

            {loading && (
              <div className="flex justify-center py-12">
                <Spinner size="lg" />
              </div>
            )}

            {data?.data && (
              <div className="space-y-4">
                <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                  <p className="text-slate-700 font-DM_Sans mb-2">Dominant Emotion:</p>
                  <div className="text-5xl mb-2">
                    {emotionEmojis[data.data.dominant_emotion] || '😐'}
                  </div>
                  <p className="text-3xl font-bold text-[#43E8D8]">
                    {data.data.dominant_emotion?.toUpperCase()}
                  </p>
                  <p className="text-slate-700 font-DM_Sans mt-2">
                    Confidence: <span className="text-[#6C63FF] font-bold">{(data.data.confidence * 100).toFixed(1)}%</span>
                  </p>
                </div>

                {data.data.emotions && (
                  <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                    <p className="text-slate-700 font-DM_Sans mb-3">All Emotions:</p>
                    <div className="space-y-2">
                      {Object.entries(data.data.emotions).map(([emotion, score]) => (
                        <div key={emotion} className="flex items-center justify-between">
                          <span className="text-slate-600 font-DM_Sans capitalize">
                            {emotionEmojis[emotion]} {emotion}
                          </span>
                          <div className="w-32 h-2 bg-[#6C63FF]/20 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-[#6C63FF] to-[#43E8D8]"
                              style={{ width: `${score}%` }}
                            />
                          </div>
                          <span className="text-[#43E8D8] font-bold w-12 text-right">
                            {score.toFixed(0)}%
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {data.data.frame_second !== undefined && (
                  <p className="text-slate-600 font-DM_Sans">
                    Frame Time: <span className="text-[#43E8D8]">{data.data.frame_second}s</span>
                  </p>
                )}
              </div>
            )}

            {!loading && !data && (
              <div className="text-center py-8">
                <p className="text-slate-500 font-DM_Sans">Upload a file and click Analyze to see results</p>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
};
