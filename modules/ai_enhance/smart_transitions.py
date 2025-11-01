"""
Smart Transitions Module
Provides AI-powered cinematic transitions with scene-aware selection
"""

import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import cv2
import numpy as np


def detect_scene_changes(video_path: str, threshold: float = 30.0) -> List[float]:
    """
    Detect scene changes in video using content analysis
    
    Args:
        video_path: Path to video file
        threshold: Scene change detection threshold
    
    Returns:
        List of scene change timestamps in seconds
    """
    from scenedetect import detect, ContentDetector
    
    # Detect scenes
    scene_list = detect(video_path, ContentDetector(threshold=threshold))
    
    # Extract timestamps
    timestamps = []
    for scene in scene_list:
        timestamps.append(scene[0].get_seconds())
    
    return timestamps


def analyze_scene_content(video_path: str, timestamp: float) -> Dict:
    """
    Analyze scene content to determine best transition type
    
    Args:
        video_path: Path to video file
        timestamp: Timestamp to analyze
    
    Returns:
        Scene characteristics dictionary
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_number = int(timestamp * fps)
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        return {"brightness": 0.5, "motion": "medium", "type": "neutral"}
    
    # Analyze brightness
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray) / 255.0
    
    # Simple scene classification based on brightness
    if brightness < 0.3:
        scene_type = "dark"
    elif brightness > 0.7:
        scene_type = "bright"
    else:
        scene_type = "neutral"
    
    return {
        "brightness": brightness,
        "motion": "medium",  # Would need temporal analysis for accurate motion
        "type": scene_type
    }


def get_transition_for_scene(scene_info: Dict, transition_style: str = "auto") -> str:
    """
    Select appropriate transition based on scene characteristics
    
    Args:
        scene_info: Scene analysis results
        transition_style: Transition style preference (auto, cinematic, smooth, dynamic)
    
    Returns:
        FFmpeg xfade transition name
    """
    if transition_style == "cinematic":
        transitions = ["fade", "wipeleft", "wiperight", "slideleft", "slideright"]
    elif transition_style == "smooth":
        transitions = ["fade", "dissolve", "pixelize"]
    elif transition_style == "dynamic":
        transitions = ["circleopen", "circleclose", "squeezev", "squeezeh", "radial"]
    else:  # auto
        # Select based on scene brightness
        brightness = scene_info.get("brightness", 0.5)
        if brightness < 0.3:
            transitions = ["fade", "dissolve"]
        elif brightness > 0.7:
            transitions = ["wipeleft", "wiperight", "slideleft"]
        else:
            transitions = ["fade", "circleopen", "radial"]
    
    # Return first transition (could be randomized)
    return transitions[0]


def apply_transition_between_clips(clip1_path: str, clip2_path: str, 
                                  output_path: str, transition: str = "fade",
                                  duration: float = 0.5) -> str:
    """
    Apply transition between two video clips
    
    Args:
        clip1_path: Path to first clip
        clip2_path: Path to second clip
        output_path: Path to save output
        transition: Transition type
        duration: Transition duration in seconds
    
    Returns:
        Path to output video
    """
    # Use xfade filter for transitions
    filter_complex = (
        f"[0:v][1:v]xfade=transition={transition}:duration={duration}:offset=0[v];"
        f"[0:a][1:a]acrossfade=d={duration}[a]"
    )
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(clip1_path),
        "-i", str(clip2_path),
        "-filter_complex", filter_complex,
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "128k",
        str(output_path)
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    return str(output_path)


def apply_smart_transition(clips: List[str], output_path: str,
                          transition_style: str = "auto",
                          transition_duration: float = 0.5,
                          analyze_scenes: bool = True) -> str:
    """
    Apply smart transitions to a list of video clips
    
    Args:
        clips: List of video clip paths
        output_path: Path to save final video
        transition_style: Transition style (auto, cinematic, smooth, dynamic)
        transition_duration: Duration of each transition
        analyze_scenes: Enable scene-aware transition selection
    
    Returns:
        Path to final video with transitions
    """
    if len(clips) < 2:
        # No transitions needed, just copy
        if clips:
            subprocess.run(["cp", clips[0], output_path], check=True)
        return str(output_path)
    
    temp_dir = Path(output_path).parent / "temp_transitions"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Process clips with transitions
    current_output = clips[0]
    
    for i in range(1, len(clips)):
        # Analyze scene if enabled
        if analyze_scenes:
            scene_info = analyze_scene_content(clips[i], 0.1)
            transition = get_transition_for_scene(scene_info, transition_style)
        else:
            transition = "fade" if transition_style == "smooth" else "circleopen"
        
        temp_output = str(temp_dir / f"merged_{i}.mp4")
        
        # Apply transition
        apply_transition_between_clips(
            current_output, clips[i], temp_output,
            transition=transition, duration=transition_duration
        )
        
        current_output = temp_output
    
    # Copy final result
    subprocess.run(["cp", current_output, output_path], check=True)
    
    # Cleanup temp files
    import shutil
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    return str(output_path)


def get_available_transitions() -> List[str]:
    """
    Get list of available transition effects
    
    Returns:
        List of transition names
    """
    return [
        "fade", "fadeblack", "fadewhite", "distance", "wipeleft", "wiperight",
        "wipeup", "wipedown", "slideleft", "slideright", "slideup", "slidedown",
        "smoothleft", "smoothright", "smoothup", "smoothdown", "circlecrop",
        "rectcrop", "circleclose", "circleopen", "horzclose", "horzopen",
        "vertclose", "vertopen", "diagbl", "diagbr", "diagtl", "diagtr",
        "hlslice", "hrslice", "vuslice", "vdslice", "dissolve", "pixelize",
        "radial", "hblur", "fadegrays", "squeezeh", "squeezev", "zoomin"
    ]


def create_transition_demo(clip_path: str, output_dir: str, 
                          transitions: Optional[List[str]] = None) -> List[str]:
    """
    Create demo videos showing different transitions
    
    Args:
        clip_path: Path to sample clip
        output_dir: Directory to save demos
        transitions: List of transitions to demo (None = all)
    
    Returns:
        List of demo video paths
    """
    if transitions is None:
        transitions = ["fade", "circleopen", "wipeleft", "dissolve", "radial"]
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    demo_paths = []
    
    for transition in transitions:
        output_path = output_dir / f"transition_demo_{transition}.mp4"
        try:
            # Create transition using same clip twice for demo
            apply_transition_between_clips(
                clip_path, clip_path, str(output_path),
                transition=transition, duration=1.0
            )
            demo_paths.append(str(output_path))
        except Exception:
            continue
    
    return demo_paths
