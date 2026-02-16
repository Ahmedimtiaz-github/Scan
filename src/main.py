#!/usr/bin/env python3
"""
src/main.py

CLI entrypoint for the AI Room Scan pipeline (Ahmed's integration entry).
Usage example:
    python -m src.main --mode image --preset fast --input "samples/input.jpg" --output outputs
"""
import argparse
import logging
import os
from src.config import PRESETS
from src.orchestrator import run_pipeline

def parse_args():
    parser = argparse.ArgumentParser(description="AI Room Scan - orchestration entrypoint")
    parser.add_argument("--mode", choices=["image","video"], required=True, help="image or video input")
    parser.add_argument("--preset", choices=["fast","balanced","quality"], default="fast", help="resource preset")
    parser.add_argument("--input", required=True, help="path to input image, video, or input folder")
    parser.add_argument("--output", default="outputs", help="output directory")
    return parser.parse_args()

def main():
    args = parse_args()
    os.makedirs(args.output, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    logging.info(f"Starting pipeline mode={args.mode} preset={args.preset} input={args.input}")
    run_pipeline(mode=args.mode, preset=args.preset, input_path=args.input, output_dir=args.output)

if __name__ == "__main__":
    main()
