# Extract township files from ZIP without encoding issues

import zipfile
import shutil
from pathlib import Path

def extract_township_files():
    """Extract township boundary files from ZIP"""
    
    # File paths
    zip_path = Path(r"C:\Users\User\Downloads\OFiles_9e222fea-bafb-4436-9b17-10921abc6ef2.zip")
    target_dir = Path(r"D:\114學年\遙測\windsurf_project\week6\week6_exercise6\data")
    
    print("Extracting township files from ZIP...")
    print(f"ZIP file: {zip_path}")
    print(f"Target dir: {target_dir}")
    
    if not zip_path.exists():
        print(f"ERROR: ZIP file not found: {zip_path}")
        return False
    
    # Ensure target directory exists
    target_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # List ZIP contents
            file_list = zip_ref.namelist()
            print(f"\nZIP contents ({len(file_list)} files):")
            
            # Find TOWN_MOI files
            town_files = []
            for file in file_list:
                if 'TOWN_MOI' in file and file.endswith(('.shp', '.shx', '.dbf', '.prj')):
                    town_files.append(file)
                    print(f"  Found: {file}")
            
            print(f"\nTownship files to extract: {len(town_files)}")
            
            # Extract files
            extracted_count = 0
            for file_info in town_files:
                try:
                    # Extract file
                    zip_ref.extract(file_info, target_dir)
                    
                    # Get just the filename
                    filename = Path(file_info).name
                    extracted_path = target_dir / filename
                    
                    if extracted_path.exists():
                        size = extracted_path.stat().st_size
                        print(f"EXTRACTED: {filename} ({size} bytes)")
                        extracted_count += 1
                    else:
                        print(f"ERROR: {filename} not found after extraction")
                        
                except Exception as e:
                    print(f"ERROR extracting {file_info}: {e}")
            
            print(f"\nExtraction complete: {extracted_count} files")
            
            # Verify results
            print(f"\nVerification:")
            shp_files = ['TOWN_MOI.shp', 'TOWN_MOI.shx', 'TOWN_MOI.dbf', 'TOWN_MOI.prj']
            
            all_exist = True
            for filename in shp_files:
                file_path = target_dir / filename
                if file_path.exists():
                    size = file_path.stat().st_size
                    print(f"  {filename}: OK ({size} bytes)")
                else:
                    print(f"  {filename}: MISSING")
                    all_exist = False
            
            return all_exist
            
    except Exception as e:
        print(f"ERROR: Cannot process ZIP file: {e}")
        return False

if __name__ == "__main__":
    success = extract_township_files()
    if success:
        print("\nSUCCESS: Township boundary files extracted!")
        print("Cell 11 can now run with real data.")
    else:
        print("\nFAILED: Township boundary files extraction failed!")
        print("Cell 11 will continue with simulated data.")
