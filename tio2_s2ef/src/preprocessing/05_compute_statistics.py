"""
Step 5: Compute normalization statistics for TiO2 data
Calculates mean and std for energies and forces
"""

import pickle
import lmdb
import numpy as np
from pathlib import Path
from tqdm import tqdm
import json


def compute_statistics(lmdb_path):
    """
    Compute mean and std for energies and forces
    
    Args:
        lmdb_path: Path to LMDB file
        
    Returns:
        dict: Statistics
    """
    print(f"\nProcessing: {lmdb_path}")
    
    if not lmdb_path.exists():
        print(f"File not found")
        return None
    
    # Open database
    env = lmdb.open(
        str(lmdb_path),
        readonly=True,
        lock=False,
        readahead=False,
        meminit=False,
        max_readers=1
    )
    
    energies = []
    forces_flat = []
    
    # Collect data
    with env.begin() as txn:
        cursor = txn.cursor()
        
        for key, value in tqdm(cursor, desc="  Collecting data"):
            try:
                data = pickle.loads(value)
                
                # Energy
                if hasattr(data, 'y') and data.y is not None:
                    energies.append(float(data.y))
                
                # Forces
                if hasattr(data, 'force') and data.force is not None:
                    forces_flat.extend(data.force.flatten().tolist())
                    
            except Exception:
                continue
    
    env.close()
    
    # Compute statistics
    energies = np.array(energies)
    forces = np.array(forces_flat)
    
    stats = {
        'energy_mean': float(np.mean(energies)),
        'energy_std': float(np.std(energies)),
        'energy_min': float(np.min(energies)),
        'energy_max': float(np.max(energies)),
        'force_mean': float(np.mean(forces)),
        'force_std': float(np.std(forces)),
        'force_min': float(np.min(forces)),
        'force_max': float(np.max(forces)),
        'num_samples': len(energies)
    }
    
    return stats


def main():
    print("=" * 60)
    print("STEP 5: Compute Normalization Statistics")
    print("=" * 60)
    
    # Find TiO2 training LMDB
    train_lmdb = Path("data/tio2")
    lmdb_files = list(train_lmdb.rglob("train*.lmdb"))
    
    if not lmdb_files:
        # Try alternative path
        lmdb_files = list(train_lmdb.rglob("data.lmdb"))
    
    if not lmdb_files:
        print(f"\nError: No LMDB files found in {train_lmdb}")
        print("  Run 04_create_tio2_lmdb.py first")
        return
    
    print(f"\nFound {len(lmdb_files)} LMDB file(s)")
    
    # Compute statistics for each file
    all_stats = {}
    
    for lmdb_file in lmdb_files:
        stats = compute_statistics(lmdb_file)
        if stats:
            all_stats[str(lmdb_file)] = stats
    
    if not all_stats:
        print("\nError: No statistics computed")
        return
    
    # Combine statistics if multiple files
    if len(all_stats) == 1:
        combined_stats = list(all_stats.values())[0]
    else:
        # Weighted average
        total_samples = sum(s['num_samples'] for s in all_stats.values())
        combined_stats = {
            'energy_mean': sum(s['energy_mean'] * s['num_samples'] for s in all_stats.values()) / total_samples,
            'energy_std': np.sqrt(sum(s['energy_std']**2 * s['num_samples'] for s in all_stats.values()) / total_samples),
            'force_mean': sum(s['force_mean'] * s['num_samples'] for s in all_stats.values()) / total_samples,
            'force_std': np.sqrt(sum(s['force_std']**2 * s['num_samples'] for s in all_stats.values()) / total_samples),
            'num_samples': total_samples
        }
    
    # Print statistics
    print("\n" + "=" * 60)
    print("NORMALIZATION STATISTICS")
    print("=" * 60)
    print(f"\nNumber of samples: {combined_stats['num_samples']:,}")
    print("\nEnergy:")
    print(f"  Mean: {combined_stats['energy_mean']:.6f} eV")
    print(f"  Std:  {combined_stats['energy_std']:.6f} eV")
    print("\nForces:")
    print(f"  Mean: {combined_stats['force_mean']:.6f} eV/Å")
    print(f"  Std:  {combined_stats['force_std']:.6f} eV/Å")
    
    # Save statistics
    output_path = Path("data/metadata/tio2_normalization_stats.json")
    with open(output_path, 'w') as f:
        json.dump(combined_stats, f, indent=2)
    
    print(f"\nSaved statistics to: {output_path}")
    
    # Print config values
    print("=" * 60)
    print("\ndataset:")
    print("  train:")
    print(f"    target_mean: {combined_stats['energy_mean']}")
    print(f"    target_std: {combined_stats['energy_std']}")
    print(f"    grad_target_mean: {combined_stats['force_mean']}")
    print(f"    grad_target_std: {combined_stats['force_std']}")
    
    print("\n" + "=" * 60)
    print("Preprocessing Complete!")
    print("=" * 60)
    print("\nYou can now train your model:")
    print("  python scripts/training/train.py --config configs/tio2_schnet.yml")
    print("=" * 60)


if __name__ == "__main__":
    main()