# GuardianAI - Full Project Overview

## 1. Project Concept & Mission
**GuardianAI** is an advanced, multi-modal artificial intelligence system designed for comprehensive security, surveillance, and situational awareness. It acts as an intelligent safety net that goes beyond traditional video monitoring by incorporating multiple streams of AI analysis (Face, Object, Emotion, and Audio) in real-time. 

The core philosophy of GuardianAI is to proactively identify diverse threats and events—ranging from unauthorized access to emotional distress and panic—using automated, high-accuracy AI models. The system uses a modern web-based dashboard and a backend that seamlessly processes both static files (images/audio/video) and live camera feeds (IP/webcams).

---

## 2. Technology Stack

### Frontend (User Interface)
The frontend is built for a sleek, premium, "SaaS dashboard" experience, prioritizing responsiveness and dynamic user interactions.
* **Core Framework:** React (using Create React App)
* **Routing:** React Router (HashRouter) for single-page application navigation.
* **Styling:** Tailwind CSS combined with custom CSS libraries (`index.css`), leveraging premium gradients, glassmorphism (translucent backgrounds with blur), and hover micro-animations.
* **HTTP Client:** Axios for robust API interaction with the Flask backend.

### Backend (API & Processing Engine)
The backend acts as the central intelligence hub, ingesting media and feeding it through various machine learning pipelines.
* **Core Framework:** Python Flask
* **API Structure:** RESTful architecture with CORS enabled for cross-origin requests from the React frontend.
* **Image/Video Processing:** OpenCV (`cv2`) for video frame extraction, rendering bounding boxes, and image enhancements.
* **Audio Processing:** Librosa & NumPy for audio loading, sample rate conversion, and energy calculation.

### AI Models & Machine Learning (The Core Intelligence)
* **Face Recognition:** 
  * **Primary System:** ArcFace via InsightFace (Buffalo_L model) - Preferred for high speed (4x faster) and high accuracy (99.8%).
  * **Fallback System:** DeepFace using the Facenet512 model.
* **Object Detection:** 
  * **System:** YOLOv8s (Ultralytics) - Upgraded from YOLOv5 for improved accuracy. Tuned to a 0.2 confidence threshold for high sensitivity.
* **Emotion Analysis:**
  * **System:** DeepFace emotion detection module. Capable of analyzing both static images and video tracks (sampling at 0.5s intervals).
* **Audio Panic Detection:**
  * **System:** Custom energy-based heuristic detection using `librosa`. Analyzes raw audio energy in chunks to classify environment audio from "Complete silence" to "Screaming/Panic sounds".

---

## 3. Core Modules and Working Models

### A. Intelligent Face Recognition Module
**Purpose:** Authenticate and track individuals through video feeds or static images.
**Working Logic:**
1. **Input:** The system accepts a reference image and a target (image, video, or live IP camera stream).
2. **Auto-Enhancement:** Before processing, the system's `image_processing.py` script automatically evaluates the image for blur, contrast, and brightness. It applies dynamic Unsharp Masking, CLAHE (Contrast Limited Adaptive Histogram Equalization), or Gamma Correction to ensure the face embeddings are accurate.
3. **Detection & Embedding:** The InsightFace (ArcFace) detector locates faces in the source and target. It calculates facial embeddings (high-dimensional vectors representing facial features).
4. **Verification:** The module calculates the distance between the reference face vector and the target frame vectors. If the distance falls below the configured threshold (1.2 for ArcFace), a match is confirmed.
5. **Output:** The backend returns the match status, confidence metrics, and a frame with bounded boxes drawn around the recognized face.

### B. Proactive Object Detection Module
**Purpose:** Identify objects of interest (e.g., unattended bags, weapons, mobile phones) in a feed based on a reference image.
**Working Logic:**
1. **Input:** Reference image of the object type and a target video/image/stream.
2. **Reference Analysis:** YOLOv8 analyzes the reference image to determine the "target class" (e.g., "backpack", "suitcase").
3. **Target Scanning:** The target media is scanned. If it's a video, frames are extracted at 0.5s intervals to optimize performance.
4. **Detection:** YOLOv8 scans each frame. If it detects the "target class" with a confidence > 0.2, it flags the detection.
5. **Output:** Returns a list of detections with bounding box coordinates, class labels, and the highest-confidence visual frame.

### C. Emotion & Behavioral Analysis Module
**Purpose:** Assess the emotional state of individuals to detect potential distress, anger, or fear.
**Working Logic:**
1. **Input:** Video or image file.
2. **Sampling:** For videos, the system iterates over the feed, extracting frames at 0.5-second intervals.
3. **Deep Analysis:** The DeepFace engine evaluates the facial landmarks to classify the dominant emotion (e.g., fear, angry, happy, sad, neutral, surprise, disgust).
4. **Confidence Scoring:** It calculates a confidence percentage based on the weight of the dominant emotion versus the sum of all detected emotional vectors.
5. **Output:** Returns the dominant emotion and a granular breakdown of all emotional weights detected in the frame.

### D. Audio Panic & Threat Detection Module
**Purpose:** Detect anomalous audio events such as screaming, shouting, or loud disturbances in an environment.
**Working Logic:**
1. **Input:** Audio file (wav, mp3, ogg, etc.).
2. **Signal processing:** Librosa loads the file into a mono waveform array.
3. **Energy Calculation:** The system computes the raw energy (mean absolute amplitude) of the audio signal.
4. **Scaling & Classification:** The raw energy is clamped and scaled to a 1-1000 range.
    * 1-50: Normal conversational levels.
    * 51-60: Loud talking.
    * >60: Threshold crossed. Categorized as "PANIC" (Shouting, Screaming, Intense Sounds).
5. **Output:** Returns the volume category and safety status (NORMAL vs. PANIC).

---

## 4. Architectural Data Flow & Real-Time Logistics

1. **Client Interaction:** 
   The React frontend initiates an action (e.g., submitting a reference image and an IP camera URL for live face tracking).
2. **API Payload:** 
   Axios packages this into a `multipart/form-data` request and sends it to the Flask backend on port 8001.
3. **File Handling:** 
   Flask uses `werkzeug` to securely save inputs into a local `uploads/` directory with unique timestamps and UUIDs to prevent collisions.
4. **Processing Pipeline:**
   * If working with video, `cv2.VideoCapture` breaks the video down into discrete frames based on configured temporal sampling (e.g., every 0.2s or 0.5s).
   * Contextual pre-processing (like auto-enhancement for low-light frames) executes.
   * AI Models process the frames in memory. For speed and efficiency, loops break the moment a high-confidence match is found in tasks like authentication.
5. **Response Delivery:** 
   Bounding boxes are drawn on successful frames (`_marked.jpg`), and JSON payloads containing success booleans, metadata, and relative links to the marked images are sent back to the frontend.
6. **UI Update:** 
   The React application interprets the JSON, updates its state, and renders the premium dashboard visualizations, presenting the analyzed frame and threat metrics to the operator.
