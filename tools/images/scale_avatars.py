#!/usr/bin/env python3
"""
Avatar scaling script for the Legend game.

This script scales all avatar images in the avatars directory by a specified ratio.
Usage: python scale_avatars.py <ratio>

Example: python scale_avatars.py 0.25
"""

import sys
import os
from PIL import Image
import glob

def scale_avatars(ratio):
    """
    Scale all avatar images in the avatars directory by the specified ratio.
    
    Args:
        ratio (float): The scaling ratio (e.g., 0.25 for 25% of original size)
    """
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Get the project root directory (parent of tools)
    project_root = os.path.dirname(script_dir)
    # Path to avatars directory
    avatars_dir = os.path.join(project_root, 'resources', 'avatars')
    
    if not os.path.exists(avatars_dir):
        print(f"Error: Avatars directory not found at {avatars_dir}")
        return False
    
    # Find all PNG files in the avatars directory
    avatar_files = glob.glob(os.path.join(avatars_dir, '*.png'))
    
    if not avatar_files:
        print(f"No PNG files found in {avatars_dir}")
        return False
    
    print(f"Found {len(avatar_files)} avatar files to scale by ratio {ratio}")
    
    success_count = 0
    error_count = 0
    
    for avatar_path in avatar_files:
        try:
            # Open the image
            with Image.open(avatar_path) as img:
                # Get original dimensions
                original_width, original_height = img.size
                
                # Calculate new dimensions
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
                
                # Resize the image using high-quality resampling
                scaled_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Save the scaled image (overwrite the original)
                scaled_img.save(avatar_path, 'PNG', optimize=True)
                
                # Get file sizes for reporting
                file_size_before = os.path.getsize(avatar_path)
                
                filename = os.path.basename(avatar_path)
                print(f"✓ Scaled {filename}: {original_width}x{original_height} → {new_width}x{new_height}")
                
                success_count += 1
                
        except Exception as e:
            filename = os.path.basename(avatar_path)
            print(f"✗ Error scaling {filename}: {str(e)}")
            error_count += 1
    
    print(f"\nScaling complete: {success_count} successful, {error_count} errors")
    return error_count == 0

def main():
    """Main entry point for the script."""
    if len(sys.argv) != 2:
        print("Usage: python scale_avatars.py <ratio>")
        print("Example: python scale_avatars.py 0.25")
        sys.exit(1)
    
    try:
        ratio = float(sys.argv[1])
        if ratio <= 0 or ratio > 1:
            print("Error: Ratio must be between 0 and 1 (exclusive of 0)")
            sys.exit(1)
    except ValueError:
        print("Error: Ratio must be a valid number")
        sys.exit(1)
    
    # Check if PIL is available
    try:
        from PIL import Image
    except ImportError:
        print("Error: PIL (Pillow) is required but not installed.")
        print("Install it with: pip install Pillow")
        sys.exit(1)
    
    success = scale_avatars(ratio)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()