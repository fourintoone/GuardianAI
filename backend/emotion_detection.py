# emotion_detection.py
import cv2
import numpy as np
from deepface import DeepFace
import traceback
import os

def analyze_emotion(frame_img, enforce_detection=False, return_face_region=False):
    """
    Enhanced emotion detection with better error handling and face validation
    
    Args:
        frame_img: Path to image file or image array
        enforce_detection: Whether to enforce face detection
        return_face_region: Return face region data for visualization
        
    Returns:
        Dictionary with emotion analysis results
    """
    try:
        # Validate image exists and can be read
        if isinstance(frame_img, str):
            if not os.path.exists(frame_img):
                return {
                    "error": f"Image file not found: {frame_img}",
                    "status": "failed"
                }
            img = cv2.imread(frame_img)
            if img is None:
                return {
                    "error": "Could not read image file",
                    "status": "failed"
                }
        else:
            img = frame_img
        
        # Check image dimensions
        if img is None or len(img.shape) < 2 or img.shape[0] < 20 or img.shape[1] < 20:
            return {
                "error": "Image too small or invalid for emotion detection",
                "status": "failed",
                "dimensions": img.shape if img is not None else None
            }
        
        # Perform emotion analysis with multiple tries
        try:
            result = DeepFace.analyze(
                img_path=frame_img,
                actions=['emotion'],
                enforce_detection=enforce_detection,
                detector_backend='opencv'  # Explicitly use OpenCV for reliability
            )
        except Exception as deepface_error:
            print(f"DeepFace first attempt failed: {deepface_error}")
            # Try with different detector backend
            try:
                result = DeepFace.analyze(
                    img_path=frame_img,
                    actions=['emotion'],
                    enforce_detection=False,
                    detector_backend='retinaface'
                )
            except:
                # Final fallback
                result = DeepFace.analyze(
                    img_path=frame_img,
                    actions=['emotion'],
                    enforce_detection=False,
                    detector_backend='mtcnn'
                )
        
        # Handle both list and dict responses
        if isinstance(result, list):
            if len(result) == 0:
                return {
                    "error": "No faces detected in image",
                    "status": "no_faces",
                    "emotions": {},
                    "face_detected": False
                }
            # If multiple faces, use the largest/most prominent one
            result = result[0] if len(result) == 1 else max(result, key=lambda x: x.get('region', {}).get('w', 0) * x.get('region', {}).get('h', 0))
        
        # Extract emotion data
        emotions = result.get('emotion', {})
        dominant_emotion = result.get('dominant_emotion', 'unknown')
        face_region = result.get('region', {}) if return_face_region else None
        
        if not emotions:
            return {
                "error": "No emotion data extracted",
                "status": "failed",
                "emotions": {},
                "face_detected": True
            }
        
        # Convert emotion scores to float and percentage
        emotions_clean = {}
        max_emotion = 0
        max_emotion_name = dominant_emotion
        
        for emotion, score in emotions.items():
            score_float = float(score)
            emotions_clean[emotion] = {
                "value": score_float,
                "percentage": f"{score_float:.2f}%"
            }
            if score_float > max_emotion:
                max_emotion = score_float
                max_emotion_name = emotion
        
        # Use the actual maximum emotion, not the one from DeepFace
        dominant_emotion = max_emotion_name
        
        response = {
            "status": "success",
            "dominant_emotion": dominant_emotion,
            "emotions": emotions_clean,
            "confidence": float(max_emotion),
            "face_detected": True
        }
        
        if return_face_region and face_region:
            response["face_region"] = face_region
        
        return response
        
    except Exception as e:
        print(f"Emotion detection error: {str(e)}")
        traceback.print_exc()
        return {
            "error": str(e),
            "status": "failed",
            "emotions": {},
            "face_detected": False
        }

def analyze_emotion_batch(frame_imgs):
    """
    Analyze multiple frames for emotion
    
    Args:
        frame_imgs: List of image paths or arrays
        
    Returns:
        List of emotion analysis results
    """
    results = []
    for frame_img in frame_imgs:
        result = analyze_emotion(frame_img)
        results.append(result)
    return results

def get_panic_level(dominant_emotion, confidence):
    """
    Determine panic/threat level based on emotion with improved sensitivity
    
    Args:
        dominant_emotion: The dominant emotion detected
        confidence: Confidence score (0-100)
        
    Returns:
        Panic level and risk assessment
    """
    # Emotion threat weights (0-1)
    panic_emotions = {
        'fear': 0.95,      # Highest threat
        'angry': 0.85,     # High threat
        'disgust': 0.45,   # Medium threat
        'sad': 0.35,       # Low threat
        'surprise': 0.25,  # Minimal threat
        'happy': 0.0,      # No threat
        'neutral': 0.05    # Minimal threat
    }
    
    # Get base panic score from emotion type
    base_panic = panic_emotions.get(dominant_emotion.lower(), 0.0)
    
    # Normalize confidence to 0-1 range if it's in 0-100 format
    if confidence > 10:  # Likely 0-100 scale
        normalized_confidence = confidence / 100.0
    else:
        normalized_confidence = confidence
    
    # Confidence must be > 20% for meaningful threat assessment
    if normalized_confidence < 0.2:
        confidence_factor = 0.5  # Reduce impact if low confidence
    else:
        confidence_factor = 1.0  # Full impact if high confidence
    
    # Calculate final panic score
    panic_score = base_panic * normalized_confidence * confidence_factor
    
    # Risk levels with sensitivity adjustment
    if dominant_emotion.lower() in ['fear', 'angry']:
        # Higher emotions are more sensitive
        if panic_score >= 0.6:
            risk_level = "HIGH"
        elif panic_score >= 0.3:
            risk_level = "MEDIUM"
        elif panic_score >= 0.1:
            risk_level = "LOW"
        else:
            risk_level = "NORMAL"
    else:
        # Standard risk assessment for other emotions
        if panic_score >= 0.5:
            risk_level = "MEDIUM"
        elif panic_score >= 0.2:
            risk_level = "LOW"
        else:
            risk_level = "NORMAL"
    
    return {
        "panic_score": float(panic_score),
        "risk_level": risk_level,
        "emotion": dominant_emotion,
        "confidence": float(normalized_confidence * 100),  # Return as 0-100
        "threat_weight": float(base_panic)
    }

# Test the module
if __name__ == "__main__":
    frame_img = "dataset/faces/crowd_scene.jpg"
    result = analyze_emotion(frame_img)
    print("Emotion Analysis Result:")
    print(result)
    
    if result.get('status') == 'success':
        panic_level = get_panic_level(
            result['dominant_emotion'],
            result['confidence']
        )
        print("\nPanic Level Assessment:")
        print(panic_level)
