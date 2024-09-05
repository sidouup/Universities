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
    
    # Custom CSS for styling
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    
    body {
        font-family: 'Roboto', sans-serif;
        background-color: #ffffff;
        color: #333333;
    }
    
    .stApp {
        background-color: #ffffff;
    }
    
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
        padding: 10px;
    }
    
    [data-testid="stSidebar"] {
        min-width: 200px !important;
        max-width: 200px !important;
    }
    
    .stSelectbox, .stMultiSelect, .stSlider {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 5px;
        margin-bottom: 10px;
    }
    
    .university-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        min-height: 500px;  /* Fixed height for consistent card size */
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .university-card:hover {
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .university-header {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }
    
    .university-logo {
        width: 50px;
        height: 50px;
        margin-right: 10px;
        object-fit: contain;
    }
    
    .university-name {
        font-size: 1.2rem;
        font-weight: bold;
        color: #333333;
        flex-grow: 1;
        text-align: center;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2; /* Limit to two lines */
        -webkit-box-orient: vertical;
    }
    
    .speciality-name {
        font-size: 1rem;
        margin-bottom: 15px;
        color: #555555;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2; /* Limit to two lines */
        -webkit-box-orient: vertical;
        text-align: center;
        text-decoration: underline;  /* Underline specialty names */
    }
    
    .info-container {
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        font-size: 0.9rem;
    }
    
    .info-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 5px;
        font-size: 0.85rem;
        color: #666666;
    }
    
    .info-row span:first-child {
        font-weight: bold; /* Make labels bold */
    }
    
    .create-application-btn {
        background-color: #1e88e5;
        color: white !important;  /* Force text color to white */
        font-weight: bold !important;  /* Force text to bold */
        padding: 10px 15px;
        border-radius: 5px;
        text-align: center;
        text-decoration: none;
        display: block;
        font-size: 1rem;
        margin-top: 10px;
        transition: background-color 0.3s ease;
    }
    
    .create-application-btn:hover {
        background-color: #1565c0;
    }
    
    .prime-tags {
        margin-bottom: 10px;
        display: flex;
        flex-wrap: nowrap; /* Prevent wrapping */
        justify-content: center;
        height: 25px; /* Adjust height for consistency */
        align-items: center; /* Vertically align tags */
        overflow: hidden; /* Hide overflow if too many tags */
    }
    
    .prime-tag {
        background-color: #ffd700;
        color: #333333;
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 0.65rem; /* Smaller size for fitting more tags */
        margin-right: 2px;
        display: inline-block;
    }
    
    .stButton > button {
        background-color: #1e88e5;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 5px 10px;
        font-size: 1rem;
        transition: background-color 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #1565c0;
    }
    
    .pagination {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 20px;
    }
    
    .page-info {
        margin: 0 10px;
        font-size: 1rem;
    }
    
    h1, h2, h3 {
        text-align: center;
        font-weight: bold;
        text-decoration: underline;
    }
    </style>
    """, unsafe_allow_html=True)

    # Replace with your Google Sheet ID
    SPREADSHEET_ID = "14pdY9sOkA0d6_5WtMFh-9Vp2lcO4WbLGCHdwye4s0J4"

    # Initialize session state for filters
    if 'filters' not in st.session_state:
        st.session_state.filters = {
            'major': 'All',
            'country': 'All',
            'program_level': 'All',
            'field': 'All',
            'specialty': 'All',
            'institution_type': 'All',
            'tuition_min': 0,
            'tuition_max': 100000  # Default range for tuition
        }

    # Load filter options (Assume preloaded lists from the dataset)
    major_options = ["All"]  # Load from dataset
    country_options = ["All"]  # Load from dataset
    level_options = ["All"]  # Load from dataset
    field_options = ["All"]  # Load from dataset
    specialty_options = ["All"]  # Load from dataset
    institution_options = ["All"]  # Load from dataset

    # Filters
    st.session_state.filters['major'] = st.selectbox("Major", major_options)
    st.session_state.filters['country'] = st.selectbox("Country", country_options)
    st.session_state.filters['program_level'] = st.selectbox("Program Level", level_options)
    st.session_state.filters['field'] = st.selectbox("Field", field_options)
    st.session_state.filters['specialty'] = st.selectbox("Specialty", specialty_options)
    st.session_state.filters['institution_type'] = st.selectbox("Institution Type", institution_options)

    # Tuition Range Filter
    st.session_state.filters['tuition_min'], st.session_state.filters['tuition_max'] = st.slider(
        "Tuition Fee Range (CAD)",
        min_value=0,
        max_value=100000,  # Adjust max value based on your data
        value=(st.session_state.filters['tuition_min'], st.session_state.filters['tuition_max'])
    )

    # Load filtered data with a limit of 10,000 rows
    df = load_filtered_data(
        SPREADSHEET_ID,
        st.session_state.filters['major'],
        st.session_state.filters['country'],
        st.session_state.filters['program_level'],
        st.session_state.filters['field'],
        st.session_state.filters['specialty'],
        st.session_state.filters['institution_type'],
        st.session_state.filters['tuition_min'],
        st.session_state.filters['tuition_max']
    )

    st.subheader(f"Showing {len(df)} results (Max 10,000 rows)")

    # Display results with pagination
    items_per_page = 16
    total_pages = math.ceil(len(df) / items_per_page)

    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1

    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    for i in range(0, min(items_per_page, len(df) - start_idx), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(df[start_idx:end_idx]):
                row = df.iloc[start_idx + i + j]
                with cols[j]:
                    st.markdown(f'''
                    <div class="university-card">
                        <div class="university-header">
                            <div class="university-name">{row.get('University Name', 'N/A')}</div>
                        </div>
                        <div class="speciality-name">{row.get('Spec', 'N/A')}</div>
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
                                <span>Application Fee:</span>
                                <span>${row.get('Application Fee Price', 'N/A'):,.0f}</span>
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

