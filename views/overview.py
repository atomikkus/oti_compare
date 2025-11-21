import streamlit as st
import pandas as pd

def show(analyses):
    st.title("Twin Analysis Overview")

    if not analyses:
        st.info("No analyses found.")
        return

    # Summary Metrics
    total_analyses = len(analyses)
    avg_similarity = pd.Series([a.get('similarity_score', 0) for a in analyses]).mean()

    col1, col2 = st.columns(2)
    col1.metric("Total Analyses", total_analyses)
    col2.metric("Average Similarity Score", f"{avg_similarity:.4f}")

    # Data Table
    data = []
    for a in analyses:
        data.append({
            "Query Patient": a.get('query_patient_id'),
            "Twin Patient": a.get('twin_id'),
            "Similarity Score": a.get('similarity_score'),
            "Rank": a.get('rank'),
            "Filename": a.get('filename')
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
