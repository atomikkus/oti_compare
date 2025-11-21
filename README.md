# Twin Analysis Dashboard

A Streamlit application for exploring and comparing patient clinical and genomic data, focusing on "twin" analysis to find similar patient profiles.

## Setup

1.  **Install Dependencies**:
    Ensure you have Python installed. Install the required packages using pip:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Application**:
    ```bash
    streamlit run app.py
    ```

## Required Data Structure

The application expects the following directory structure and data files to be present in the root directory:

-   **`final_twin_analysis/`**:
    -   Contains JSON files representing the twin analysis results (e.g., `P-XXXXXXX_vs_P-YYYYYYY.json`).
    -   These files drive the "Overview" and "Analysis Detail" views.

-   **`patient_profiles/`**:
    -   Contains JSON files for individual patient profiles (e.g., `P-XXXXXXX.json`).
    -   These files provide the detailed clinical and genomic data for the "Clinical Deep Dive" and "Genomics Deep Dive" views.
    -   *Note: This folder is populated by extracting data from the source profiles.*

## Application Views

-   **Overview**: Displays a high-level summary of all twin analyses, including similarity scores and key metrics.
-   **Analysis Detail**: Provides a side-by-side comparison of a query patient and their "twin", highlighting shared features, key differences, and genomic alignment.
-   **Clinical Deep Dive**: Detailed view of a single patient's clinical history, including demographics, treatments, and timeline events (surgery, radiation, progression, etc.).
-   **Genomics Deep Dive**: Detailed view of a single patient's genomic data, including mutations, copy number alterations (CNA), and structural variants (SV).
