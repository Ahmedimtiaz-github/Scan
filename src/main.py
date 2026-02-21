"""
CLI entrypoint for AI Room Scan & Interior Styling pipeline.
"""

import argparse
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)


def main():
    parser = argparse.ArgumentParser(
        description="AI Room Scan & Interior Styling (CPU-optimized)"
    )
    parser.add_argument(
        "--mode",
        choices=["image", "video"],
        default="image",
        help="Input mode: image or video",
    )
    parser.add_argument(
        "--preset",
        choices=["fast", "balanced", "quality"],
        default="fast",
        help="Quality preset (fast=512x512 20 steps, balanced=768 25, quality=1024 40)",
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to input image or video",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="outputs/integration_test",
        help="Output directory (default: outputs/integration_test)",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=1.0,
        help="Frame sampling rate for video mode (default: 1.0)",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=10,
        help="Max keyframes for video mode (default: 10)",
    )

    args = parser.parse_args()

    # Defer heavy import until after --help (avoids loading torch etc.)
    from src.orchestrator import run

    run(
        mode=args.mode,
        preset=args.preset,
        input_path=args.input,
        output_dir=args.output,
        fps=args.fps,
        max_frames=args.max_frames,
    )


if __name__ == "__main__":
    main()
