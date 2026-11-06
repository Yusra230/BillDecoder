import os
import zipfile
from pathlib import Path

def create_submission_zip():
    base_dir = Path(__file__).resolve().parent
    zip_path = base_dir / "your-submission.zip"
    
    output_dir = base_dir / "output"
    l1_csv = output_dir / "level1.csv"
    l2_csv = output_dir / "level2.csv"
    
    if not (l1_csv.exists() and l2_csv.exists()):
        print("[ERROR] Output CSV files missing. Run main.py first!")
        return False
        
    print(f"Creating submission zip at {zip_path.name}...")
    
    files_to_pack = [
        # Output folder
        (l1_csv, "output/level1.csv"),
        (l2_csv, "output/level2.csv"),
        # Source files
        (base_dir / "README.md", "source/README.md"),
        (base_dir / ".env.example", "source/.env.example"),
        (base_dir / "requirements.txt", "source/requirements.txt"),
        (base_dir / "main.py", "source/main.py"),
    ]
    
    # Core package files
    core_dir = base_dir / "core"
    for py_file in core_dir.glob("*.py"):
        files_to_pack.append((py_file, f"source/core/{py_file.name}"))
        
    # Optional demo file if present
    demo_dir = base_dir / "demo"
    if demo_dir.exists():
        for d in demo_dir.glob("demo.*"):
            files_to_pack.append((d, f"demo/{d.name}"))
            
    with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for file_path, arcname in files_to_pack:
            if file_path.exists():
                zipf.write(file_path, arcname)
                print(f"  + Added: {arcname}")
            else:
                print(f"  ! Warning: {file_path.name} not found")
                
    zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"\n[SUCCESS] your-submission.zip created successfully.")
    print(f"Total ZIP size: {zip_size_mb:.2f} MB (Limit: 15.0 MB)")
    
    if zip_size_mb > 15.0:
        print("[ALERT] ZIP exceeds 15 MB limit! Reduce file sizes.")
        return False
    else:
        print("[CHECK] ZIP size is within the 15 MB limit.")
        return True

if __name__ == "__main__":
    create_submission_zip()
