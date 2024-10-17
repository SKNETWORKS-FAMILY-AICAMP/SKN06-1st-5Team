import pandas as pd
import streamlit as st

# Add a title and subtitle
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>FAQ</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>전기차 충전에 관한 FAQ를 제공합니다.</h3>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(['KIA EV', 'TAGO EV'])

with tab1: 
    # Load data
    df = pd.read_csv('EV_faq3.csv', index_col=False)

    # Display FAQs in an accordion style
    for index, row in df.iterrows():
        with st.expander(f"**{row['Questions']}**"):
            st.write(f"{row['Answer']}", unsafe_allow_html=True)

with tab2:
    df = pd.read_csv('tago_faq.csv', index_col=False)

    # Display FAQs in an accordion style
    for index, row in df.iterrows():
        with st.expander(f"**{row['Question']}**"):
            st.write(f"{row['Answer']}", unsafe_allow_html=True)

st.markdown(
    """
    <style>
    body {
        background-color: #f0f2f6;
    }
    .css-1d391kg {
        background-color: #ffffff;
        border: 1px solid #e6e6e6;
        padding: 20px;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

