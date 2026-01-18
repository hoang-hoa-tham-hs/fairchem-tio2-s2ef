"""
Step 3: Download S2EF dataset from OC20
Uses FAIRChem's download script to get trajectory data
"""

import os
import sys
import subprocess
from pathlib import Path
import tarfile
import urllib.request
from tqdm import tqdm

# Add root directory to path to import local scripts
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts import preprocess_ef

from tio2_s2ef.scripts.path_config import DataPath, S2EFDataPath, DownloadURLs

# Helpers for download process
class DownloadProgressBar(tqdm):
    """Progress bar for downloads"""
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_file(url, output_path):
    """Download file with progress bar"""
    print(f"Downloading: {url}")
    print(f"To: {output_path}")
    
    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1) as t:
        urllib.request.urlretrieve(url, output_path, reporthook=t.update_to)
    
    print(f"Downloaded: {output_path.stat().st_size / (1024**3):.2f} GB")

def extract_tar(tar_path, extract_to):
    """Extract tar file with progress bar"""
    print(f"\nExtracting: {tar_path.name}")
    
    with tarfile.open(tar_path, 'r') as tar:
        members = tar.getmembers()
        
        for member in tqdm(members, desc="Extracting"):
            tar.extract(member, path=extract_to)
    
    print(f"Extracted to: {extract_to}")

def download_s2ef_data(split="200k"):
    """
    Download S2EF dataset
    
    Args:
        split: "200k", "2M", "20M", or "all"
    """
    
    print("=" * 60)
    print(f"STEP 3: Download S2EF Dataset (Split: {split})")
    print("=" * 60)
    
    # Dataset sizes (approximate)
    sizes = {
        "200k": {"train": 1.7, "val": 4},
        "2M": {"train": 17, "val": 4},
        "20M": {"train": 165, "val": 4},
        "all": {"train": 1100, "val": 4}
    }
    
    if split not in sizes:
        print(f"Error: Invalid split '{split}'")
        print(f"Valid options: {list(sizes.keys())}")
        return
    
    # Show size warning
    total_size = sum(sizes[split].values())
    print(f"\nTotal download size: ~{total_size} GB")
    print(f"  Training: ~{sizes[split]['train']} GB")
    # print(f"  Validation: ~{sizes[split]['val']} GB")
    
    response = input("\nContinue? (y/n): ").lower()
    if response != 'y':
        print("Download cancelled.")
        return
    
    # Create directories
    DataPath.RAW_DIR.mkdir(parents=True, exist_ok=True)
    DataPath.RAW_S2EF_DIR.mkdir(parents=True, exist_ok=True)
    
    # Download and extract each dataset
    # for dataset_type in ["train", "val"]:
    for dataset_type in ["train"]:
        # Get paths
        url = DownloadURLs.get_s2ef_url(split, dataset_type)
        tar_path = S2EFDataPath.get_tar_file(split, dataset_type)
        extract_path = S2EFDataPath.get_split_dir(split, dataset_type)
        
        # Check if already downloaded
        if tar_path.exists():
            print(f"\n{tar_path.name} already exists.")
            response = input("Re-download? (y/n): ").lower()
            if response != 'y':
                print("Skipping download.")
            else:
                tar_path.unlink()
                download_file(url, tar_path)
        else:
            # Download
            print(f"\n{'=' * 60}")
            print(f"Downloading {dataset_type.upper()} data...")
            print(f"{'=' * 60}")
            download_file(url, tar_path)
        
        # Extract
        print(f"\n{'=' * 60}")
        print(f"Extracting {dataset_type.upper()} data...")
        print(f"{'=' * 60}")
        
        extract_path.mkdir(parents=True, exist_ok=True)
        extract_tar(tar_path, extract_path)
        
        # Verify extraction
        txt_files = list(extract_path.rglob("*.txt"))
        print(f"Found {len(txt_files)} .txt files")
        
        if len(txt_files) == 0:
            print("Warning: No .txt files found after extraction!")
            print("The archive structure might be different.")
            print(f"Contents of {extract_path}:")
            for item in extract_path.iterdir():
                print(f"  - {item.name}")
    
    # Preprocess to LMDB
    print(f"\n{'=' * 60}")
    print("Preprocessing data to LMDB format...")
    print(f"{'=' * 60}")
    
    try:
        from fairchem.core.scripts import preprocess_ef
        
        # for dataset_type in ["train", "val"]:
        for dataset_type in ["train"]:
            extract_path = S2EFDataPath.get_split_dir(split, dataset_type)
            output_path = S2EFDataPath.get_split_lmdb(split, dataset_type)
            
            # Check if .txt files exist
            txt_files = list(extract_path.rglob("*.txt"))
            
            if len(txt_files) == 0:
                print(f"\nSkipping preprocessing for {dataset_type} - no .txt files found")
                print(f"Looking in: {extract_path}")
                continue
            
            print(f"\nPreprocessing {dataset_type} data...")
            print(f"  Input: {extract_path}")
            print(f"  Output: {output_path}")
            print(f"  Files to process: {len(txt_files)}")
            
            # Create args for preprocessing
            class Args:
                data_path = str(extract_path)
                out_path = str(output_path)
                get_edges = True
                num_workers = 4
                ref_energy = True
            
            args = Args()
            
            try:
                preprocess_ef.main(args)
                print(f"Preprocessed {dataset_type} data to LMDB")
            except Exception as e:
                print(f"Error preprocessing {dataset_type}: {e}")
                print("You may need to preprocess manually later.")
    
    except ImportError:
        print("\nCould not import preprocessing script")
        print("You'll need to preprocess manually")
    
    print(f"\n{'=' * 60}")
    print("Download Complete!")
    print(f"\nData location: {DataPath.RAW_S2EF_DIR.absolute()}")
    print(f"{'=' * 60}")

def main():
    # Chose split to download (https://github.com/facebookresearch/fairchem/blob/main/src/fairchem/core/scripts/download_data.py)
    print("\nAvailable dataset splits:")
    print("  1. 200k  - ~1.7G")
    print("  2. 2M    - ~17G")
    print("  3. 20M   - ~165G")
    print("  4. all   - ~1.1 T")
    
    choice = input("\nEnter choice (1-4) [default: 1]: ").strip()
    
    split_map = {
        "1": "200k",
        "2": "2M",
        "3": "20M",
        "4": "all",
        "": "200k"
    }
    
    split = split_map.get(choice, "200k")
    download_s2ef_data(split)


if __name__ == "__main__":
    main()