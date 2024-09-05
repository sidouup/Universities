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

# Function to load all sheets from Google Sheets and merge into one DataFrame
@st.cache_data
def load_all_sheets(spreadsheet_id):
    client = get_google_sheet_client()
    sheets = client.open_by_key(spreadsheet_id).worksheets()
    all_data = []
    for sheet in sheets:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        all_data.append(df)
    
    # Combine all sheets into one DataFrame
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Clean Tuition Price and Application Fee Price columns
    combined_df['Tuition Price'] = pd.to_numeric(combined_df['Tuition Price'], errors='coerce')
    combined_df['Application Fee Price'] = pd.to_numeric(combined_df['Application Fee Price'], errors='coerce')
    
    return combined_df

def main():
    st.set_page_config(layout="wide", page_title="University Search Tool")
    
    # Custom CSS for styling
    st.markdown("""
    <style>
    /* Add your styling similar to the provided interface */
    .university-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        min-height: 500px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .university-card:hover {
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }

    .university-name {
        font-size: 1.2rem;
        font-weight: bold;
        color: #333333;
        text-align: center;
    }

    .speciality-name {
        font-size: 1rem;
        margin-bottom: 15px;
        color: #555555;
        text-align: center;
    }

    .info-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 5px;
        font-size: 0.9rem;
        color: #666666;
    }

    .info-row span:first-child {
        font-weight: bold;
    }

    .page-info {
        margin: 0 10px;
        font-size: 1rem;
        text-align: center;
    }

    </style>
    """, unsafe_allow_html=True)

    # Replace with your Google Sheet ID
    SPREADSHEET_ID = "14pdY9sOkA0d6_5WtMFh-9Vp2lcO4WbLGCHdwye4s0J4"

    # Load data from all sheets
    df = load_all_sheets(SPREADSHEET_ID)

    # Initialize session state for filters
    if 'filters' not in st.session_state:
        st.session_state.filters = {
            'major': 'All',
            'country': 'All',
            'program_level': 'All',
            'field': 'All',
            'specialty': 'All',
            'institution_type': 'All',
            'tuition_min': int(df['Tuition Price'].min()),
            'tuition_max': int(df['Tuition Price'].max())
        }

    # Filters
    major_options = ["All"] + sorted(df['Major'].unique().tolist())
    st.session_state.filters['major'] = st.selectbox("Search by Major", major_options)

    country_options = ["All"] + sorted(df['Country'].unique().tolist())
    st.session_state.filters['country'] = st.selectbox("Country", country_options)

    level_options = ["All"] + sorted(df['Level'].unique().tolist())
    st.session_state.filters['program_level'] = st.selectbox("Program Level", level_options)

    field_options = ["All"] + sorted(df['Field'].unique().tolist())
    st.session_state.filters['field'] = st.selectbox("Field", field_options)

    specialty_options = ["All"] + sorted(df['Spec'].unique().tolist())
    st.session_state.filters['specialty'] = st.selectbox("Specialty", specialty_options)

    institution_options = ["All"] + sorted(df['Institution Type'].unique().tolist())
    st.session_state.filters['institution_type'] = st.selectbox("Institution Type", institution_options)

    st.session_state.filters['tuition_min'], st.session_state.filters['tuition_max'] = st.slider(
        "Tuition Fee Range (CAD)",
        min_value=int(df['Tuition Price'].min()),
        max_value=int(df['Tuition Price'].max()),
        value=(st.session_state.filters['tuition_min'], st.session_state.filters['tuition_max'])
    )

    # Filter the data based on selected filters
    filtered_df = df.copy()
    if st.session_state.filters['major'] != "All":
        filtered_df = filtered_df[filtered_df['Major'] == st.session_state.filters['major']]
    if st.session_state.filters['country'] != "All":
        filtered_df = filtered_df[filtered_df['Country'] == st.session_state.filters['country']]
    if st.session_state.filters['program_level'] != "All":
        filtered_df = filtered_df[filtered_df['Level'] == st.session_state.filters['program_level']]
    if st.session_state.filters['field'] != "All":
        filtered_df = filtered_df[filtered_df['Field'] == st.session_state.filters['field']]
    if st.session_state.filters['specialty'] != "All":
        filtered_df = filtered_df[filtered_df['Spec'] == st.session_state.filters['specialty']]
    if st.session_state.filters['institution_type'] != "All":
        filtered_df = filtered_df[filtered_df['Institution Type'] == st.session_state.filters['institution_type']]
    filtered_df = filtered_df[
        (filtered_df['Tuition Price'] >= st.session_state.filters['tuition_min']) &
        (filtered_df['Tuition Price'] <= st.session_state.filters['tuition_max'])
    ]

    # Display results using pagination
    st.subheader(f"Showing {len(filtered_df)} results")

    items_per_page = 16  # Adjust pagination
    total_pages = math.ceil(len(filtered_df) / items_per_page)

    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1

    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    for i in range(0, min(items_per_page, len(filtered_df) - start_idx), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(filtered_df[start_idx:end_idx]):
                row = filtered_df.iloc[start_idx + i + j]
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
