"""
ClaudyKey Bundle Builder - Phase 2
===================================
Called by build_bundle.bat AFTER Python embeddable is already set up in env/.
This script installs PyTorch, EasyOCR, and all other pip packages.
"""
import os
import sys
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_DIR = os.path.join(SCRIPT_DIR, "env")
PYTHON = os.path.join(ENV_DIR, "python.exe")

# Change to "cu118" for CUDA 11.8
CUDA_TAG = "cu121"


def run(args):
    print(f"  > {' '.join(args)}")
    r = subprocess.run(args)
    if r.returncode != 0:
        print(f"\n[ERROR] Command failed (exit {r.returncode})")
        input("Press Enter to exit...")
        sys.exit(1)


def main():
    if not os.path.exists(PYTHON):
        print(f"[ERROR] {PYTHON} not found!")
        input("Press Enter to exit...")
        sys.exit(1)

    print()
    print("=" * 56)
    print(f"  Installing packages (CUDA: {CUDA_TAG})")
    print("=" * 56)
    print()

    print("[1/3] Installing PyTorch (large, ~2.5GB)...")
    run([PYTHON, "-m", "pip", "install",
         "torch", "torchvision",
         "--index-url", f"https://download.pytorch.org/whl/{CUDA_TAG}",
         "--no-warn-script-location"])

    print()
    print("[2/3] Installing other packages...")
    run([PYTHON, "-m", "pip", "install",
         "PyQt6>=6.6", "mss", "opencv-python",
         "easyocr>=1.7", "pynput", "numpy", "Pillow",
         "--no-warn-script-location"])

    print()
    print("[3/3] Pre-downloading EasyOCR models (~200MB)...")
    run([PYTHON, "-c",
         "import easyocr; easyocr.Reader(['ch_sim','en'], gpu=True, verbose=False); print('Models ready!')"])

    print()
    print("=" * 56)
    print("  BUILD COMPLETE!")
    print()
    print("  Launch:  double-click ClaudyKey.bat")
    print("  Share:   zip the entire claudykey folder")
    print("=" * 56)
    print()


if __name__ == "__main__":
    main()
