import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def show(analyses):
    st.title("Twin Analysis Overview")

    if not analyses:
        st.info("No analyses found.")
        return

    # Prepare data
    df_data = []
    for a in analyses:
        # Handle shared_features - it can be a list, dict with 'biomarkers' key, or dict with other structure
        shared_features = a.get('shared_features', {})
        if isinstance(shared_features, dict):
            shared_biomarkers_count = len(shared_features.get('biomarkers', []))
        elif isinstance(shared_features, list):
            shared_biomarkers_count = len(shared_features)
        else:
            shared_biomarkers_count = 0
            
        df_data.append({
            "Query Patient": a.get('query_patient_id'),
            "Twin Patient": a.get('twin_id'),
            "Similarity Score": a.get('similarity_score', 0),
            "Rank": a.get('rank', 0),
            "Match Grade": a.get('match_quality', {}).get('grade', 'N/A'),
            "Shared Biomarkers": shared_biomarkers_count,
        })
    
    df = pd.DataFrame(df_data)
    
    # Summary Metrics
    total_analyses = len(analyses)
    avg_similarity = df['Similarity Score'].mean()
    max_similarity = df['Similarity Score'].max()
    avg_biomarkers = df['Shared Biomarkers'].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Analysis Pairs", total_analyses)
    col2.metric("Avg Similarity Score", f"{avg_similarity:.3f}")
    col3.metric("Max Similarity Score", f"{max_similarity:.3f}")
    col4.metric("Avg Shared Biomarkers", f"{avg_biomarkers:.1f}")

    st.markdown("---")

    # Visualizations
    col_left, col_right = st.columns(2)
    
    with col_left:
        # 1. Similarity Score Distribution
        st.markdown("#### Similarity Score Distribution")
        fig_hist = px.histogram(
            df, 
            x='Similarity Score',
            nbins=20,
            color_discrete_sequence=['#3B82F6'],
            labels={'Similarity Score': 'Similarity Score', 'count': 'Count'}
        )
        fig_hist.update_layout(
            showlegend=False,
            height=300,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_right:
        # 2. Match Grade Distribution
        st.markdown("#### Match Grade Distribution")
        grade_counts = df['Match Grade'].value_counts().reset_index()
        grade_counts.columns = ['Match Grade', 'Count']
        grade_counts = grade_counts.sort_values('Match Grade')
        
        fig_grades = px.bar(
            grade_counts,
            x='Match Grade',
            y='Count',
            color='Count',
            color_continuous_scale='Viridis',
            labels={'Match Grade': 'Match Grade', 'Count': 'Number of Pairs'}
        )
        fig_grades.update_layout(
            showlegend=False,
            height=300,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_grades, use_container_width=True)

    # 3. Top Twin Pairs
    st.markdown("#### Top 10 Twin Pairs by Similarity Score")
    df_top = df.nlargest(10, 'Similarity Score').copy()
    df_top['Pair'] = df_top['Query Patient'] + ' ↔ ' + df_top['Twin Patient']
    
    fig_top = px.bar(
        df_top.sort_values('Similarity Score'),
        x='Similarity Score',
        y='Pair',
        orientation='h',
        color='Similarity Score',
        color_continuous_scale='Blues',
        labels={'Similarity Score': 'Similarity Score', 'Pair': 'Twin Pair'}
    )
    fig_top.update_layout(
        showlegend=False,
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        yaxis={'categoryorder': 'total ascending'}
    )
    st.plotly_chart(fig_top, use_container_width=True)

    # 4. Shared Biomarkers Distribution
    st.markdown("#### Shared Biomarkers Distribution")
    fig_biomarkers = px.histogram(
        df,
        x='Shared Biomarkers',
        nbins=15,
        color_discrete_sequence=['#10B981'],
        labels={'Shared Biomarkers': 'Number of Shared Biomarkers', 'count': 'Count'}
    )
    fig_biomarkers.update_layout(
        showlegend=False,
        height=300,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_biomarkers, use_container_width=True)
