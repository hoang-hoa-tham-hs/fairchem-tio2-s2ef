"""
Step 1: Download OC20 metadata file
This file contains information about all systems in the OC20 dataset
"""

import urllib.request
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.path_config import DataPath, DownloadURLs

def download_metadata():
    """Download OC20 data mapping file"""
    # Create metadata directory
    DataPath.METADATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check if already exists
    if DataPath.OC22_MAPPING_FILE.exists():
        print(f"\nMetadata file already exists: {DataPath.OC22_MAPPING_FILE}")
        print(f"File size: {DataPath.OC22_MAPPING_FILE.stat().st_size / 1024:.2f} KB")
        
        user_input = input("\nDo you want to re-download? (y/n): ").lower()
        if user_input != 'y':
            print("Skipping download.")
            return
        
        DataPath.OC22_MAPPING_FILE.unlink()
    
    # Download
    print(f"\nDownloading from: {DownloadURLs.OC22_METADATA_URL}")
    print(f"Saving to: {DataPath.OC22_MAPPING_FILE}")
    
    try:
        urllib.request.urlretrieve(
            DownloadURLs.OC22_METADATA_URL,
            DataPath.OC22_MAPPING_FILE
        )
        print(f"\nDownload successful!")
        print(f"File size: {DataPath.OC22_MAPPING_FILE.stat().st_size / 1024:.2f} KB")
        print(f"Location: {DataPath.OC22_MAPPING_FILE.absolute()}")
        
    except Exception as e:
        print(f"\nError downloading file: {e}")
        sys.exit(1)



if __name__ == "__main__":
    print("=" * 60)
    print(f"STEP 2: Download OC20 Metadata File")

    download_metadata()

    print("\nFinishing OC20 Metadata Download")
    print(f"{'=' * 60}")