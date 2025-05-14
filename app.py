import streamlit as st
import pandas as pd
import time 
from datetime import datetime
import os
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# Page config with custom theme
st.set_page_config(
    page_title="Face Recognition Attendance System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stDataFrame {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1 {
        color: #1f77b4;
        padding-bottom: 20px;
    }
    h2 {
        color: #2c3e50;
        padding: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title and header
st.title("🎓 Face Recognition Attendance System")

# Sidebar
with st.sidebar:
    st.header("System Controls")
    st.info("ℹ️ Instructions:\n1. Run test.py to start face recognition\n2. Press 'O' to mark attendance\n3. Press 'Q' to quit")
    if st.button("📝 Download Attendance Report"):
        # TODO: Implement report download
        pass

# Auto refresh setup
st_autorefresh(interval=2000, limit=None, key="attendance_refresh")

# Get current date and time
ts = time.time()
date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
current_time = datetime.fromtimestamp(ts).strftime("%H:%M:%S")

# Create Attendance directory if it doesn't exist
if not os.path.exists("Attendance"):
    os.makedirs("Attendance")

# Load and display attendance data
attendance_file = f"Attendance/Attendance_{date}.csv"

try:
    if os.path.exists(attendance_file):
        df = pd.read_csv(attendance_file)
        
        # Top metrics
        st.markdown("### 📊 Today's Overview")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📅 Date", date)
        with col2:
            st.metric("⏰ Time", current_time)
        with col3:
            st.metric("👥 Total Students", len(df))
        with col4:
            present_count = len(df[df['Status'] == 'Present']) if 'Status' in df.columns else len(df)
            st.metric("✅ Present Students", present_count)
            
        # Attendance Timeline
        st.markdown("### 📈 Attendance Timeline")
        df['TIME'] = pd.to_datetime(df['TIME'], format='%H:%M-%S', errors='coerce')
        df['DATE'] = date
        df['Hour'] = df['TIME'].dt.hour
        hourly_counts = df.groupby('Hour').size().reset_index(name='Count')
        fig = px.line(hourly_counts, x='Hour', y='Count', 
                     title='Attendance Pattern Throughout the Day',
                     labels={'Count': 'Number of Students', 'Hour': 'Hour of Day'})
        fig.update_layout(
            xaxis=dict(tickmode='linear', tick0=0, dtick=1),
            plot_bgcolor='white'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Attendance Table
        st.markdown("### 📋 Attendance Records")
        df_display = df.copy()
        df_display['Serial No.'] = range(1, len(df_display) + 1)
        df_display = df_display[['Serial No.', 'NAME', 'TIME']]

        # Format time to show only HH:MM (without date and seconds)
        df_display['TIME'] = df_display['TIME'].apply(
            lambda x: x.strftime("%H:%M") if not pd.isna(x) else x
        )

        st.dataframe(
            df_display.style.highlight_max(axis=0)
            .set_properties(**{'background-color': 'white',
                            'color': 'black',
                            'border-color': 'lightgrey'}),
            use_container_width=True
        )
        
    else:
        st.warning("🔍 No attendance records found for today. Start the face recognition system (test.py) to begin recording attendance.")
        
        # Placeholder visualization
        st.markdown("### 📈 Preview")
        df_example = pd.DataFrame({
            'Hour': range(9, 18),
            'Count': [0] * 9
        })
        fig = px.line(df_example, x='Hour', y='Count',
                     title='Attendance Pattern Throughout the Day (No Data Yet)',
                     labels={'Count': 'Number of Students', 'Hour': 'Hour of Day'})
        fig.update_layout(
            xaxis=dict(tickmode='linear', tick0=0, dtick=1),
            plot_bgcolor='white'
        )
        st.plotly_chart(fig, use_container_width=True)
        
except Exception as e:
    st.error(f"⚠️ Error loading attendance data: {str(e)}")
    st.info("💡 Make sure the face recognition system is running and attendance is being recorded.")