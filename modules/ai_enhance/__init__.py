"""
AI Enhancement Module for Pragya Studio
Provides advanced AI-powered video enhancement features
"""

from .video_enhancer import enhance_video, upscale_video, apply_color_enhancement, apply_hdr_conversion
from .music_generator import generate_background_music, sync_music_to_beats
from .smart_transitions import apply_smart_transition, detect_scene_changes
from .face_tracker import track_faces, smart_crop_portrait, export_multi_aspect

__all__ = [
    'enhance_video',
    'upscale_video', 
    'apply_color_enhancement',
    'apply_hdr_conversion',
    'generate_background_music',
    'sync_music_to_beats',
    'apply_smart_transition',
    'detect_scene_changes',
    'track_faces',
    'smart_crop_portrait',
    'export_multi_aspect'
]
