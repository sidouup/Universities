
import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
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

# Function to load data from Google Sheets and apply filters
@st.cache_data
def load_filtered_data(spreadsheet_id, major_filter, country_filter, level_filter, field_filter, specialty_filter, institution_filter, tuition_min, tuition_max):
    client = get_google_sheet_client()
    sheets = client.open_by_key(spreadsheet_id).worksheets()
    filtered_data = []

    for sheet in sheets:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        # Convert numeric fields
        df['Tuition Price'] = pd.to_numeric(df['Tuition Price'], errors='coerce')
        df['Application Fee Price'] = pd.to_numeric(df['Application Fee Price'], errors='coerce')

        # Apply filters incrementally
        if major_filter != 'All':
            df = df[df['Major'] == major_filter]
        if country_filter != 'All':
            df = df[df['Country'] == country_filter]
        if level_filter != 'All':
            df = df[df['Level'] == level_filter]
        if field_filter != 'All':
            df = df[df['Field'] == field_filter]
        if specialty_filter != 'All':
            df = df[df['Spec'] == specialty_filter]
        if institution_filter != 'All':
            df = df[df['Institution Type'] == institution_filter]

        df = df[(df['Tuition Price'] >= tuition_min) & (df['Tuition Price'] <= tuition_max)]

        filtered_data.append(df)

    # Combine all filtered data
    combined_df = pd.concat(filtered_data, ignore_index=True)

    # Limit the number of rows to a maximum of 10,000
    if len(combined_df) > 10000:
        combined_df = combined_df.sample(n=10000, random_state=42)

    return combined_df


def main():
    st.set_page_config(layout="wide", page_title="University Search Tool")
    
    # Custom CSS for modern styling
    st.markdown("""
    <style>
    body {
        font-family: 'Roboto', sans-serif;
        background-color: #f9f9f9;
        color: #333333;
    }

    .stApp {
        background-color: #ffffff;
    }

    .sidebar .sidebar-content {
        background-color: #f8f9fa;
        padding: 15px;
    }

    [data-testid="stSidebar"] {
        min-width: 250px !important;
        max-width: 250px !important;
    }

    .stSelectbox, .stMultiSelect, .stSlider {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 8px;
        margin-bottom: 15px;
    }

    .university-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        min-height: 550px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.3s ease;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }

    .university-card:hover {
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }

    .university-header {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }

    .university-logo {
        width: 60px;
        height: 60px;
        margin-right: 15px;
        object-fit: contain;
    }

    .university-name {
        font-size: 1.5rem;
        font-weight: bold;
        color: #333333;
        text-align: left;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
    }

    .speciality-name {
        font-size: 1rem;
        margin-bottom: 15px;
        color: #555555;
        text-align: left;
        text-decoration: underline;
    }

    .info-container {
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        font-size: 0.95rem;
    }

    .info-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
        font-size: 0.9rem;
        color: #666666;
    }

    .info-row span:first-child {
        font-weight: bold;
    }

    .pagination {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 20px;
    }

    .page-info {
        margin: 0 10px;
        font-size: 1.1rem;
    }

    .stButton > button {
        background-color: #1e88e5;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 15px;
        font-size: 1rem;
        transition: background-color 0.3s ease;
    }

    .stButton > button:hover {
        background-color: #1565c0;
    }

    h1, h2, h3 {
        text-align: center;
        font-weight: bold;
        color: #333;
    }
    </style>
    """, unsafe_allow_html=True)

    # Replace with your Google Sheet ID
    SPREADSHEET_ID = "14pdY9sOkA0d6_5WtMFh-9Vp2lcO4WbLGCHdwye4s0J4"

    # Load data to extract filter options dynamically
    client = get_google_sheet_client()
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1  # Load first sheet, you can adjust this
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    # Extract filter options dynamically from the dataframe
    major_options = ['All'] + sorted(df['Major'].dropna().unique().tolist())
    country_options = ['All'] + sorted(df['Country'].dropna().unique().tolist())
    level_options = ['All'] + sorted(df['Level'].dropna().unique().tolist())
    field_options = ['All'] + sorted(df['Field'].dropna().unique().tolist())
    institution_options = ['All'] + sorted(df['Institution Type'].dropna().unique().tolist())

    # Initialize session state for filters
    if 'filters' not in st.session_state:
        st.session_state.filters = {
            'major': 'All',
            'country': 'All',
            'program_level': 'All',
            'field': 'All',
            'institution_type': 'All',
            'tuition_min': 0,
            'tuition_max': 100000  # Default range for tuition
        }

    # Initialize df_filtered with the entire dataset by default or an empty DataFrame
    df_filtered = df.copy()

    # Display filters in a more compact layout
    with st.form("filter_form"):
        st.subheader("Filter Options")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.session_state.filters['major'] = st.selectbox("Major", major_options)
            st.session_state.filters['country'] = st.selectbox("Country", country_options)
        with col2:
            st.session_state.filters['program_level'] = st.selectbox("Program Level", level_options)
            st.session_state.filters['field'] = st.selectbox("Field", field_options)
        with col3:
            st.session_state.filters['institution_type'] = st.selectbox("Institution Type", institution_options)
        
        # Tuition slider across all columns
        st.session_state.filters['tuition_min'], st.session_state.filters['tuition_max'] = st.slider(
            "Tuition Fee Range (CAD)",
            min_value=int(df['Tuition Price'].min()),
            max_value=int(df['Tuition Price'].max()),
            value=(st.session_state.filters['tuition_min'], st.session_state.filters['tuition_max'])
        )
        submit_button = st.form_submit_button("Apply Filters")

    # Load filtered data with a limit of 10,000 rows only if the button is pressed
    if submit_button:
        df_filtered = load_filtered_data(
            SPREADSHEET_ID,
            st.session_state.filters['major'],
            st.session_state.filters['country'],
            st.session_state.filters['program_level'],
            st.session_state.filters['field'],
            st.session_state.filters['institution_type'],
            st.session_state.filters['tuition_min'],
            st.session_state.filters['tuition_max']
        )
        st.success(f"Showing {len(df_filtered)} results (Max 10,000 rows)")

    # Display results with pagination
    items_per_page = 16
    total_pages = math.ceil(len(df_filtered) / items_per_page)

    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1

    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    # Display universities in a grid of 4 columns per row
    for i in range(0, min(items_per_page, len(df_filtered) - start_idx), 4):
        cols = st.columns(4)  # Create a grid layout with four columns
        for j in range(4):
            if i + j < len(df_filtered[start_idx:end_idx]):
                row = df_filtered.iloc[start_idx + i + j]
                st.markdown(f'''
                <div class="university-card">
                    <div class="university-header">
                        <img src="{row['Picture']}" class="university-logo" alt="{row['University Name']} logo">
                        <div class="university-name" style="font-size: 1.2rem;">{row['University Name']}</div>
                    </div>
                    <div class="speciality-name" style="font-size: 1rem; font-weight: bold; text-decoration: underline;">
                        {row['Speciality']}
                    </div>
                    <div class="info-container">
                        <div class="info-row">
                            <span>Location:</span>
                            <span>{row['City']}, {row['Country']}</span>
                        </div>
                        <div class="info-row">
                            <span>Tuition:</span>
                            <span>${row['Tuition Price']:,.0f} {row['Tuition Currency']}/Year</span>
                        <div class="info-row">
                            <span>Application Fee:</span>
                            <span>${row['Application Fee Price']:,.0f} {row['Application Fee Currency']}</span>
                        </div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)

    # Pagination controls
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

