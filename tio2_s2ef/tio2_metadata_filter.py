import pickle
import json
import re
from fractions import Fraction

def parse_formula(bulk_symbols):
    """
    Parse chemical formula and return element counts
    Example: "Ti12O4" -> {'Ti': 12, 'O': 4}
    """
    elements = {}
    pattern = r'([A-Z][a-z]?)(\d*)'
    matches = re.findall(pattern, bulk_symbols)
    
    for element, count in matches:
        if element:
            count = int(count) if count else 1
            elements[element] = count
    
    return elements

def is_tio2(bulk_symbols):
    """
    Check if bulk_symbols represents TiO2 stoichiometry (Ti:O ratio = 1:2)
    """
    elements = parse_formula(bulk_symbols)
    
    # Check if it's only Ti and O (no other elements)
    if set(elements.keys()) != {'Ti', 'O'}:
        return False
    
    # Check Ti:O ratio = 1:2
    ti_count = elements.get('Ti', 0)
    o_count = elements.get('O', 0)
    
    if ti_count == 0 or o_count == 0:
        return False
    
    # Reduce the ratio
    ratio = Fraction(ti_count, o_count)
    
    # TiO2 should have Ti:O = 1:2
    return ratio == Fraction(1, 2)

def load_and_filter_tio2_metadata(pkl_file_path, output_json_path='oc22_tio2_metadata.json'):
    """
    Load oc22_metadata.pkl, filter for TiO2 only (1:2 ratio), and save to JSON
    
    Args:
        pkl_file_path: Path to the oc22_metadata.pkl file
        output_json_path: Path where to save the filtered JSON file
    """
    
    print(f"Loading {pkl_file_path}...")
    
    # Load the pickle file
    with open(pkl_file_path, 'rb') as f:
        oc22_metadata = pickle.load(f)
    
    print(f"Loaded successfully!")
    print(f"Total systems in OC22: {len(oc22_metadata)}")
    
    # Filter for TiO2 only
    print("\nFiltering for TiO2 systems (Ti:O ratio = 1:2)...")
    
    tio2_metadata = {}
    tio2_slab_only = {}
    tio2_adslab = {}
    
    for system_id, info in oc22_metadata.items():
        bulk_symbols = info.get('bulk_symbols', '')
        
        if is_tio2(bulk_symbols):
            tio2_metadata[system_id] = info
            
            # Separate slab-only vs adsorbate+slab
            if 'ads_symbols' in info and info.get('nads', 0) > 0:
                tio2_adslab[system_id] = info
            else:
                tio2_slab_only[system_id] = info
    
    print(f"\n{'='*80}")
    print(f"FILTERING RESULTS:")
    print(f"{'='*80}")
    print(f"Total TiO2 systems found: {len(tio2_metadata)}")
    print(f"  - Clean TiO2 slabs (no adsorbates): {len(tio2_slab_only)}")
    print(f"  - TiO2 + adsorbates: {len(tio2_adslab)}")
    
    # Analyze the TiO2 data
    if tio2_metadata:
        print(f"\n{'='*80}")
        print(f"TiO2 DATASET ANALYSIS:")
        print(f"{'='*80}")
        
        # Analyze surface orientations
        surfaces = {}
        for info in tio2_metadata.values():
            miller = tuple(info['miller_index'])
            surfaces[miller] = surfaces.get(miller, 0) + 1
        
        print(f"\nSurface orientations (Miller indices):")
        for miller, count in sorted(surfaces.items(), key=lambda x: x[1], reverse=True):
            print(f"  {miller}: {count} systems")
        
        # Analyze adsorbates
        if tio2_adslab:
            adsorbates = {}
            for info in tio2_adslab.values():
                ads = info.get('ads_symbols', 'N/A')
                adsorbates[ads] = adsorbates.get(ads, 0) + 1
            
            print(f"\nAdsorbates on TiO2:")
            for ads, count in sorted(adsorbates.items(), key=lambda x: x[1], reverse=True):
                print(f"  {ads}: {count} systems")
        
        # Analyze bulk formulas
        bulk_formulas = {}
        for info in tio2_metadata.values():
            formula = info.get('bulk_symbols', 'N/A')
            bulk_formulas[formula] = bulk_formulas.get(formula, 0) + 1
        
        print(f"\nTiO2 stoichiometries found:")
        for formula, count in sorted(bulk_formulas.items(), key=lambda x: x[1], reverse=True):
            elements = parse_formula(formula)
            print(f"  {formula} (Ti:{elements.get('Ti', 0)}, O:{elements.get('O', 0)}): {count} systems")
        
        # Show example entries
        print(f"\n{'='*80}")
        print(f"EXAMPLE TiO2 ENTRIES:")
        print(f"{'='*80}")
        
        # Example clean slab
        if tio2_slab_only:
            example_slab_id = list(tio2_slab_only.keys())[0]
            print(f"\nExample Clean TiO2 Slab (System ID: {example_slab_id}):")
            for key, value in tio2_slab_only[example_slab_id].items():
                print(f"  {key}: {value}")
        
        # Example adsorbate+slab
        if tio2_adslab:
            example_adslab_id = list(tio2_adslab.keys())[0]
            print(f"\nExample TiO2 + Adsorbate (System ID: {example_adslab_id}):")
            for key, value in tio2_adslab[example_adslab_id].items():
                print(f"  {key}: {value}")
    else:
        print("\n⚠ WARNING: No TiO2 systems found!")
        print("This could mean:")
        print("  1. The pickle file doesn't contain TiO2 data")
        print("  2. The bulk_symbols format is different than expected")
        print("  3. TiO2 might be labeled differently in this dataset")
        return None
    
    # Convert to JSON-compatible format
    print(f"\n{'='*80}")
    print(f"Saving to JSON...")
    print(f"{'='*80}")
    
    json_data = {}
    for system_id, info in tio2_metadata.items():
        json_data[str(system_id)] = {}
        for key, value in info.items():
            # Convert tuples to lists for JSON compatibility
            if isinstance(value, tuple):
                json_data[str(system_id)][key] = list(value)
            else:
                json_data[str(system_id)][key] = value
    
    # Save as JSON
    with open(output_json_path, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"\n✓ Successfully saved {len(json_data)} TiO2 systems to {output_json_path}")
    
    return json_data

if __name__ == "__main__":
    # Example usage
    pkl_file = r"D:\Train_thử\fairchem-tio2-s2ef\tio2_s2ef\data\metadata\oc22_metadata.pkl"
    output_file = r"D:\Train_thử\fairchem-tio2-s2ef\tio2_s2ef\oc22_tio2_metadata.json"
    
    # Load and save
    tio2_data = load_and_filter_tio2_metadata(pkl_file, output_file)
    
    if tio2_data:
        print("\n" + "="*80)
        print("DONE! ✓")
        print("="*80)
        print(f"You can now use the filtered TiO2 data from: {output_file}")
    else:
        print("\n" + "="*80)
        print("FAILED!")
        print("="*80)