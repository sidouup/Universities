import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import math

st.set_page_config(layout="wide", page_title="University Search Tool")

# Add the image in the center of the page
st.markdown("""
<div style="text-align:center;">
    <img src="https://assets.zyrosite.com/cdn-cgi/image/format=auto,w=1200,h=630,fit=crop,f=jpeg/YBgonz9JJqHRMK43/blue-red-minimalist-high-school-logo-10-ALpbw97ayrS4jgJX.png" 
    alt="Logo" style="width:50%; height:auto;">
</div>
""", unsafe_allow_html=True)
