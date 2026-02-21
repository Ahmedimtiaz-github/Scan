#!/usr/bin/env python3
"""
Validate end-to-end pipeline outputs.
Usage: python scripts/validate_end_to_end.py <outputs_dir>
Example: python scripts/validate_end_to_end.py outputs/integration_test
Exit 0 on success, 1 on failure.
"""

import argparse
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Validate pipeline outputs")
    parser.add_argument("outputs_dir", nargs="?", default="outputs/integration_test", help="Output directory")
    parser.add_argument("-i", "--input", dest="outputs_dir_alt", help="Input outputs dir (for PS1 -Input)")
    args = parser.parse_args()
    outputs_dir = args.outputs_dir_alt or args.outputs_dir

    if not os.path.isdir(outputs_dir):
        print(f"VALIDATION: FAIL - Directory not found: {outputs_dir}")
        return 1

    errors = []

    # 1. scene/frame_0001.json exists and validates against schema
    scene_json = os.path.join(outputs_dir, "scene", "frame_0001.json")
    if not os.path.exists(scene_json):
        errors.append(f"Missing {scene_json}")
    else:
        try:
            with open(scene_json) as f:
                data = json.load(f)
            schema_path = os.path.join(os.path.dirname(__file__), "..", "docs", "scene_schema.json")
            if os.path.exists(schema_path):
                import jsonschema
                with open(schema_path) as sf:
                    schema = json.load(sf)
                jsonschema.validate(instance=data, schema=schema)
        except Exception as e:
            errors.append(f"Scene JSON invalid: {e}")

    # 2. frame_0001_styled.png exists and size > 100
    styled_path = os.path.join(outputs_dir, "frame_0001_styled.png")
    if not os.path.exists(styled_path):
        errors.append(f"Missing {styled_path}")
    elif os.path.getsize(styled_path) <= 100:
        errors.append(f"{styled_path} too small (<= 100 bytes)")

    # 3. final_video.mp4 OR video_placeholder.txt exists
    video_path = os.path.join(outputs_dir, "final_video.mp4")
    placeholder_path = os.path.join(outputs_dir, "video_placeholder.txt")
    if not os.path.exists(video_path) and not os.path.exists(placeholder_path):
        errors.append(f"Missing {video_path} and {placeholder_path}")

    if errors:
        print("VALIDATION: FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("VALIDATION: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
