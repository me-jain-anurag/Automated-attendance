import streamlit as st
import pandas as pd
import time 
from datetime import datetime
import os

# Set page config
st.set_page_config(
    page_title="Face Recognition Attendance System",
    layout="wide"
)

# Title and description
st.title("Face Recognition Attendance System")
st.markdown("---")

# Get current date and time
ts = time.time()
date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
timestamp = datetime.fromtimestamp(ts).strftime("%H:%M-%S")

# Auto refresh setup
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=2000, limit=None, key="attendance_refresh")

# Create Attendance directory if it doesn't exist
if not os.path.exists("Attendance"):
    os.makedirs("Attendance")

# Load and display attendance data
attendance_file = f"Attendance/Attendance_{date}.csv"

try:
    if os.path.exists(attendance_file):
        df = pd.read_csv(attendance_file)
        
        # Display statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Date", date)
        with col2:
            st.metric("Total Students", len(df))
        with col3:
            present_count = len(df[df['Status'] == 'Present']) if 'Status' in df.columns else len(df)
            st.metric("Present Students", present_count)
        
        # Display attendance table
        st.subheader("Today's Attendance")
        st.dataframe(df.style.highlight_max(axis=0), use_container_width=True)
        
    else:
        st.info("No attendance records found for today. Start the face recognition system (test.py) to begin recording attendance.")
        
except Exception as e:
    st.error(f"Error loading attendance data: {str(e)}")
    st.info("Make sure the face recognition system is running and attendance is being recorded.")