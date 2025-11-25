import os
import json
import pandas as pd
import streamlit as st

def load_twin_analyses(directory):
    """Loads all JSON twin analysis files from the specified directory."""
    analyses = []
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory not found: {directory}")

    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    data['filename'] = filename # Add filename for reference
                    analyses.append(data)
            except json.JSONDecodeError:
                pass # st.warning(f"Skipping invalid JSON file: {filename}")
    return analyses

def load_clinical_data(directory):
    """Loads clinical patient and sample data from text files."""
    patient_file = os.path.join(directory, "data_clinical_patient.txt")
    sample_file = os.path.join(directory, "data_clinical_sample.txt")

    if not os.path.exists(patient_file) or not os.path.exists(sample_file):
        raise FileNotFoundError(f"Clinical data files not found in {directory}")

    # Skip header lines starting with #
    clinical_patients = pd.read_csv(patient_file, sep='\t', comment='#')
    clinical_samples = pd.read_csv(sample_file, sep='\t', comment='#')

    return clinical_patients, clinical_samples

def load_genomics_data(directory):
    """Loads genomics data (mutations, CNA, SV) from CSV files."""
    mutations_file = os.path.join(directory, "data_mutations_fully_annotated_luad.csv")
    cna_file = os.path.join(directory, "data_cna_fully_annotated_luad.csv")
    sv_file = os.path.join(directory, "data_sv_fully_annotated_luad.csv")

    genomics_data = {}
    
    # Load mutations
    if os.path.exists(mutations_file):
        genomics_data['mutations'] = pd.read_csv(mutations_file)
    else:
        st.warning(f"Mutations file not found: {mutations_file}")
        genomics_data['mutations'] = pd.DataFrame()
    
    # Load CNA
    if os.path.exists(cna_file):
        genomics_data['cna'] = pd.read_csv(cna_file)
    else:
        st.warning(f"CNA file not found: {cna_file}")
        genomics_data['cna'] = pd.DataFrame()
    
    # Load SV
    if os.path.exists(sv_file):
        genomics_data['sv'] = pd.read_csv(sv_file)
    else:
        st.warning(f"SV file not found: {sv_file}")
        genomics_data['sv'] = pd.DataFrame()

    return genomics_data

def load_patient_profiles(directory):
    """Loads all patient profile JSON files from the specified directory."""
    profiles = {}
    if not os.path.exists(directory):
        st.error(f"Directory not found: {directory}")
        return profiles

    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    # Use filename without extension as key if patient_id is missing, 
                    # though patient_id should be in the JSON
                    patient_id = data.get('patient_id', os.path.splitext(filename)[0])
                    profiles[patient_id] = data
            except json.JSONDecodeError:
                pass
    return profiles
