import os
import shutil
import re
from pathlib import Path

# Define paths
final_twin_analysis_dir = r"c:\Users\satya\Downloads\oti_compare\final_twin_analysis"
source_profiles_dir = r"c:\Users\satya\Downloads\oti_compare\output_profiles_lite-20251120T113706Z-1-001\output_profiles_lite"
destination_dir = r"c:\Users\satya\Downloads\oti_compare\patient_profiles"

# Create destination directory if it doesn't exist
os.makedirs(destination_dir, exist_ok=True)

# Extract unique patient IDs from final_twin_analysis folder
patient_ids = set()

for filename in os.listdir(final_twin_analysis_dir):
    if filename.endswith('_analysis.json'):
        # Extract patient IDs from filenames like "P-0021419_twin_P-0004863_analysis.json"
        # Pattern: P-XXXXXXX_twin_P-YYYYYYY_analysis.json
        matches = re.findall(r'(P-\d{7})', filename)
        patient_ids.update(matches)

print(f"Found {len(patient_ids)} unique patients in final_twin_analysis folder")
print(f"Patient IDs: {sorted(patient_ids)[:10]}...")  # Show first 10

# Copy patient profile files
copied_count = 0
missing_count = 0
missing_patients = []

for patient_id in sorted(patient_ids):
    source_file = os.path.join(source_profiles_dir, f"{patient_id}.json")
    destination_file = os.path.join(destination_dir, f"{patient_id}.json")
    
    if os.path.exists(source_file):
        shutil.copy2(source_file, destination_file)
        copied_count += 1
    else:
        missing_count += 1
        missing_patients.append(patient_id)

print(f"\nCopied {copied_count} patient profiles to {destination_dir}")
print(f"Missing {missing_count} patient profiles")

if missing_patients:
    print(f"\nMissing patients: {missing_patients[:10]}...")  # Show first 10 missing
