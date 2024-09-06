import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import math

st.set_page_config(layout="wide", page_title="University Search Tool")
st.title("Scholarships prochainmnt ......")
# Add the image in the center of the page
st.markdown("""
<div style="text-align:center;">
    <img src="https://assets.zyrosite.com/cdn-cgi/image/format=auto,w=228,fit=crop,q=95/YBgonz9JJqHRMK43/blue-red-minimalist-high-school-logo-9-AVLN0K6MPGFK2QbL.png" 
    alt="Logo" style="width:50%; height:auto;">
</div>
""", unsafe_allow_html=True)
