# Rename extracted township files

import os
from pathlib import Path

def rename_township_files():
    """Rename extracted township files to standard names"""
    
    data_dir = Path(r"D:\114學年\遙測\windsurf_project\week6\week6_exercise6\data")
    
    print("Renaming township files...")
    print(f"Data directory: {data_dir}")
    
    # File mappings (source -> target)
    file_mappings = {
        "TOWN_MOI_1140318.shp": "TOWN_MOI.shp",
        "TOWN_MOI_1140318.shx": "TOWN_MOI.shx", 
        "TOWN_MOI_1140318.dbf": "TOWN_MOI.dbf",
        "TOWN_MOI_1140318.prj": "TOWN_MOI.prj"
    }
    
    renamed_count = 0
    
    for source_name, target_name in file_mappings.items():
        source_path = data_dir / source_name
        target_path = data_dir / target_name
        
        if source_path.exists():
            try:
                # Remove target if it exists
                if target_path.exists():
                    target_path.unlink()
                    print(f"Removed existing: {target_name}")
                
                # Rename source to target
                source_path.rename(target_path)
                size = target_path.stat().st_size
                print(f"RENAMED: {source_name} -> {target_name} ({size} bytes)")
                renamed_count += 1
                
            except Exception as e:
                print(f"ERROR renaming {source_name}: {e}")
        else:
            print(f"MISSING: {source_name}")
    
    print(f"\nRenaming complete: {renamed_count}/{len(file_mappings)} files")
    
    # Verify results
    print(f"\nFinal verification:")
    target_files = ['TOWN_MOI.shp', 'TOWN_MOI.shx', 'TOWN_MOI.dbf', 'TOWN_MOI.prj']
    
    all_exist = True
    for filename in target_files:
        file_path = data_dir / filename
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  {filename}: OK ({size} bytes)")
        else:
            print(f"  {filename}: MISSING")
            all_exist = False
    
    return all_exist

if __name__ == "__main__":
    success = rename_township_files()
    if success:
        print("\nSUCCESS: All township files renamed correctly!")
        print("Cell 11 can now run with real data.")
    else:
        print("\nFAILED: Some township files are still missing!")
