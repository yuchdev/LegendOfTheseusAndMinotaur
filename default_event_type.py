#!/usr/bin/env python3
"""
Default Event Type script for the Legend game.

This script iterates over all JSON files and all events in each file,
adding the property "event_type": "dialogue" to each event.

Usage: python default_event_type.py
"""

import os
import json
import glob
from typing import List, Dict, Any

def find_json_files() -> List[str]:
    """
    Find all JSON files in the project.
    
    Returns:
        List[str]: List of JSON file paths
    """
    json_files = []
    
    # Look for JSON files in common directories
    search_patterns = [
        "*.json",
        "scripted_events/*.json",
        "play_chapters/*.json",
        "raw/*.json"
    ]
    
    for pattern in search_patterns:
        files = glob.glob(pattern)
        json_files.extend(files)
    
    # Remove duplicates and sort
    json_files = sorted(list(set(json_files)))
    
    return json_files

def process_json_file(file_path: str) -> bool:
    """
    Process a single JSON file, adding event_type property to all events.
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        bool: True if file was processed successfully, False otherwise
    """
    try:
        # Read the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if the data is a list (array of events)
        if not isinstance(data, list):
            print(f"Skipping {file_path}: Not an array of events")
            return False
        
        # Track if any changes were made
        changes_made = False
        
        # Process each event in the file
        for i, event in enumerate(data):
            if isinstance(event, dict):
                # Check if event_type already exists
                if "event_type" not in event:
                    event["event_type"] = "dialogue"
                    changes_made = True
                    print(f"  Added event_type to event {i+1}")
                else:
                    print(f"  Event {i+1} already has event_type: {event['event_type']}")
            else:
                print(f"  Warning: Event {i+1} is not a dictionary object")
        
        # Write back the modified data if changes were made
        if changes_made:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✓ Updated {file_path} with {sum(1 for event in data if isinstance(event, dict) and event.get('event_type') == 'dialogue')} events")
        else:
            print(f"✓ No changes needed for {file_path}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"✗ Error parsing JSON in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")
        return False

def main():
    """Main entry point for the script."""
    print("Default Event Type Script")
    print("=" * 40)
    
    # Find all JSON files
    json_files = find_json_files()
    
    if not json_files:
        print("No JSON files found in the project.")
        return
    
    print(f"Found {len(json_files)} JSON files:")
    for file_path in json_files:
        print(f"  - {file_path}")
    
    print("\nProcessing files...")
    print("-" * 40)
    
    # Process each file
    success_count = 0
    total_events = 0
    
    for file_path in json_files:
        print(f"\nProcessing: {file_path}")
        
        if process_json_file(file_path):
            success_count += 1
            
            # Count events in this file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    file_events = len([event for event in data if isinstance(event, dict)])
                    total_events += file_events
                    print(f"  File contains {file_events} events")
            except:
                pass
    
    print("\n" + "=" * 40)
    print("Summary:")
    print(f"✓ Successfully processed {success_count}/{len(json_files)} files")
    print(f"✓ Total events processed: {total_events}")
    print("\nAll events now have 'event_type': 'dialogue' property!")

if __name__ == "__main__":
    main()