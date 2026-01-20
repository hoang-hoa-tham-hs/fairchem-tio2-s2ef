"""
Step 3: Download S2EF dataset from OC20
Uses FAIRChem's download script to get trajectory data
"""

import os
import sys
import tarfile
import urllib.request
from pathlib import Path
from tqdm import tqdm

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tio2_s2ef.src.path_config import DataPath, DownloadURLs


class DownloadProgressBar(tqdm):
    """Progress bar for downloads"""
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_file(url, output_path):
    """Download file with progress bar"""
    print(f"Downloading to: {output_path}")
    
    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc="Downloading") as t:
        urllib.request.urlretrieve(url, output_path, reporthook=t.update_to)
    
    size_gb = output_path.stat().st_size / (1024**3)
    print(f"Downloaded: {size_gb:.2f} GB")


def extract_tar(tar_path, extract_to):
    """Extract tar file with progress bar"""
    print(f"Extracting: {tar_path.name}")
    
    with tarfile.open(tar_path, 'r') as tar:
        members = tar.getmembers()
        for member in tqdm(members, desc="Extracting"):
            tar.extract(member, path=extract_to)
    
    print(f"Extracted to: {extract_to}")


def download_and_uncompress_s2ef(split="200k"):
    """
    Download and uncompress S2EF dataset
    
    Args:
        split: "200k", "2M", "20M", or "all"
    """
    
    # Dataset sizes (approximate)
    sizes = {
        "200k": 1.7,
        "2M": 17,
        "20M": 165,
        "all": 1100
    }
    
    if split not in sizes:
        print(f"Error: Invalid split '{split}'. Valid options: {list(sizes.keys())}")
        return
    
    print(f"Download size: ~{sizes[split]} GB")
    response = input("Continue? (y/n): ").lower()
    if response != 'y':
        return
    
    # Create directories
    DataPath.RAW_DIR.mkdir(parents=True, exist_ok=True)
    DataPath.RAW_S2EF_DIR.mkdir(parents=True, exist_ok=True)
    
    # Get paths
    url = DownloadURLs.get_s2ef_url(split, "train")
    tar_filename = f"s2ef_train_{split.upper()}.tar"
    tar_path = DataPath.RAW_DIR / tar_filename
    
    # Download
    if tar_path.exists():
        print(f"{tar_filename} exists.")
        response = input("Re-download? (y/n): ").lower()
        if response == 'y':
            tar_path.unlink()
            download_file(url, tar_path)
    else:
        download_file(url, tar_path)
    
    # Extract tar
    print("\nExtracting tar file...")
    extract_tar(tar_path, DataPath.RAW_DIR)
    
    # Find compressed directory
    compressed_base = DataPath.RAW_DIR / f"s2ef_train_{split.upper()}"
    compressed_dir = compressed_base / f"s2ef_train_{split.upper()}"
    
    if not compressed_dir.exists():
        # Try to find .xz files in subdirectories
        possible_dirs = list(compressed_base.rglob("*.xz"))
        if possible_dirs:
            compressed_dir = possible_dirs[0].parent
        else:
            print(f"Error: Could not find compressed files in {compressed_base}")
            print("Contents:")
            for item in compressed_base.rglob("*"):
                print(f"  {item.relative_to(compressed_base)}")
            return
    
    xz_files = list(compressed_dir.glob("*.xz"))
    print(f"\nFound {len(xz_files)} compressed files in {compressed_dir}")
    
    # Uncompress
    print("\nUncompressing data...")
    uncompressed_dir = DataPath.RAW_S2EF_DIR / split / "train_uncompressed"
    uncompressed_dir.mkdir(parents=True, exist_ok=True)
    
    # Import here to avoid circular imports
    from scripts.uncompress import main as uncompress_main
    
    class UncompressArgs:
        ipdir = str(compressed_dir)
        opdir = str(uncompressed_dir)
        num_workers = 8
    
    uncompress_main(UncompressArgs())
    
    # Verify
    txt_files = list(uncompressed_dir.glob("*.txt"))
    extxyz_files = list(uncompressed_dir.glob("*.extxyz"))
    print(f"\nUncompressed: {len(txt_files)} .txt, {len(extxyz_files)} .extxyz files")
    
    if len(txt_files) == 0 or len(extxyz_files) == 0:
        print("Warning: Missing expected files!")
        return
    
    # Cleanup
    print()
    response = input("Delete compressed files to save space? (y/n): ").lower()
    if response == 'y':
        import shutil
        if tar_path.exists():
            tar_path.unlink()
            print(f"Deleted: {tar_path.name}")
        if compressed_base.exists():
            shutil.rmtree(compressed_base)
            print(f"Deleted: {compressed_base.name}")
    
    print(f"\nData location: {uncompressed_dir.absolute()}")

if __name__ == "__main__":
    print("=" * 60)
    print(f"STEP 3: Download & Uncompress S2EF Dataset")

    # Chose split to download (https://github.com/facebookresearch/fairchem/blob/main/src/fairchem/core/scripts/download_data.py)
    print("\nAvailable splits:")
    print("  1. 200k  - ~1.7 GB")
    print("  2. 2M    - ~17 GB")
    print("  3. 20M   - ~165 GB")
    print("  4. all   - ~1.1 TB")
    
    choice = input("\nEnter choice (1-4) [default: 1]: ").strip()
    
    split_map = {"1": "200k", "2": "2M", "3": "20M", "4": "all", "": "200k"}
    split = split_map.get(choice, "200k")
    
    download_and_uncompress_s2ef(split)

    print("Download and Uncompress Complete!")
    print(f"{'=' * 60}")