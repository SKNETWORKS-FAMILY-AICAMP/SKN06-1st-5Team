import streamlit as st
import pandas as pd

st.title("FAQ")

df = pd.read_csv('EV_faq2.csv', index_col=False)
st.write(df)