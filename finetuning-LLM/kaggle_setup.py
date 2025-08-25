#!/usr/bin/env python3
"""
Kaggle Environment Setup for UMPF Equivalency Training
======================================================

This script sets up the Kaggle environment for training the 
Universal Pattern Recognition Engine.

Run this first to install dependencies and prepare the environment.
"""

import subprocess
import sys
import os

def install_packages():
    """Install required packages for UMPF training"""
    packages = [
        "transformers==4.36.0",
        "datasets==2.15.0", 
        "trl==0.7.4",
        "torch>=2.0.0",
        "accelerate>=0.25.0",
        "peft>=0.7.0",
        "bitsandbytes>=0.41.0",
        "scipy>=1.11.0",
        "scikit-learn>=1.3.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0"
    ]
    
    print("=== Installing UMPF Training Dependencies ===")
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {package}: {e}")

def setup_directories():
    """Create necessary directories"""
    dirs = [
        "/kaggle/working/umpf-equivalency-model",
        "/kaggle/working/cache",
        "/kaggle/working/logs"
    ]
    
    print("=== Setting up directories ===")
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✓ Created {dir_path}")

def check_gpu():
    """Check GPU availability"""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"✓ GPU Available: {gpu_name} ({memory:.1f}GB)")
            return True
        else:
            print("⚠ No GPU available, will use CPU (slower)")
            return False
    except ImportError:
        print("⚠ PyTorch not available yet")
        return False

def verify_dataset():
    """Verify the training dataset is available"""
    possible_paths = [
        "/kaggle/input/umpf-training/equivalency-training-pairs.json",
        "/kaggle/working/equivalency-training-pairs.json",
        "./equivalency-training-pairs.json"
    ]
    
    print("=== Checking for training dataset ===")
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✓ Found training data at: {path}")
            return path
    
    print("⚠ Training dataset not found!")
    print("Please upload equivalency-training-pairs.json to Kaggle")
    return None

def main():
    """Setup Kaggle environment for UMPF training"""
    print("🚀 UMPF Equivalency Training - Kaggle Setup")
    print("From Months to Minutes: Scientific Automation")
    print("=" * 50)
    
    # Install packages
    install_packages()
    
    # Setup directories  
    setup_directories()
    
    # Check GPU
    gpu_available = check_gpu()
    
    # Verify dataset
    dataset_path = verify_dataset()
    
    print("\n" + "=" * 50)
    print("📋 Setup Summary:")
    print(f"✓ Dependencies installed")
    print(f"✓ Directories created")
    print(f"{'✓' if gpu_available else '⚠'} GPU: {'Available' if gpu_available else 'Not available'}")
    print(f"{'✓' if dataset_path else '⚠'} Dataset: {'Found' if dataset_path else 'Missing'}")
    
    if dataset_path and gpu_available:
        print("\n🎉 Ready to start UMPF equivalency training!")
        print("Run: python kaggle_equivalency_training.py")
    else:
        print("\n⚠ Setup incomplete. Please check the issues above.")
    
    # Environment info
    print(f"\nPython version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
if __name__ == "__main__":
    main()