import cv2
import numpy as np
import os

def auto_enhance_image(image_path):
    """
    Automatically detect image quality issues and apply appropriate enhancements
    Returns: (enhanced_image_array, enhanced_path, enhancements_list)
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            return None, image_path, []
        
        # Convert to grayscale for quality analysis
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate image quality metrics
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        brightness = np.mean(gray)
        contrast = gray.std()
        
        enhanced = image.copy()
        enhancement_applied = []
        
        # Apply enhancements based on quality metrics
        
        # 1. Check for blur (low blur_score means blurry)
        if blur_score < 150:  # Increased threshold for better detection
            # Apply unsharp masking for better sharpening
            gaussian = cv2.GaussianBlur(enhanced, (0, 0), 2.0)
            enhanced = cv2.addWeighted(enhanced, 2.0, gaussian, -1.0, 0)
            enhancement_applied.append("sharpening")
        
        # 2. Check for low contrast
        if contrast < 35:  # Slightly increased threshold
            # Apply CLAHE for low contrast
            lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            lab[:,:,0] = clahe.apply(lab[:,:,0])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            enhancement_applied.append("contrast_enhancement")
        
        # 3. Check for poor lighting
        if brightness < 60:  # Too dark
            enhanced = cv2.convertScaleAbs(enhanced, alpha=1.2, beta=25)
            enhancement_applied.append("brightness_increase")
        elif brightness > 190:  # Too bright
            enhanced = cv2.convertScaleAbs(enhanced, alpha=0.85, beta=-15)
            enhancement_applied.append("brightness_decrease")
        
        # 4. Apply noise reduction if needed
        noise_level = np.std(cv2.Laplacian(gray, cv2.CV_64F))
        if noise_level > 25:
            enhanced = cv2.fastNlMeansDenoisingColored(enhanced, None, 8, 8, 7, 21)
            enhancement_applied.append("denoising")
        
        # 5. Additional enhancement for face recognition - gamma correction
        if brightness < 80 or contrast < 25:
            gamma = 1.2 if brightness < 80 else 0.9
            inv_gamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
            enhanced = cv2.LUT(enhanced, table)
            enhancement_applied.append("gamma_correction")
        
        # Save enhanced image if any enhancements were applied
        if enhancement_applied:
            enhanced_path = save_processed_image(enhanced, image_path, "_auto_enhanced")
            return enhanced, enhanced_path, enhancement_applied
        else:
            return image, image_path, []
            
    except Exception as e:
        print(f"Error in auto_enhance_image: {str(e)}")
        return None, image_path, []

def apply_image_filters(image_path, filter_type="gaussian"):
    """
    Apply various filters to the image
    """
    image = cv2.imread(image_path)
    if image is None:
        return None
    
    if filter_type == "gaussian":
        filtered = cv2.GaussianBlur(image, (15, 15), 0)
    
    elif filter_type == "median":
        filtered = cv2.medianBlur(image, 15)
    
    elif filter_type == "bilateral":
        filtered = cv2.bilateralFilter(image, 9, 75, 75)
    
    elif filter_type == "edge_detection":
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        filtered = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    elif filter_type == "emboss":
        kernel = np.array([[-2, -1, 0], [-1, 1, 1], [0, 1, 2]])
        filtered = cv2.filter2D(image, -1, kernel)
    
    elif filter_type == "blur_background":
        # Advanced background blur while keeping face sharp
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        # Create mask for face region
        mask = np.zeros(gray.shape, dtype=np.uint8)
        for (x, y, w, h) in faces:
            cv2.ellipse(mask, (x + w//2, y + h//2), (w//2, h//2), 0, 0, 360, 255, -1)
        
        # Blur the entire image
        blurred = cv2.GaussianBlur(image, (21, 21), 0)
        
        # Combine original face region with blurred background
        mask_3d = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) / 255.0
        filtered = (image * mask_3d + blurred * (1 - mask_3d)).astype(np.uint8)
    
    else:
        filtered = image
    
    return filtered

def crop_face_region(image_path, face_coords, padding=20):
    """
    Crop the face region from the image with padding
    """
    image = cv2.imread(image_path)
    if image is None or not face_coords:
        return None
    
    x, y, w, h = face_coords
    # Add padding around the face
    x = max(0, x - padding)
    y = max(0, y - padding)
    w = min(image.shape[1] - x, w + 2*padding)
    h = min(image.shape[0] - y, h + 2*padding)
    
    cropped_face = image[y:y+h, x:x+w]
    return cropped_face

def extract_and_enhance_face(image_path, detector=None):
    """
    Extract face from image with MINIMAL enhancements for face recognition.
    Over-enhancement distorts face embeddings and reduces matching accuracy.
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            return None, image_path, []
        
        faces = []
        if detector and hasattr(detector, 'app'):
            # Use robust InsightFace detector if provided
            detected_faces = detector.app.get(image)
            for face in detected_faces:
                bbox = [int(x) for x in face.bbox]
                faces.append((bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1])) # x, y, w, h
        else:
            # Fallback to Haar Cascade if no robust detector available
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(30, 30))
        
        if len(faces) > 0:
            # Get the largest face
            largest_face = max(faces, key=lambda x: x[2] * x[3])
            x, y, w, h = largest_face
            
            # Add minimal padding around face
            padding_w = int(w * 0.15)
            padding_h = int(h * 0.15)
            x1 = max(0, x - padding_w)
            y1 = max(0, y - padding_h)
            x2 = min(image.shape[1], x + w + padding_w)
            y2 = min(image.shape[0], y + h + padding_h)
            
            # Extract face region
            face_region = image[y1:y2, x1:x2]
            enhancements = []
            
            # IMPORTANT: For face recognition, minimal enhancement preserves embeddings
            # Only apply CLAHE if image is very dark or low contrast
            gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray_face)
            contrast = gray_face.std()
            
            enhanced_face = face_region.copy()
            
            # Only apply light CLAHE for very low contrast images (don't over-enhance)
            if contrast < 20:
                lab = cv2.cvtColor(enhanced_face, cv2.COLOR_BGR2LAB)
                clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8,8))
                lab[:,:,0] = clahe.apply(lab[:,:,0])
                enhanced_face = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
                enhancements.append("light_contrast_boost")
            
            # Only slightly adjust brightness if very dark
            if brightness < 50:
                enhanced_face = cv2.convertScaleAbs(enhanced_face, alpha=1.1, beta=10)
                enhancements.append("brightness_adjustment")
            
            # Save if enhancements were applied
            if enhancements:
                enhanced_path = save_processed_image(enhanced_face, image_path, "_face_enhanced")
                return enhanced_face, enhanced_path, enhancements
            else:
                # Return original if no enhancements needed
                return face_region, image_path, []
            
    except Exception as e:
        print(f"Error in extract_and_enhance_face: {str(e)}")
        return None, image_path, []

def save_processed_image(processed_image, original_path, suffix):
    """
    Save processed image with a suffix
    """
    base_name = os.path.splitext(original_path)[0]
    extension = os.path.splitext(original_path)[1]
    new_path = f"{base_name}{suffix}{extension}"
    cv2.imwrite(new_path, processed_image)
    return new_path
