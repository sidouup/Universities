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

# Function to load all data from Google Sheets
@st.cache_data(ttl=3600)
def load_all_data(spreadsheet_id):
    client = get_google_sheet_client()
    sheets = client.open_by_key(spreadsheet_id).worksheets()
    all_data = []

    for sheet in sheets:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        all_data.append(df)

    # Combine all data
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Ensure the 'Tuition Price' column is numeric
    combined_df['Tuition Price'] = pd.to_numeric(combined_df['Tuition Price'], errors='coerce')
    
    return combined_df

# Function to apply filters to the data
def apply_filters(df, major_filter, country_filter, level_filter, field_filter, institution_filter, tuition_min, tuition_max, search_query):
    if major_filter != 'All':
        df = df[df['Major'] == major_filter]
    if country_filter != 'All':
        df = df[df['Country'] == country_filter]
    if level_filter != 'All':
        df = df[df['Level'] == level_filter]
    if field_filter != 'All':
        df = df[df['Field'] == field_filter]
    if institution_filter != 'All':
        df = df[df['Institution Type'] == institution_filter]

    df = df[df['Tuition Price'].notna() & (df['Tuition Price'] >= tuition_min) & (df['Tuition Price'] <= tuition_max)]

    if search_query:
        df = df[df['University Name'].str.contains(search_query, case=False, na=False) |
                df['Speciality'].str.contains(search_query, case=False, na=False)]

    return df


def main():
    st.set_page_config(layout="wide", page_title="University Search Tool")

        # Custom CSS
    st.markdown("""
    <style>
.university-card {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 15px;
    padding: 15px;
    margin-bottom: 20px;
    height: 350px;  /* Fixed height */
    display: flex;
    flex-direction: column;
    transition: all 0.3s ease;
    box-shadow: 0 4px 8px rgba(0,0,0,0.05);
}
.university-card:hover {
    box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}
.university-header {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
    height: 60px;  /* Fixed height for logo and name */
}
.university-logo {
    width: 50px;
    height: 50px;
    margin-right: 10px;
    object-fit: contain;
}
.university-name {
    font-size: 1.1rem;
    font-weight: bold;
    color: #333333;
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}
.speciality-container {
    height: 50px;  /* Fixed height for specialty */
    margin-bottom: 10px;
    position: relative;
}
.speciality-name {
    font-size: 0.9rem;
    font-weight: bold;
    color: #555555;
    text-decoration: underline;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
    cursor: pointer;
}
.speciality-name:hover::after {
    content: attr(data-full-text);
    position: absolute;
    background: #ffffff;
    border: 1px solid #ddd;
    padding: 5px;
    border-radius: 5px;
    z-index: 1;
    white-space: normal;
    word-wrap: break-word;
    max-width: 300px;
    top: 100%;
    left: 0;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
.info-container {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.info-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
    font-size: 0.85rem;
    color: #666666;
}
.info-row span:first-child {
    font-weight: bold;
}
.emoji-icon {
    font-size: 1rem;
    margin-right: 4px;
    display: inline-block;
}

/* Level specific styling */
.level-container {
    position: relative;
    margin-bottom: 10px;
    display: flex;
    align-items: center; /* Align icon and text in the same line */
}
.level-container span {
    display: inline-block;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis; /* Ensure the text truncates with ellipsis */
    max-width: 100%; /* Ensure it fits in the available space */
}
.level-name {
    font-size: 0.9rem;
    font-weight: bold;
    color: #555555;
    overflow: hidden;
    white-space: nowrap; /* Prevent text from wrapping */
    text-overflow: ellipsis; /* Add ellipsis */
    max-width: calc(100% - 1rem); /* Ensure some part of the text is shown */
}
.level-name:hover::after {
    content: attr(data-full-text); /* Shows the full content on hover */
    position: absolute;
    background: #ffffff;
    border: 1px solid #ddd;
    padding: 5px;
    border-radius: 5px;
    z-index: 1;
    white-space: normal;
    word-wrap: break-word;
    max-width: 300px; /* Adjust for tooltip size */
    top: 100%;
    left: 0;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

/* Pagination styling */
.page-info {
    text-align: center;
    color: #4b5563;
    font-weight: bold;
    margin-top: 10px;
}
    </style>
    """, unsafe_allow_html=True)
    
    st.title("🎓 University Search Tool")

    # Google Sheet ID
    # Google Sheet ID
    SPREADSHEET_ID = "14pdY9sOkA0d6_5WtMFh-9Vp2lcO4WbLGCHdwye4s0J4"

    # Load all data once
    all_data = load_all_data(SPREADSHEET_ID)

    # Extract filter options dynamically from the dataframe
    major_options = ['All'] + sorted(all_data['Major'].dropna().unique().tolist())
    country_options = ['All'] + sorted(all_data['Country'].dropna().unique().tolist())
    level_options = ['All'] + sorted(all_data['Level'].dropna().unique().tolist())
    field_options = ['All'] + sorted(all_data['Field'].dropna().unique().tolist())
    institution_options = ['All'] + sorted(all_data['Institution Type'].dropna().unique().tolist())

    # Initialize session state for filters and pagination
    if 'filters' not in st.session_state:
        st.session_state.filters = {
            'major': 'All',
            'country': 'All',
            'program_level': 'All',
            'field': 'All',
            'institution_type': 'All',
            'tuition_min': int(all_data['Tuition Price'].min()),
            'tuition_max': int(all_data['Tuition Price'].max())
        }
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""

    search_query = st.text_input("🔍 Search by University Name or Speciality", value=st.session_state.search_query)

    with st.form("filter_form"):
        st.subheader("🔎 Filter Options")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.session_state.filters['major'] = st.selectbox("📚 Major", major_options, index=major_options.index(st.session_state.filters['major']))
            st.session_state.filters['country'] = st.selectbox("🌎 Country", country_options, index=country_options.index(st.session_state.filters['country']))
        with col2:
            st.session_state.filters['program_level'] = st.selectbox("🎓 Program Level", level_options, index=level_options.index(st.session_state.filters['program_level']))
            st.session_state.filters['field'] = st.selectbox("🔬 Field", field_options, index=field_options.index(st.session_state.filters['field']))
        with col3:
            st.session_state.filters['institution_type'] = st.selectbox("🏛️ Institution Type", institution_options, index=institution_options.index(st.session_state.filters['institution_type']))
        
        st.session_state.filters['tuition_min'], st.session_state.filters['tuition_max'] = st.slider(
            "💰 Tuition Fee Range (CAD)",
            min_value=int(all_data['Tuition Price'].min()),
            max_value=int(all_data['Tuition Price'].max()),
            value=(st.session_state.filters['tuition_min'], st.session_state.filters['tuition_max'])
        )
        
        submit_button = st.form_submit_button("🔍 Apply Filters")

    # Reset button outside the form
    reset_button = st.button("🔄 Reset Filters")

    # Handle reset button click
    if reset_button:
        st.session_state.filters = {
            'major': 'All',
            'country': 'All',
            'program_level': 'All',
            'field': 'All',
            'institution_type': 'All',
            'tuition_min': int(all_data['Tuition Price'].min()),
            'tuition_max': int(all_data['Tuition Price'].max())
        }
        st.session_state.search_query = ""
        st.session_state.current_page = 1
        st.rerun()

    if submit_button or search_query != st.session_state.search_query:
        st.session_state.current_page = 1
        st.session_state.search_query = search_query

    filtered_data = apply_filters(
        all_data,
        st.session_state.filters['major'],
        st.session_state.filters['country'],
        st.session_state.filters['program_level'],
        st.session_state.filters['field'],
        st.session_state.filters['institution_type'],
        st.session_state.filters['tuition_min'],
        st.session_state.filters['tuition_max'],
        st.session_state.search_query
    )

    # Pagination setup
    items_per_page = 24
    total_pages = math.ceil(len(filtered_data) / items_per_page)

    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    # Display universities
    for i in range(0, len(filtered_data[start_idx:end_idx]), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(filtered_data[start_idx:end_idx]):
                row = filtered_data.iloc[start_idx + i + j]
                with cols[j]:
                    st.markdown(f'''
                        <div class="university-card">
                            <div class="university-header">
                                <img src="{row['Picture']}" class="university-logo" alt="{row['University Name']} logo">
                                <div class="university-name">{row['University Name']}</div>
                            </div>
                            <div class="speciality-container">
                                <div class="speciality-name" data-full-text="{row['Speciality']}">🎯 {row['Speciality']}</div>
                            </div>
                            <div class="info-container">
                                <div class="info-row">
                                    <span><span class="emoji-icon">📍</span>Location:</span>
                                    <span>{row['City']}, {row['Country']}</span>
                                </div>
                                <div class="info-row">
                                    <span><span class="emoji-icon">💰</span>Tuition:</span>
                                    <span>${row['Tuition Price']:,.0f} {row['Tuition Currency']}/Year</span>
                                </div>
                                <div class="info-row">
                                    <span><span class="emoji-icon">📝</span>Application Fee:</span>
                                    <span>${row['Application Fee Price']:,.0f} {row['Application Fee Currency']}</span>
                                </div>
                                <div class="info-row">
                                    <span><span class="emoji-icon">⏳</span>Duration:</span>
                                    <span>{row['Duration']}</span>
                                </div>
                                <!-- Updated Level row with hover feature for long texts -->
                                <div class="info-row level-container">
                                    <span><span class="emoji-icon">🎓</span>
                                    <span class="level-name" data-full-text="{row['Level']}">{row['Level']}</span></span>
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
        st.markdown(f'<div style="text-align: center; color: #4b5563;">Page {st.session_state.current_page} of {total_pages}</div>', unsafe_allow_html=True)
    with col3:
        if st.session_state.current_page < total_pages:
            if st.button("Next ▶"):
                st.session_state.current_page += 1
                st.rerun()

if __name__ == "__main__":
    main()
