import streamlit as st
import altair as alt
import pandas as pd
from streamlit_extras import chart_container

col1, col2 = st.columns([1,3])

with col2:
    st.subheader("Container for charts",divider='rainbow')
    with st.container():
        source = pd.DataFrame({
            "a": ["A", "B", "C"],
            "b": [28, 55, 43]
        })

        bar = alt.Chart(source).mark_bar().encode(
            y="a:N",
            x=alt.X("b:Q").scale(domain=[0, 60])
        ).properties(height=600)
        
        text = bar.mark_text(
            align="left",
            baseline="middle",
            dx=3
        ).encode(text="b")

        st.altair_chart(bar + text, use_container_width=True)