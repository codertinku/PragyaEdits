#!/usr/bin/env python3
"""
Simple validation script for AI enhancement modules.
This checks the module structure without requiring all dependencies.
"""

import sys
import ast
from pathlib import Path

def check_file_syntax(filepath):
    """Check if a Python file has valid syntax."""
    try:
        with open(filepath, 'r') as f:
            ast.parse(f.read())
        return True, None
    except SyntaxError as e:
        return False, str(e)

def main():
    print("🔍 Validating AI Enhancement Modules...")
    
    base_dir = Path(__file__).parent
    ai_enhance_dir = base_dir / "modules" / "ai_enhance"
    
    if not ai_enhance_dir.exists():
        print("❌ modules/ai_enhance/ directory not found!")
        return 1
    
    # Check all Python files
    python_files = [
        ai_enhance_dir / "__init__.py",
        ai_enhance_dir / "video_enhancer.py",
        ai_enhance_dir / "music_generator.py",
        ai_enhance_dir / "smart_transitions.py",
        ai_enhance_dir / "face_tracker.py",
    ]
    
    all_valid = True
    for filepath in python_files:
        if not filepath.exists():
            print(f"❌ {filepath.name} not found!")
            all_valid = False
            continue
        
        valid, error = check_file_syntax(filepath)
        if valid:
            print(f"✅ {filepath.name} - Valid syntax")
        else:
            print(f"❌ {filepath.name} - Syntax error: {error}")
            all_valid = False
    
    # Check main files
    main_files = [
        base_dir / "main.py",
        base_dir / "streamlit_app_pragya.py",
        base_dir / "config.yaml",
    ]
    
    for filepath in main_files:
        if not filepath.exists():
            print(f"❌ {filepath.name} not found!")
            all_valid = False
        else:
            if filepath.suffix == ".py":
                valid, error = check_file_syntax(filepath)
                if valid:
                    print(f"✅ {filepath.name} - Valid syntax")
                else:
                    print(f"❌ {filepath.name} - Syntax error: {error}")
                    all_valid = False
            else:
                print(f"✅ {filepath.name} - Exists")
    
    if all_valid:
        print("\n✅ All validations passed!")
        return 0
    else:
        print("\n❌ Some validations failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
