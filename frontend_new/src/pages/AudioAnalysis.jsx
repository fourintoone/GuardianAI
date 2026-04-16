import React, { useState } from 'react';
import { Card, Button, FileInput, Badge, Alert, Spinner } from '../components/ui/index.jsx';
import { useApi, useFileUpload } from '../hooks';
import { analyzeAudio } from '../api/endpoints';

export const AudioAnalysis = () => {
  const audioFile = useFileUpload();
  const { data, loading, error, execute } = useApi(analyzeAudio);
  const [alert, setAlert] = useState(null);

  const handleAnalyze = async () => {
    if (!audioFile.file) {
      setAlert({ type: 'error', message: 'Please upload an audio file' });
      return;
    }
    try {
      await execute(audioFile.file);
      setAlert({ type: 'success', message: 'Audio analysis completed!' });
    } catch (err) {
      setAlert({ type: 'error', message: error || 'Analysis failed' });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-[#F7F7FF] to-[#ECFFFC]">
      <div className="max-w-6xl mx-auto px-6 py-12">
        <h1 className="text-4xl font-bold font-Syne mb-2">Audio Analysis</h1>
        <p className="text-slate-600 font-DM_Sans mb-8">
          Detect panic signals and distress sounds in audio files using advanced acoustic analysis.
        </p>

        {alert && <Alert {...alert} onClose={() => setAlert(null)} />}

        <div className="grid md:grid-cols-2 gap-8">
          {/* Upload Section */}
          <Card>
            <h2 className="text-2xl font-bold font-Syne mb-6 text-[#43E8D8]">Upload Audio</h2>

            <div className="space-y-6">
              <div>
                <FileInput
                  label="Audio File (MP3, WAV, MPEG, etc.)"
                  accept="audio/*, video/mpeg, .mpeg, .mpg"
                  onChange={audioFile.handleFileChange}
                  error={!audioFile.file && loading ? 'Required' : ''}
                />
                {audioFile.file && (
                  <div className="mt-3 p-3 bg-slate-50 border border-slate-200 rounded-lg">
                    <p className="text-slate-700 font-DM_Sans text-sm">
                      {audioFile.file.name}
                    </p>
                    <p className="text-slate-500 font-DM_Sans text-xs">
                      {(audioFile.file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                )}
              </div>

              <Button
                onClick={handleAnalyze}
                loading={loading}
                className="w-full"
                disabled={loading || !audioFile.file}
              >
                {loading ? 'Analyzing...' : 'Analyze'}
              </Button>
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
                <div className="bg-[#F0F7FF] p-6 rounded-xl border border-[#D6E8FD]">
                  <h3 className="text-xl font-bold font-Syne text-[#1A2B4C] text-center mb-4">
                    Audio Panic Detection
                  </h3>
                  
                  <div className="bg-[#E2E8F0]/70 py-2 px-3 rounded-md text-sm font-DM_Sans text-[#3B82F6] mb-6 font-medium">
                    {data.data.filename || "Uploaded Audio File"}
                  </div>

                  <div className="space-y-4 text-sm font-DM_Sans text-slate-800">
                    <div className="flex items-center gap-2">
                      <span className="font-bold">Status:</span>
                      <span className={`font-bold ${data.data.status === 'PANIC' ? 'text-[#EF4444]' : 'text-[#10B981]'}`}>
                        {data.data.status}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="font-bold">Volume Level:</span>
                      <span>{data.data.volume}/1000</span>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="font-bold">Volume Category:</span>
                      <span>{data.data.volume_category}</span>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="font-bold">Raw Energy:</span>
                      <span>{data.data.raw_energy}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {!loading && !data && (
              <div className="text-center py-8">
                <p className="text-slate-500 font-DM_Sans">Upload an audio file and click Analyze to see results</p>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
};
