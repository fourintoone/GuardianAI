# GuardianAI Frontend

Advanced React/Vite frontend for GuardianAI - AI-powered analysis platform with face recognition, object detection, emotion analysis, and real-time live detection.

## ✨ Features

- **👤 Face Recognition** - Verify faces using ArcFace/DeepFace AI
- **📦 Object Detection** - Locate objects using YOLOv8
- **😊 Emotion Detection** - Analyze facial emotions
- **🎙️ Audio Analysis** - Detect panic/distress sounds
- **📹 Live Detection** - Real-time IP camera analysis
- **🎨 Modern UI** - Vibrant, professional dark-theme design
- **⚡ Fast & Responsive** - Optimized React + Vite setup
- **🔐 Secure** - JWT interceptor, secure API communication

## 🚀 Quick Start

### Prerequisites
- Node.js >= 16.x
- npm or yarn
- Backend running on `http://localhost:8001`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The frontend will run on `http://localhost:3000` and automatically proxy API calls to the backend at `http://localhost:8001`.

## 📁 Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   ├── client.js           # Axios instance with JWT interceptor
│   │   └── endpoints.js        # API functions for all features
│   ├── components/
│   │   ├── ui/                 # Reusable UI components
│   │   │   └── index.js        # Button, Card, Input, FileInput, Badge, etc.
│   │   └── layout/
│   │       └── index.js        # Navbar, Sidebar, Footer
│   ├── pages/
│   │   ├── Home.jsx            # Landing page
│   │   ├── FaceRecognition.jsx  # Face analysis page
│   │   ├── ObjectDetection.jsx  # Object detection page
│   │   ├── EmotionDetection.jsx # Emotion analysis page
│   │   ├── AudioAnalysis.jsx    # Audio analysis page
│   │   └── LiveDetection.jsx    # Live camera detection page
│   ├── hooks/
│   │   └── index.js            # useApi, useFileUpload, useLocalStorage
│   ├── App.jsx                 # Main app with routing
│   ├── main.jsx                # Entry point
│   └── index.css               # Global styles + Tailwind
├── index.html
├── vite.config.js              # Vite config with API proxy
├── tailwind.config.js          # Tailwind CSS config
├── postcss.config.js           # PostCSS config
└── package.json
```

## 🎨 Design System

### Colors
- **Dark Background**: `#0F0F1A`
- **Primary (Violet)**: `#6C63FF`
- **Accent (Pink)**: `#FF6584`
- **Highlight (Teal)**: `#43E8D8`

### Typography
- **Headings**: Syne (400-800 weight)
- **Body**: DM Sans (400-700 weight)

### Components
- **Button** - Primary, secondary, tertiary, outline variants
- **Card** - Gradient background with hover effects
- **Input** - Text input with validation
- **FileInput** - Drag-and-drop file upload
- **Badge** - Success, error, warning, info variants
- **Spinner** - Loading indicator
- **Alert** - Notification component

## 🔧 API Integration

All API calls go through `src/api/client.js` with automatic JWT handling:

```javascript
import { analyzeFace, analyzeEmotion, analyzeAudio } from '@/api/endpoints';

// Use in components
const { data, loading, error, execute } = useApi(analyzeFace);
await execute(inputImage, frameFile);
```

### Backend Endpoints
- `POST /analyze/face` - Face recognition
- `POST /analyze/object` - Object detection
- `POST /analyze/emotion` - Emotion analysis
- `POST /analyze/audio` - Audio analysis
- `POST /analyze/live_face` - IP camera face detection
- `POST /analyze/face_live` - Multi-frame face detection
- `POST /analyze/live_object` - IP camera object detection
- `GET /health` - Health check
- `GET /test/emotion` - Test emotion module

## 📦 Building for Production

```bash
npm run build
```

Creates optimized production build in `dist/` directory.

To deploy:
- Copy `dist/` contents to your web server
- Ensure API proxy is configured for production
- Update CORS settings if needed

## 🔐 Security

- JWT tokens stored in localStorage with httpOnly fallback
- Automatic token injection in request headers
- Secure file uploads with type validation
- CORS enabled for frontend origin only

## 🐛 Debugging

Enable development mode:
```bash
npm run dev
```

Check browser DevTools Console for API errors and logs.

## 📝 Environment Variables

Create `.env.local`:
```
VITE_API_URL=http://localhost:8001
VITE_UPLOAD_SIZE_MB=100
```

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/amazing-feature`
2. Commit changes: `git commit -m 'Add amazing feature'`
3. Push to branch: `git push origin feature/amazing-feature`
4. Open Pull Request

## 📄 License

MIT License - See LICENSE file

## 🆘 Support

For issues or questions:
1. Check the [Wiki](https://github.com/), or
2. Open an issue in the repository

---

**Built with ❤️ using React + Vite + Tailwind CSS**
