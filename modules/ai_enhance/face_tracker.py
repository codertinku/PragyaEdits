"""
Face Tracking Module
Provides advanced face detection, smart portrait cropping, and multi-aspect ratio support
"""

import subprocess
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import mediapipe as mp


def track_faces(video_path: str, confidence_threshold: float = 0.5) -> List[Dict]:
    """
    Track faces throughout video using MediaPipe
    
    Args:
        video_path: Path to video file
        confidence_threshold: Minimum confidence for face detection
    
    Returns:
        List of face tracking data for each frame
    """
    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(
        model_selection=1, 
        min_detection_confidence=confidence_threshold
    )
    
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    tracking_data = []
    frame_idx = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb_frame)
        
        frame_data = {
            "frame": frame_idx,
            "timestamp": frame_idx / fps if fps > 0 else 0,
            "faces": []
        }
        
        if results.detections:
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                h, w, _ = frame.shape
                
                face_info = {
                    "x": int(bbox.xmin * w),
                    "y": int(bbox.ymin * h),
                    "width": int(bbox.width * w),
                    "height": int(bbox.height * h),
                    "confidence": detection.score[0]
                }
                frame_data["faces"].append(face_info)
        
        tracking_data.append(frame_data)
        frame_idx += 1
    
    cap.release()
    face_detection.close()
    
    return tracking_data


def get_primary_face_region(tracking_data: List[Dict], 
                           start_time: float = 0, 
                           end_time: Optional[float] = None) -> Optional[Dict]:
    """
    Get the primary face region for a time segment
    
    Args:
        tracking_data: Face tracking data
        start_time: Start time in seconds
        end_time: End time in seconds (None = end of video)
    
    Returns:
        Average face region dictionary or None
    """
    if not tracking_data:
        return None
    
    # Filter frames in time range
    relevant_frames = [
        frame for frame in tracking_data
        if start_time <= frame["timestamp"] and (end_time is None or frame["timestamp"] <= end_time)
    ]
    
    if not relevant_frames:
        return None
    
    # Collect all face bounding boxes
    all_faces = []
    for frame in relevant_frames:
        if frame["faces"]:
            # Take the largest face (likely the primary subject)
            largest_face = max(frame["faces"], key=lambda f: f["width"] * f["height"])
            all_faces.append(largest_face)
    
    if not all_faces:
        return None
    
    # Calculate average face position
    avg_x = int(np.mean([f["x"] for f in all_faces]))
    avg_y = int(np.mean([f["y"] for f in all_faces]))
    avg_width = int(np.mean([f["width"] for f in all_faces]))
    avg_height = int(np.mean([f["height"] for f in all_faces]))
    
    return {
        "x": avg_x,
        "y": avg_y,
        "width": avg_width,
        "height": avg_height
    }


def smart_crop_portrait(video_path: str, output_path: str, 
                       target_aspect: str = "9:16",
                       padding_factor: float = 1.5,
                       tracking_data: Optional[List[Dict]] = None) -> str:
    """
    Smart crop video to portrait mode focusing on detected faces
    
    Args:
        video_path: Path to input video
        output_path: Path to save cropped video
        target_aspect: Target aspect ratio (9:16, 4:5, 1:1)
        padding_factor: Padding around face (1.0 = tight, 2.0 = loose)
        tracking_data: Pre-computed tracking data (optional)
    
    Returns:
        Path to cropped video
    """
    # Track faces if not provided
    if tracking_data is None:
        tracking_data = track_faces(video_path)
    
    # Get primary face region
    face_region = get_primary_face_region(tracking_data)
    
    # Get video dimensions
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    
    # Parse target aspect ratio
    aspect_parts = target_aspect.split(":")
    aspect_w, aspect_h = int(aspect_parts[0]), int(aspect_parts[1])
    
    # Calculate crop dimensions
    if aspect_w > aspect_h:  # Landscape
        crop_width = width
        crop_height = int(width * aspect_h / aspect_w)
    else:  # Portrait or square
        crop_height = height
        crop_width = int(height * aspect_w / aspect_h)
    
    # Determine crop center
    if face_region:
        # Center on face
        face_center_x = face_region["x"] + face_region["width"] // 2
        face_center_y = face_region["y"] + face_region["height"] // 2
        
        # Apply padding
        face_size = max(face_region["width"], face_region["height"])
        min_crop_width = int(face_size * padding_factor)
        min_crop_height = int(face_size * padding_factor)
        
        crop_width = max(crop_width, min_crop_width)
        crop_height = max(crop_height, min_crop_height)
        
        # Ensure crop doesn't exceed video dimensions
        crop_width = min(crop_width, width)
        crop_height = min(crop_height, height)
        
        # Calculate crop position
        crop_x = max(0, min(face_center_x - crop_width // 2, width - crop_width))
        crop_y = max(0, min(face_center_y - crop_height // 2, height - crop_height))
    else:
        # No face detected, center crop
        crop_x = (width - crop_width) // 2
        crop_y = (height - crop_height) // 2
    
    # Apply crop using ffmpeg
    crop_filter = f"crop={crop_width}:{crop_height}:{crop_x}:{crop_y}"
    
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-vf", crop_filter,
        "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
        "-c:a", "copy",
        str(output_path)
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    return str(output_path)


def export_multi_aspect(video_path: str, output_dir: str,
                       aspect_ratios: Optional[List[str]] = None,
                       tracking_data: Optional[List[Dict]] = None) -> Dict[str, str]:
    """
    Export video in multiple aspect ratios optimized for different platforms
    
    Args:
        video_path: Path to input video
        output_dir: Directory to save exports
        aspect_ratios: List of aspect ratios (None = common ratios)
        tracking_data: Pre-computed tracking data (optional)
    
    Returns:
        Dictionary mapping aspect ratio to output path
    """
    if aspect_ratios is None:
        aspect_ratios = [
            "9:16",   # Instagram Reels, TikTok, YouTube Shorts
            "4:5",    # Instagram Feed
            "1:1",    # Instagram Square
            "16:9",   # YouTube, Landscape
        ]
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Track faces once for all exports
    if tracking_data is None:
        tracking_data = track_faces(video_path)
    
    exports = {}
    video_stem = Path(video_path).stem
    
    for aspect in aspect_ratios:
        aspect_name = aspect.replace(":", "x")
        output_path = output_dir / f"{video_stem}_{aspect_name}.mp4"
        
        try:
            smart_crop_portrait(
                video_path, str(output_path),
                target_aspect=aspect,
                tracking_data=tracking_data
            )
            exports[aspect] = str(output_path)
        except Exception as e:
            print(f"Failed to export {aspect}: {e}")
    
    return exports


def add_face_blur(video_path: str, output_path: str,
                 blur_strength: int = 51,
                 tracking_data: Optional[List[Dict]] = None) -> str:
    """
    Blur faces in video (privacy mode)
    
    Args:
        video_path: Path to input video
        output_path: Path to save blurred video
        blur_strength: Blur kernel size (odd number)
        tracking_data: Pre-computed tracking data (optional)
    
    Returns:
        Path to blurred video
    """
    if tracking_data is None:
        tracking_data = track_faces(video_path)
    
    # For now, use a simple approach with OpenCV
    # A full implementation would need frame-by-frame processing
    
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    temp_output = str(Path(output_path).with_suffix('.avi'))
    out = cv2.VideoWriter(temp_output, fourcc, fps, (width, height))
    
    frame_idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Get face data for this frame
        if frame_idx < len(tracking_data):
            frame_data = tracking_data[frame_idx]
            for face in frame_data["faces"]:
                x, y, w, h = face["x"], face["y"], face["width"], face["height"]
                # Extract face region
                face_region = frame[y:y+h, x:x+w]
                if face_region.size > 0:
                    # Apply blur
                    blurred = cv2.GaussianBlur(face_region, (blur_strength, blur_strength), 0)
                    # Replace in frame
                    frame[y:y+h, x:x+w] = blurred
        
        out.write(frame)
        frame_idx += 1
    
    cap.release()
    out.release()
    
    # Convert to final format
    cmd = [
        "ffmpeg", "-y", "-i", temp_output,
        "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
        "-c:a", "copy",
        str(output_path)
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    
    # Cleanup temp file
    Path(temp_output).unlink(missing_ok=True)
    
    return str(output_path)
