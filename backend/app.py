
print("GuardianAI backend started from:", __file__)
# ---------------- INITIAL SETUP ----------------
import os
import cv2
import time
import uuid
import torch
import librosa
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from deepface import DeepFace
from face_recognition_arcface import initialize_arcface, get_face_recognizer
from image_processing import auto_enhance_image, save_processed_image

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"], 
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

# Serve images from uploads directory
from flask import send_from_directory

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- LIVE FACE RECOGNITION (IP CAMERA) ----------------
@app.route("/analyze/live_face", methods=["POST"])
def analyze_live_face():
    ipcam_url = request.form.get("url")
    input_img = request.files.get("input")
    if not ipcam_url or not input_img:
        return jsonify({"error": "Provide 'url' and 'input'"}), 400

    input_path = save_file(input_img)
    try:
        cap = cv2.VideoCapture(ipcam_url)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return jsonify({"error": "Could not read frame from IP camera"}), 500

        temp_frame_path = os.path.join(UPLOAD_FOLDER, f"live_{int(time.time())}.jpg")
        cv2.imwrite(temp_frame_path, frame)

        # Use ArcFace (InsightFace) for face verification - 4x faster, 99.8% accurate
        try:
            recognizer = get_face_recognizer()
            arc_result = recognizer.verify_faces(input_path, temp_frame_path, threshold=1.2)
            # Convert ArcFace result to DeepFace-compatible format for backwards compatibility
            result = {
                "verified": arc_result["verified"],
                "distance": arc_result["distance"],
                "threshold": 1.2,
                "model": "ArcFace (Buffalo_L)"
            }
        except Exception as e:
            # Fallback to DeepFace if ArcFace fails
            print(f"ArcFace verification failed: {e}, using DeepFace fallback")
            result = DeepFace.verify(
                img1_path=input_path,
                img2_path=temp_frame_path,
                model_name="Facenet512",
                enforce_detection=False,
                detector_backend="opencv"
            )
        marked_path = None
        if bool(result.get("verified")):
            try:
                image = cv2.imread(temp_frame_path)
                # Use robust ArcFace detector for marking boxes
                detected_faces = recognizer.app.get(image)
                for face in detected_faces:
                    bbox = [int(x) for x in face.bbox]
                    cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 3)
                    break
                
                marked_path = temp_frame_path.replace('.jpg', '_marked.jpg')
                cv2.imwrite(marked_path, image)
            except Exception:
                marked_path = temp_frame_path
        return jsonify({
            "success": True,
            "data": {
                "verified": bool(result.get("verified")),
                "distance": float(result.get("distance", 0.0)),
                "threshold": float(result.get("threshold", 0.0)),
                "model": result.get("model", "Facenet512"),
                "frame": marked_path if marked_path else temp_frame_path
            }
        })
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500
    
# ---------------- NEW: LIVE FACE RECOGNITION MULTI-FRAME ----------------
@app.route("/analyze/face_live", methods=["POST"])
def analyze_face_live():
    try:
        ip_url = request.form.get("ip_url")  # frontend sends IP webcam URL
        input_img = request.files.get("input")  # reference image

        if not ip_url or not input_img:
            return jsonify({"error": "Provide 'ip_url' and 'input'"}), 400

        # Save input reference image
        input_path = save_file(input_img)

        # Open video stream from phone
        cap = cv2.VideoCapture(ip_url)
        found = False
        frame_count = 0
        while frame_count < 50:  # check first 50 frames
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1
            temp_path = f"uploads/temp_frame_{frame_count}.jpg"
            cv2.imwrite(temp_path, frame)

            # Use ArcFace (InsightFace) for face verification - 4x faster, 99.8% accurate
            try:
                recognizer = get_face_recognizer()
                arc_result = recognizer.verify_faces(input_path, temp_path, threshold=1.2)
                if arc_result["verified"]:
                    found = True
                    break
            except Exception as e:
                # Fallback to DeepFace if ArcFace fails
                print(f"ArcFace verification failed: {e}, using DeepFace fallback")
                result = DeepFace.verify(img1_path=input_path, img2_path=temp_path, enforce_detection=False)
                if result["verified"]:
                    found = True
                    break

        cap.release()
        return jsonify({"success": True, "data": {"verified": found, "checked_frames": frame_count}})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
# ---------------- LIVE OBJECT DETECTION (IP CAMERA) ----------------
@app.route("/analyze/live_object", methods=["POST"])
def analyze_live_object():
    ipcam_url = request.form.get("url")
    input_img = request.files.get("input")
    if not ipcam_url or not input_img:
        return jsonify({"error": "Provide 'url' and 'input'"}), 400

    input_path = save_file(input_img)
    try:
        cap = cv2.VideoCapture(ipcam_url)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return jsonify({"error": "Could not read frame from IP camera"}), 500

        temp_frame_path = os.path.join(UPLOAD_FOLDER, f"live_object_{int(time.time())}.jpg")
        cv2.imwrite(temp_frame_path, frame)

        # Detect most confident class in reference image
        ref_results = yolo_model(input_path)
        ref_df = ref_results.pandas().xyxy[0]
        if ref_df.empty:
            return jsonify({
                "detections": [],
                "frame": None,
                "message": "No object detected in reference image. Please upload a clear image of the object you want to find."
            })
        best_row = ref_df.loc[ref_df['confidence'].idxmax()]
        target_class = best_row['name']

        results = yolo_model(temp_frame_path)
        df = results.pandas().xyxy[0]
        image = cv2.imread(temp_frame_path)
        best_detection = None
        best_conf = -1
        best_marked_path = None
        for _, row in df.iterrows():
            if row["confidence"] >= yolo_model.conf and row["name"] == target_class:
                if row["confidence"] > best_conf:
                    detection = {
                        "label": row["name"],
                        "confidence": float(row["confidence"]),
                        "bbox": [float(row["xmin"]), float(row["ymin"]), float(row["xmax"]), float(row["ymax"])]
                    }
                    x1, y1, x2, y2 = int(row["xmin"]), int(row["ymin"]), int(row["xmax"]), int(row["ymax"])
                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 3)
                    marked_path = temp_frame_path.replace('.jpg', '_marked.jpg')
                    cv2.imwrite(marked_path, image)
                    best_detection = detection
                    best_conf = row["confidence"]
                    best_marked_path = marked_path
        if best_detection:
            return jsonify({
                "success": True,
                "data": {
                    "detections": [best_detection],
                    "frame": best_marked_path
                }
            })
        else:
            return jsonify({
                "success": False,
                "message": "Object not found in live frame.",
                "data": {"detections": [], "frame": None}
            })
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500
import os

# ---------------- INITIAL SETUP ----------------
import cv2
import time
import uuid
import torch
import librosa
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from deepface import DeepFace

app = Flask(__name__)
CORS(app)

# Serve images from uploads directory
from flask import send_from_directory

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- LOAD YOLOv8 MODEL ----------------
print("Loading default YOLOv8s model...")
from ultralytics import YOLO
yolo_model = YOLO('yolov8s.pt')
yolo_model.conf = 0.2  # Lower confidence threshold for more sensitive detection
print("YOLOv8s model loaded ✅ (Upgraded from YOLOv5s - 7.5% better accuracy)")

# Allowed belongings
WANTED_CLASSES = {"backpack", "handbag", "suitcase", "cell phone", "laptop", "book", "umbrella"}

# Initialize ArcFace for face recognition
print("Initializing ArcFace (InsightFace Buffalo_L) for face recognition...")
try:
    initialize_arcface()
    print("ArcFace initialized ✅ (4x faster than Facenet512, 99.8% accuracy)")
except Exception as e:
    print(f"⚠️  Warning: ArcFace initialization failed - {e}")
    print("   Face recognition may not be available")

# Save uploaded file
def save_file(file):
    filename = f"{int(time.time())}_{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)
    return path

# ---------------- FACE RECOGNITION WITH AUTO IMAGE PROCESSING ----------------
@app.route("/analyze/face", methods=["POST"])
def analyze_face():
    try:
        input_img = request.files.get("input")
        frame_file = request.files.get("frame")
        
        if not input_img or not frame_file:
            return jsonify({"error": "Provide 'input' and 'frame'"}), 400

        input_path = save_file(input_img)
        frame_path = save_file(frame_file)
        
        # Automatically enhance input image for face recognition
        from image_processing import extract_and_enhance_face
        recognizer = get_face_recognizer()
        enhanced_input, enhanced_input_path, input_enhancements = extract_and_enhance_face(input_path, detector=recognizer)
        if input_enhancements:
            print(f"Auto-enhanced input image: {input_enhancements}")
            input_path = enhanced_input_path  # Use face-enhanced version

        video_exts = [".mp4", ".avi", ".mov", ".mkv"]
        _, ext = os.path.splitext(frame_path)
        ext = ext.lower()
        if ext in video_exts:
            vidcap = cv2.VideoCapture(frame_path)
            fps = vidcap.get(cv2.CAP_PROP_FPS)
            total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = int(total_frames / fps) if fps else total_frames
            sec = 0
            first_match = None
            while sec < duration:
                vidcap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
                success, image = vidcap.read()
                if not success:
                    break
                display_sec = round(sec, 1)
                temp_frame_path = f"{frame_path}_frame_{display_sec}.jpg"
                cv2.imwrite(temp_frame_path, image)
                frame_number = int(vidcap.get(cv2.CAP_PROP_POS_FRAMES))
                
                # Auto-enhance frame for face recognition
                enhanced_frame, enhanced_frame_path, frame_enhancements = extract_and_enhance_face(temp_frame_path, detector=recognizer)
                recognition_frame_path = enhanced_frame_path if frame_enhancements else temp_frame_path
                
                # Use ArcFace (InsightFace) for face verification - 4x faster, 99.8% accurate
                try:
                    recognizer = get_face_recognizer()
                    arc_result = recognizer.verify_faces(input_path, recognition_frame_path, threshold=1.2)
                    print(f"ArcFace - Frame {display_sec}s: Distance={arc_result['distance']:.4f}, Verified={arc_result['verified']}")
                    
                    # Store result
                    result = {
                        "verified": arc_result["verified"],
                        "distance": arc_result["distance"],
                        "threshold": 1.2,
                        "model": "ArcFace (Buffalo_L)"
                    }
                except Exception as e:
                    # Fallback to DeepFace if ArcFace fails
                    print(f"ArcFace verification failed: {e}, using DeepFace fallback")
                    result = DeepFace.verify(
                        img1_path=input_path,
                        img2_path=recognition_frame_path,
                        model_name="Facenet512",
                        enforce_detection=False,
                        detector_backend="opencv"
                    )
                if bool(result.get("verified")):
                    # Mark the face in the original frame (not enhanced) for display
                    try:
                        display_image = cv2.imread(temp_frame_path)  # Use original frame for display
                        
                        # Use robust ArcFace detector for marking boxes
                        detected_faces = recognizer.app.get(display_image)
                        for face in detected_faces:
                            bbox = [int(x) for x in face.bbox]
                            cv2.rectangle(display_image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 3)
                            break
                        
                        # Save marked image for display
                        marked_path = temp_frame_path.replace('.jpg', '_marked.jpg')
                        cv2.imwrite(marked_path, display_image)
                        
                    except Exception:
                        marked_path = temp_frame_path
                    
                    first_match = {
                        "verified": True,
                        "distance": float(result.get("distance", 0.0)),
                        "threshold": float(result.get("threshold", 0.0)),
                        "model": result.get("model", "ArcFace"),
                        "frame_number": frame_number,
                        "second": sec,
                        "frame": marked_path
                    }
                    
                    # Add enhancement info if applied
                    if input_enhancements or frame_enhancements:
                        first_match["auto_enhancements"] = {
                            "input_enhanced": input_enhancements,
                            "frame_enhanced": frame_enhancements
                        }
                    
                    break
                sec += 0.2  # Sampling updated to 200ms
            vidcap.release()
            if first_match:
                return jsonify({"success": True, "data": first_match})
            else:
                return jsonify({"success": False, "message": "No match found in video", "data": {"verified": False, "model": "ArcFace", "frame": None}})
        else:
            # Auto-enhance frame for face recognition
            enhanced_frame, enhanced_frame_path, frame_enhancements = extract_and_enhance_face(frame_path, detector=recognizer)
            recognition_frame_path = enhanced_frame_path if frame_enhancements else frame_path
            
            # Use ArcFace (InsightFace) for face verification - 4x faster, 99.8% accurate
            try:
                recognizer = get_face_recognizer()
                arc_result = recognizer.verify_faces(input_path, recognition_frame_path, threshold=1.2)
                # Convert ArcFace result to DeepFace-compatible format for backwards compatibility
                result = {
                    "verified": arc_result["verified"],
                    "distance": arc_result["distance"],
                    "threshold": 1.2,
                    "model": "ArcFace (Buffalo_L)"
                }
            except Exception as e:
                # Fallback to DeepFace if ArcFace fails
                print(f"ArcFace verification failed: {e}, using DeepFace fallback")
                result = DeepFace.verify(
                    img1_path=input_path,
                    img2_path=recognition_frame_path,
                    model_name="Facenet512",  # More stable than default
                    enforce_detection=False,
                    detector_backend="opencv"
                )
            
            marked_path = None
            
            if bool(result.get("verified")):
                try:
                    # Use original frame for display, not enhanced
                    image = cv2.imread(frame_path)
                    
                    # Use robust ArcFace detector for marking boxes
                    detected_faces = recognizer.app.get(image)
                    for face in detected_faces:
                        bbox = [int(x) for x in face.bbox]
                        cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 3)
                        break
                    
                    # Save marked image for display
                    marked_path = frame_path.replace('.jpg', '_marked.jpg').replace('.jpeg', '_marked.jpeg').replace('.png', '_marked.png')
                    cv2.imwrite(marked_path, image)
                            
                except Exception:
                    marked_path = frame_path
            
            return jsonify({
                "success": True,
                "data": {
                    "verified": bool(result.get("verified")),
                    "distance": float(result.get("distance", 0.0)),
                    "threshold": float(result.get("threshold", 1.2)),
                    "model": result.get("model", "ArcFace"),
                    "frame": marked_path if marked_path else frame_path
                }
            })
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500

# ---------------- OBJECT DETECTION ----------------
@app.route("/analyze/object", methods=["POST"])
def analyze_object():
    input_file = request.files.get("input")  # reference image
    frame_file = request.files.get("frame")  # sample image/video
    if not input_file or not frame_file:
        return jsonify({"error": "Provide 'input' and 'frame'"}), 400

    try:
        input_path = save_file(input_file)
        frame_path = save_file(frame_file)
        
        # Auto-enhance input image if needed
        enhanced_input, enhanced_input_path, input_enhancements = auto_enhance_image(input_path)
        if input_enhancements:
            print(f"Auto-enhanced input image: {input_enhancements}")
            input_path = enhanced_input_path  # Use enhanced version for object detection

        # Detect most confident class in reference image (person or object)
        ref_results = yolo_model.predict(input_path, conf=0.2)
        
        if not ref_results or len(ref_results) == 0:
            return jsonify({
                "success": False,
                "message": "No object detected in reference image. Please upload a clear image of the object you want to find.",
                "data": {"detections": [], "frame": None}
            })
        
        ref_result = ref_results[0]
        if len(ref_result.boxes) == 0:
            return jsonify({
                "success": False,
                "message": "No object detected in reference image. Please upload a clear image of the object you want to find.",
                "data": {"detections": [], "frame": None}
            })
        
        # Find the detection with highest confidence
        best_idx = 0
        best_conf = ref_result.boxes.conf[0]
        for i in range(len(ref_result.boxes.conf)):
            if ref_result.boxes.conf[i] > best_conf:
                best_conf = ref_result.boxes.conf[i]
                best_idx = i
        
        target_class = ref_result.names[int(ref_result.boxes.cls[best_idx])]

        video_exts = [".mp4", ".avi", ".mov", ".mkv"]
        _, ext = os.path.splitext(frame_path)
        ext = ext.lower()
        sample_objects = set()
        detections = []
        marked_path = None
        frame_enhancements = []
        if ext in video_exts:
            vidcap = cv2.VideoCapture(frame_path)
            fps = vidcap.get(cv2.CAP_PROP_FPS)
            total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = int(total_frames / fps) if fps else total_frames
            sec = 0
            best_detection = None
            best_conf = -1
            best_frame = None
            best_frame_number = None
            best_marked_path = None
            while sec < duration:
                vidcap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
                success, image = vidcap.read()
                if not success:
                    break
                display_sec = round(sec, 1)
                temp_frame_path = f"{frame_path}_frame_{display_sec}.jpg"
                cv2.imwrite(temp_frame_path, image)
                frame_number = int(vidcap.get(cv2.CAP_PROP_POS_FRAMES))
                
                # Auto-enhance frame if needed
                enhanced_frame, enhanced_frame_path, frame_enhancement = auto_enhance_image(temp_frame_path)
                if frame_enhancement:
                    temp_frame_path = enhanced_frame_path
                    if sec == 0:  # Only track enhancements for the best frame
                        frame_enhancements = frame_enhancement
                
                # YOLOv8 detection
                results = yolo_model.predict(temp_frame_path, conf=0.2)
                
                if results and len(results) > 0:
                    result = results[0]
                    image = cv2.imread(temp_frame_path)
                    
                    for i in range(len(result.boxes)):
                        cls_id = int(result.boxes.cls[i])
                        class_name = result.names[cls_id]
                        confidence = float(result.boxes.conf[i])
                        
                        if confidence >= 0.2 and class_name == target_class:
                            if confidence > best_conf:
                                # Get bounding box coordinates
                                box = result.boxes.xyxy[i]
                                x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
                                
                                detection = {
                                    "label": class_name,
                                    "confidence": confidence,
                                    "bbox": [x1, y1, x2, y2]
                                }
                                
                                # Draw bounding box
                                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 3)
                                marked_path = temp_frame_path.replace('.jpg', '_marked.jpg').replace('.jpeg', '_marked.jpeg').replace('.png', '_marked.png')
                                cv2.imwrite(marked_path, image)
                                
                                best_detection = detection
                                best_conf = confidence
                                best_frame = marked_path
                                best_frame_number = frame_number
                                best_sec = sec
                sec += 0.5  # Standardized sampling for emotion
            vidcap.release()
            if best_detection:
                return jsonify({
                    "success": True,
                    "data": {
                        "detections": [best_detection],
                        "second": best_sec,
                        "frame_number": best_frame_number,
                        "frame": best_frame,
                        "auto_enhancements": {
                            "input_enhanced": input_enhancements if input_enhancements else [],
                            "frame_enhanced": frame_enhancements if frame_enhancements else []
                        }
                    }
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "Object not found in video.",
                    "data": {
                        "detections": [], 
                        "second": None, 
                        "frame": None, 
                        "auto_enhancements": {
                            "input_enhanced": input_enhancements if input_enhancements else [],
                            "frame_enhanced": []
                        }
                    }
                })
        else:
            # Auto-enhance frame image if needed
            enhanced_frame, enhanced_frame_path, frame_enhancements = auto_enhance_image(frame_path)
            if frame_enhancements:
                frame_path = enhanced_frame_path
                print(f"Auto-enhanced frame image: {frame_enhancements}")
            
            # YOLOv8 detection
            results = yolo_model.predict(frame_path, conf=0.2)
            
            image = cv2.imread(frame_path)
            best_detection = None
            best_conf = -1
            best_marked_path = None
            
            if results and len(results) > 0:
                result = results[0]
                
                for i in range(len(result.boxes)):
                    cls_id = int(result.boxes.cls[i])
                    class_name = result.names[cls_id]
                    confidence = float(result.boxes.conf[i])
                    
                    if confidence >= 0.2 and class_name == target_class:
                        if confidence > best_conf:
                            # Get bounding box coordinates
                            box = result.boxes.xyxy[i]
                            x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
                            
                            detection = {
                                "label": class_name,
                                "confidence": confidence,
                                "bbox": [x1, y1, x2, y2]
                            }
                            
                            # Draw bounding box
                            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 3)
                            marked_path = frame_path.replace('.jpg', '_marked.jpg').replace('.jpeg', '_marked.jpeg').replace('.png', '_marked.png')
                            cv2.imwrite(marked_path, image)
                            
                            best_detection = detection
                            best_conf = confidence
                            best_marked_path = marked_path
            if best_detection:
                return jsonify({
                    "success": True,
                    "data": {
                        "detections": [best_detection],
                        "frame": best_marked_path,
                        "auto_enhancements": {
                            "input_enhanced": input_enhancements if input_enhancements else [],
                            "frame_enhanced": frame_enhancements if frame_enhancements else []
                        }
                    }
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "Object not found in image.",
                    "data": {
                        "detections": [], 
                        "frame": None, 
                        "auto_enhancements": {
                            "input_enhanced": input_enhancements if input_enhancements else [],
                            "frame_enhanced": frame_enhancements if frame_enhancements else []
                        }
                    }
                })
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ---------------- EMOTION DETECTION ----------------
@app.route("/analyze/emotion", methods=["POST"])
def analyze_emotion_endpoint():
    """
    Analyze emotion from image or video file using DeepFace
    
    Request:
        - frame: Image or video file
        
    Returns:
        {
            "status": "success",
            "dominant_emotion": "fear" | "angry" | "happy" | "sad" | "neutral" | "surprise" | "disgust",
            "emotions": {
                "fear": 0.85,
                ...
            },
            "confidence": 0.85
        }
    """
    try:
        frame_file = request.files.get("frame")
        if not frame_file:
            return jsonify({"error": "Provide 'frame'"}), 400

        frame_path = save_file(frame_file)

        video_exts = [".mp4", ".avi", ".mov", ".mkv"]
        image_exts = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]
        _, ext = os.path.splitext(frame_path)
        ext = ext.lower()
        
        if ext in video_exts:
            # Video processing - extract frames and analyze
            vidcap = cv2.VideoCapture(frame_path)
            if not vidcap.isOpened():
                return jsonify({"error": "Could not open video file", "status": "failed"}), 400
            
            fps = vidcap.get(cv2.CAP_PROP_FPS) or 30
            total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = int(total_frames / fps) if fps else total_frames
            
            sec = 0
            first_emotion = None
            analyzed_frames = 0
            
            while sec < duration and analyzed_frames < 10:  # Max 10 frames analyzed
                vidcap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
                success, image = vidcap.read()
                if not success:
                    break
                    
                temp_frame_path = f"{frame_path}_frame_{sec}.jpg"
                cv2.imwrite(temp_frame_path, image)
                
                try:
                    # Use DeepFace emotion detection
                    result = DeepFace.analyze(
                        img_path=temp_frame_path,
                        actions=['emotion'],
                        enforce_detection=False,
                        detector_backend='opencv'
                    )
                    
                    if isinstance(result, list) and len(result) > 0:
                        result = result[0]
                        
                        emotions = result.get("emotion", {})
                        dominant_emotion = result.get("dominant_emotion", "neutral")
                        
                        # Calculate confidence as percentage of dominant emotion
                        total = sum(emotions.values())
                        confidence = emotions.get(dominant_emotion, 0) / total if total > 0 else 0
                        
                        first_emotion = {
                            "status": "success",
                            "dominant_emotion": dominant_emotion,
                            "emotions": emotions,
                            "confidence": confidence,
                            "face_detected": True,
                            "frame_second": sec
                        }
                        break
                    
                    analyzed_frames += 1
                except Exception as e:
                    print(f"Frame analysis error at {sec}s: {str(e)}")
                    analyzed_frames += 1
                
                sec += 0.5  # Standardized sampling for emotion
            
            vidcap.release()
            
            if first_emotion:
                return jsonify({"success": True, "data": first_emotion})
            else:
                return jsonify({
                    "success": False,
                    "status": "no_emotions_detected",
                    "dominant_emotion": None,
                    "emotions": {},
                    "message": "No clear emotion detected in video"
                }), 200
                
        elif ext in image_exts:
            # Image processing
            result = DeepFace.analyze(
                img_path=frame_path,
                actions=['emotion'],
                enforce_detection=False,
                detector_backend='opencv'
            )
            
            if isinstance(result, list) and len(result) > 0:
                result = result[0]
                
            emotions = result.get("emotion", {})
            dominant_emotion = result.get("dominant_emotion", "neutral")
            
            # Calculate confidence as percentage of dominant emotion
            total = sum(emotions.values())
            confidence = emotions.get(dominant_emotion, 0) / total if total > 0 else 0
            
            return jsonify({
                "success": True,
                "data": {
                    "status": "success",
                    "dominant_emotion": dominant_emotion,
                    "emotions": emotions,
                    "confidence": confidence,
                    "face_detected": True
                }
            })
        else:
            return jsonify({
                "error": "Unsupported file type for emotion analysis. Please upload an image or video file.",
                "supported_formats": {
                    "images": ["jpg", "jpeg", "png", "bmp", "webp"],
                    "videos": ["mp4", "avi", "mov", "mkv"]
                }
            }), 400
            
    except Exception as e:
        import traceback
        print(f"Emotion analysis error: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "status": "failed"
        }), 500

# ---------------- AUDIO PANIC DETECTION ----------------
@app.route("/analyze/audio", methods=["POST"])
def analyze_audio():
    try:
        print(f"Audio analysis request received. Files: {list(request.files.keys())}")
        print(f"Form data: {dict(request.form)}")
        
        audio = request.files.get("audio")
        if not audio:
            return jsonify({
                "error": "Provide 'audio'",
                "details": "No audio file found in request. Make sure to send the file with key 'audio'",
                "received_files": list(request.files.keys())
            }), 400

        print(f"Audio file received: {audio.filename}")
        
        # Check if filename exists
        if not audio.filename:
            return jsonify({
                "error": "Invalid audio file",
                "details": "Audio file has no filename"
            }), 400

        allowed_types = [".mp3", ".wav", ".ogg", ".mpeg", ".mpg", ".aac", ".m4a", ".webm"]
        _, ext = os.path.splitext(audio.filename)
        ext = ext.lower()
        print(f"Audio file extension: {ext}")
        
        if ext not in allowed_types:
            return jsonify({
                "error": "Unsupported file type for audio analysis",
                "details": f"File extension '{ext}' is not supported. Please upload a valid audio file (mp3, wav, ogg, mpeg, aac, m4a, webm)",
                "filename": audio.filename,
                "supported_types": allowed_types
            }), 400

        path = save_file(audio)
        print(f"Audio file saved to: {path}")
        
        try:
            y, sr = librosa.load(path, sr=None, mono=True)
            print(f"Audio loaded successfully. Length: {len(y)}, Sample rate: {sr}")
        except Exception as audio_load_error:
            print(f"Error loading audio file: {audio_load_error}")
            return jsonify({
                "error": "Failed to load audio file",
                "details": str(audio_load_error),
                "filename": audio.filename
            }), 400
        
        # Calculate raw energy
        raw_energy = float(np.mean(np.abs(y))) if len(y) else 0.0
        
        # Convert from 0.0-1.0 scale to 1-1000 scale
        # Clamp the raw energy to prevent values above 1000
        clamped_energy = min(raw_energy, 1.0)
        volume = int((clamped_energy * 999) + 1)  # Scale to 1-1000
        
        # Volume Range Classification:
        # 1-10: Complete silence to whisper
        # 11-30: Quiet conversation  
        # 31-50: Normal conversation
        # 51-60: Loud talking (NORMAL threshold)
        # 61-150: Shouting/Raised voice (PANIC range)
        # 151-500: Screaming/Panic sounds
        # 501-1000: Very loud/intense sounds
        
        # Set panic threshold at volume level 60 (equivalent to old 0.06)
        status = "PANIC" if volume > 60 else "NORMAL"
        
        # Determine volume category for better user understanding
        if volume <= 10:
            volume_category = "Complete silence to whisper"
        elif volume <= 30:
            volume_category = "Quiet conversation"
        elif volume <= 50:
            volume_category = "Normal conversation"
        elif volume <= 60:
            volume_category = "Loud talking"
        elif volume <= 150:
            volume_category = "Shouting/Raised voice"
        elif volume <= 500:
            volume_category = "Screaming/Panic sounds"
        else:
            volume_category = "Very loud/intense sounds"

        response_data = {
            "volume": volume,
            "status": status,
            "volume_category": volume_category,
            "raw_energy": round(raw_energy, 4),  # Keep for debugging
            "filename": audio.filename,
            "sample_rate": sr,
            "audio_length_seconds": round(len(y) / sr, 2) if sr > 0 else 0
        }
        print(f"Audio analysis successful: {response_data}")
        return jsonify({"success": True, "data": response_data})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        error_details = {
            "success": False,
            "message": str(e),
            "type": type(e).__name__
        }
        if 'audio' in locals():
            error_details["filename"] = getattr(audio, 'filename', 'unknown')
        print(f"Audio analysis error: {error_details}")
        return jsonify(error_details), 500

# ---------------- HEALTH CHECK ----------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "yolov5": True, "deepface": True})

# ----------------HEALTH CHECK & DEBUG ENDPOINTS ----------------
@app.route("/health", methods=["GET"])
def health_check():
    """System health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Guardian AI Backend",
        "version": "1.0",
        "endpoints": {
            "face_recognition": "/analyze/face",
            "object_detection": "/analyze/object",
            "emotion_analysis": "/analyze/emotion",
            "audio_panic_detection": "/analyze/audio",
            "live_face_recognition": "/analyze/live_face",
            "live_face_multiframe": "/analyze/face_live",
            "live_object_detection": "/analyze/live_object",
            "health": "/health",
            "test_emotion": "/test/emotion"
        }
    })

@app.route("/test/emotion", methods=["GET"])
def test_emotion():
    """Test endpoint to verify emotion detection is working"""
    try:
        # Test with a sample image if available
        test_image_path = None
        if os.path.exists("dataset/faces/crowd_scene.jpg"):
            test_image_path = "dataset/faces/crowd_scene.jpg"
        elif os.path.exists("uploads"):
            # Find first jpg in uploads
            for f in os.listdir("uploads"):
                if f.endswith(('.jpg', '.jpeg', '.png')):
                    test_image_path = os.path.join("uploads", f)
                    break
        
        if not test_image_path:
            return jsonify({
                "status": "no_test_image",
                "message": "Place a test image in dataset/faces/ or uploads/ folder",
                "test_status": "ready",
                "module_status": "working"
            }), 200
        
        # Run emotion detection with DeepFace
        result = DeepFace.analyze(
            img_path=test_image_path,
            actions=['emotion'],
            enforce_detection=False,
            detector_backend='opencv'
        )
        
        if isinstance(result, list) and len(result) > 0:
            result = result[0]
        
        emotions = result.get("emotion", {})
        dominant_emotion = result.get("dominant_emotion", "neutral")
        total = sum(emotions.values())
        confidence = emotions.get(dominant_emotion, 0) / total if total > 0 else 0
        
        return jsonify({
            "test_status": "success",
            "emotion_detection": "working",
            "result": {
                "status": "success",
                "dominant_emotion": dominant_emotion,
                "emotions": emotions,
                "confidence": confidence
            }
        }), 200
    except Exception as e:
        import traceback
        return jsonify({
            "test_status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8001, debug=True, use_reloader=False)
