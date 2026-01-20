"""
Step 4: Create TiO2-specific LMDB database
Filters downloaded S2EF data to keep only TiO2 systems
"""

import pickle
import lmdb
from pathlib import Path
from tqdm import tqdm


def load_tio2_system_ids():
    """Load TiO2 system IDs"""
    ids_path = Path("data/metadata/tio2_system_ids.txt")
    
    if not ids_path.exists():
        print("Error: TiO2 system IDs not found!")
        print("  Run filter_tio2_systems.py first")
        return None
    
    with open(ids_path, 'r') as f:
        system_ids = set(line.strip() for line in f)
    
    print(f"Loaded {len(system_ids):,} TiO2 system IDs")
    return system_ids


def filter_lmdb(input_path, output_path, tio2_ids):
    """
    Filter LMDB database to keep only TiO2 systems
    
    Args:
        input_path: Path to input LMDB
        output_path: Path to output LMDB
        tio2_ids: Set of TiO2 system IDs
    """
    print(f"\nFiltering: {input_path.name}")
    
    if not input_path.exists():
        print(f"File not found, skipping")
        return 0, 0
    
    # Open input database
    try:
        input_env = lmdb.open(
            str(input_path),
            readonly=True,
            lock=False,
            readahead=False,
            meminit=False,
            max_readers=1
        )
    except Exception as e:
        print(f"Error opening input LMDB: {e}")
        return 0, 0
    
    # Create output database
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_env = lmdb.open(
        str(output_path),
        map_size=1099511627776,  # 1 TB
        subdir=False,
        meminit=False,
        map_async=True
    )
    
    kept_count = 0
    total_count = 0
    
    # Filter entries
    with input_env.begin() as input_txn:
        with output_env.begin(write=True) as output_txn:
            cursor = input_txn.cursor()
            
            for key, value in tqdm(cursor, desc="  Processing"):
                total_count += 1
                
                try:
                    # Load data object
                    data_obj = pickle.loads(value)
                    
                    # Check if system ID is in TiO2 list
                    if hasattr(data_obj, 'sid'):
                        if data_obj.sid in tio2_ids:
                            output_txn.put(key, value)
                            kept_count += 1
                    
                except Exception as e:
                    # Skip corrupted entries
                    continue
    
    # Close databases
    input_env.close()
    output_env.close()
    
    print(f"Kept {kept_count:,} / {total_count:,} entries ({kept_count/total_count*100:.2f}%)")
    
    return kept_count, total_count


def main():
    # Load TiO2 system IDs
    tio2_ids = load_tio2_system_ids()
    if tio2_ids is None:
        return
    
    # Find downloaded S2EF data
    raw_data_dir = Path("data/raw/s2ef")
    
    if not raw_data_dir.exists():
        print(f"\nError: S2EF data not found at {raw_data_dir}")
        print("  Run 03_download_s2ef_data.py first")
        return
    
    # Find all LMDB files
    lmdb_files = list(raw_data_dir.rglob("*.lmdb"))
    
    if not lmdb_files:
        print(f"\nError: No LMDB files found in {raw_data_dir}")
        return
    
    print(f"\nFound {len(lmdb_files)} LMDB files to filter")
    
    # Filter each LMDB file
    total_kept = 0
    total_processed = 0
    
    for lmdb_file in lmdb_files:
        # Determine output path
        rel_path = lmdb_file.relative_to(raw_data_dir)
        output_path = Path("data/tio2") / rel_path
        
        # Filter
        kept, processed = filter_lmdb(lmdb_file, output_path, tio2_ids)
        total_kept += kept
        total_processed += processed
    
    # Summary
    print("\n" + "=" * 60)
    print("Filtering Complete!")
    print("=" * 60)
    print(f"\nTotal entries processed: {total_processed:,}")
    print(f"TiO2 entries kept: {total_kept:,}")
    print(f"Reduction: {(1 - total_kept/total_processed)*100:.1f}%")
    print(f"\nOutput location: data/tio2/")
    print("\nNext step: compute_statistics.py")
    print("=" * 60)


if __name__ == "__main__":
    main()