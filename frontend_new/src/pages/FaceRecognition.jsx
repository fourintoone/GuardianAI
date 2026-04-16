import React, { useState } from 'react';
import { Card, Button, FileInput, Badge, Alert, Spinner } from '../components/ui/index.jsx';
import { useApi, useFileUpload } from '../hooks';
import { analyzeFace } from '../api/endpoints';

export const FaceRecognition = () => {
  const inputFile = useFileUpload();
  const frameFile = useFileUpload();
  const { data, loading, error, execute } = useApi(analyzeFace);
  const [alert, setAlert] = useState(null);

  const handleAnalyze = async () => {
    if (!inputFile.file || !frameFile.file) {
      setAlert({ type: 'error', message: 'Please upload both reference image and frame' });
      return;
    }
    try {
      await execute(inputFile.file, frameFile.file);
      setAlert({ type: 'success', message: 'Face recognition completed successfully!' });
    } catch (err) {
      setAlert({ type: 'error', message: error || 'Analysis failed' });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-[#F7F7FF] to-[#ECFFFC]">
      <div className="max-w-6xl mx-auto px-6 py-12">
        <h1 className="text-4xl font-bold font-Syne mb-2">Face Recognition</h1>
        <p className="text-slate-600 font-DM_Sans mb-8">
          Verify if a person in an image/video matches a reference face using ArcFace or DeepFace AI.
        </p>

        {alert && <Alert {...alert} onClose={() => setAlert(null)} />}

        <div className="grid md:grid-cols-2 gap-8">
          {/* Upload Section */}
          <Card>
            <h2 className="text-2xl font-bold font-Syne mb-6 text-[#43E8D8]">Upload Files</h2>

            <div className="space-y-6">
              <div>
                <FileInput
                  label="Reference Image"
                  accept="image/*"
                  onChange={inputFile.handleFileChange}
                  error={!inputFile.file && loading ? 'Required' : ''}
                />
                {inputFile.preview && (
                  <img src={inputFile.preview} alt="Reference" className="w-full h-48 object-contain bg-slate-100 rounded-lg mt-3" />
                )}
              </div>

              <div>
                <FileInput
                  label="Frame (Image or Video)"
                  accept="image/*,video/*"
                  onChange={frameFile.handleFileChange}
                  error={!frameFile.file && loading ? 'Required' : ''}
                />
                {frameFile.preview && frameFile.file.type.startsWith('image') && (
                  <img src={frameFile.preview} alt="Frame" className="w-full h-48 object-contain bg-slate-100 rounded-lg mt-3" />
                )}
              </div>

              <Button
                onClick={handleAnalyze}
                loading={loading}
                className="w-full"
                disabled={loading || !inputFile.file || !frameFile.file}
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

            {data?.success && (
              <div className="space-y-4">
                <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                  <Badge variant={data.data.verified ? 'success' : 'error'}>
                    {data.data.verified ? '✓ Match Found' : '✗ No Match'}
                  </Badge>
                  <p className="text-slate-700 font-DM_Sans mt-2">
                    Confidence: <span className="text-[#43E8D8] font-bold">{(data.data.distance || 0).toFixed(4)}</span>
                  </p>
                  <p className="text-slate-700 font-DM_Sans">
                    Threshold: <span className="text-slate-900">{data.data.threshold || 0}</span>
                  </p>
                  <p className="text-slate-700 font-DM_Sans">
                    Model: <span className="text-[#6C63FF]">{data.data.model}</span>
                  </p>
                </div>

                {data.data.frame && (
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <p className="text-slate-600 font-DM_Sans">Marked Frame:</p>
                      <a
                        href={`/uploads/${data.data.frame.split('/').pop()}`}
                        download={`guardian_ai_face_result.jpg`}
                        className="text-xs font-bold text-[#6C63FF] hover:text-[#43E8D8] transition-colors uppercase tracking-wider"
                      >
                        ↓ Download
                      </a>
                    </div>
                    <img
                      src={`/uploads/${data.data.frame.split('/').pop()}`}
                      alt="Result"
                      className="w-full h-60 object-contain bg-slate-100 rounded-lg border border-slate-200"
                    />
                  </div>
                )}

                {data.data.second !== undefined && (
                  <p className="text-slate-600 font-DM_Sans">
                    Frame Time: <span className="text-[#43E8D8]">{data.data.second}s</span>
                  </p>
                )}
              </div>
            )}

            {!loading && !data && (
              <div className="text-center py-8">
                <p className="text-slate-500 font-DM_Sans">Upload files and click Analyze to see results</p>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
};
