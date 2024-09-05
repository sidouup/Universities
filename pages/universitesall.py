import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from difflib import get_close_matches
import math

# Use your service account info from Streamlit secrets
SERVICE_ACCOUNT_INFO = st.secrets["gcp_service_account"]

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']

# Authenticate and build the Google Sheets service
@st.cache_resource
def get_google_sheet_client():
    creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
    return gspread.authorize(creds)

# Function to load data from a specific sheet in Google Sheets
@st.cache_data
def load_data(spreadsheet_id, sheet_name):
    client = get_google_sheet_client()
    sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

def main():
    st.set_page_config(layout="wide", page_title="University Search Tool - Multiple Sheets")
    
    # Google Sheet ID (replace with your actual ID)
    SPREADSHEET_ID = "1gCxnCOhQRHtVdVMSiLaReBRJbCUz1Wn6-KJRZshneuM"
    
    # Get available sheets
    client = get_google_sheet_client()
    sheets = client.open_by_key(SPREADSHEET_ID).worksheets()
    sheet_names = [sheet.title for sheet in sheets]
    
    # Select sheet to display
    selected_sheet = st.selectbox("Select a sheet to view", options=sheet_names)
    
    # Load the data from the selected sheet
    df = load_data(SPREADSHEET_ID, selected_sheet)

    # Handle data formatting (adjust column names as needed for each sheet)
    # Let's assume these columns are standard and available in each sheet
    if 'Tuition Price' in df.columns:
        df['Tuition Price'] = pd.to_numeric(df['Tuition Price'], errors='coerce')
    if 'Application Fee Price' in df.columns:
        df['Application Fee Price'] = pd.to_numeric(df['Application Fee Price'], errors='coerce')

    # Filters and session state management (same logic as previous)
    if 'filters' not in st.session_state:
        st.session_state.filters = {
            'major': 'All',
            'country': 'All',
            'program_level': 'All',
            'field': 'All',
            'specialty': 'All',
            'institution_type': 'All',
            'tuition_min': int(df['Tuition Price'].min()) if 'Tuition Price' in df.columns else 0,
            'tuition_max': int(df['Tuition Price'].max()) if 'Tuition Price' in df.columns else 0,
            'french_only': False
        }

    # Apply filters as before (adjust for each sheet)
    if 'Tuition Price' in df.columns:
        st.session_state.filters['tuition_min'], st.session_state.filters['tuition_max'] = st.slider(
            "Tuition fee range (CAD)",
            min_value=int(df['Tuition Price'].min()),
            max_value=int(df['Tuition Price'].max()),
            value=(st.session_state.filters['tuition_min'], st.session_state.filters['tuition_max']),
            key='tuition_filter'
        )

    # Apply all other filters as needed, similar to the original code
    
    # Display results using similar pagination and card layout
    st.subheader(f"Showing {len(df)} results from {selected_sheet}")
    
    items_per_page = 16  # Adjust pagination
    total_pages = math.ceil(len(df) / items_per_page)

    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1

    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    # Display university cards (same logic as before)
    for i in range(0, min(items_per_page, len(df) - start_idx), 4):
        cols = st.columns(4)  # Create a grid layout with four columns
        for j in range(4):
            if i + j < len(df[start_idx:end_idx]):
                row = df.iloc[start_idx + i + j]
                with cols[j]:
                    st.markdown(f'''
                    <div class="university-card">
                        <div class="university-header">
                            <div class="university-name">{row.get('University Name', 'N/A')}</div>
                        </div>
                        <div class="speciality-name">{row.get('Speciality', 'N/A')}</div>
                        <div class="info-container">
                            <div class="info-row">
                                <span>Location:</span>
                                <span>{row.get('City', 'N/A')}, {row.get('Country', 'N/A')}</span>
                            </div>
                            <div class="info-row">
                                <span>Tuition:</span>
                                <span>${row.get('Tuition Price', 'N/A'):,.0f}</span>
                            </div>
                            <div class="info-row">
                                <span>Application fee:</span>
                                <span>${row.get('Application Fee Price', 'N/A'):,.0f}</span>
                            </div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)

    # Pagination
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.session_state.current_page > 1:
            if st.button("◀ Previous"):
                st.session_state.current_page -= 1
                st.rerun()
    with col2:
        st.markdown(f'<div class="page-info">Page {st.session_state.current_page} of {total_pages}</div>', unsafe_allow_html=True)
    with col3:
        if st.session_state.current_page < total_pages:
            if st.button("Next ▶"):
                st.session_state.current_page += 1
                st.rerun()

if __name__ == "__main__":
    main()
