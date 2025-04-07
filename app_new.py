from dotenv import load_dotenv
import os
import streamlit as st
from assistant.assistant import listen, speak, get_weather, send_email, open_app
import json
from datetime import datetime, timedelta
import platform
import psutil
import webbrowser
import pickle
from pathlib import Path
import subprocess
import time
import socket
import requests
import sys

# Load environment variables first
load_dotenv()

# Configure Streamlit settings for better performance
st.set_page_config(
    page_title="JeevaAI - Your Smart Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/JeevaAI',
        'Report a bug': 'https://github.com/yourusername/JeevaAI/issues',
        'About': 'JeevaAI - Your Smart Assistant'
    }
)

# Add custom CSS for better UI
st.markdown("""
    <style>
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
        margin: 0 auto;
        background-color: #121212;
        color: #ffffff;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1e1e1e;
        padding: 2rem 1rem;
        color: #ffffff;
    }
    
    /* Sidebar navigation */
    .stRadio > div {
        background-color: #2d2d2d;
        padding: 1rem;
        border-radius: 8px;
        color: #ffffff;
    }
    
    /* Buttons */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
        transition: all 0.3s ease;
        background-color: #2d2d2d;
        color: #ffffff;
        border: 2px solid #404040;
    }
    
    .stButton > button:hover {
        background-color: #404040;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 2px solid #404040;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
        background-color: #2d2d2d;
        color: #ffffff;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #666666;
        box-shadow: 0 0 0 2px rgba(102, 102, 102, 0.2);
    }
    
    /* Select boxes */
    .stSelectbox > div > div > div {
        border-radius: 8px;
        border: 2px solid #404040;
        background-color: #2d2d2d;
        color: #ffffff;
    }
    
    /* Cards */
    .card {
        background-color: #2d2d2d;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        border: 1px solid #404040;
        color: #ffffff;
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Loading spinner */
    .stSpinner > div {
        width: 3rem;
        height: 3rem;
        border-width: 3px;
        border-color: #666666;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff;
        margin-bottom: 1rem;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 8px;
        padding: 1rem;
        background-color: #2d2d2d;
        border: 1px solid #404040;
        color: #ffffff;
    }
    
    /* Success messages */
    .stSuccess {
        background-color: #2d2d2d;
        color: #4CAF50;
        border: 1px solid #404040;
    }
    
    /* Error messages */
    .stError {
        background-color: #2d2d2d;
        color: #f44336;
        border: 1px solid #404040;
    }
    
    /* Warning messages */
    .stWarning {
        background-color: #2d2d2d;
        color: #ff9800;
        border: 1px solid #404040;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
        
        .stColumn {
            width: 100% !important;
            padding: 0.5rem;
        }
        
        [data-testid="stSidebar"] {
            padding: 1rem 0.5rem;
        }
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #2d2d2d;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #666666;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #808080;
    }

    /* Text color */
    p, div, span {
        color: #ffffff;
    }

    /* Links */
    a {
        color: #808080;
    }

    a:hover {
        color: #ffffff;
    }

    /* Code blocks */
    pre {
        background-color: #2d2d2d;
        border: 1px solid #404040;
        border-radius: 8px;
        padding: 1rem;
    }

    /* Tables */
    table {
        background-color: #2d2d2d;
        border: 1px solid #404040;
    }

    th, td {
        border: 1px solid #404040;
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# Connection management with retry mechanism
def check_internet_connection(retries=3, timeout=5):
    """Check internet connection with multiple reliable servers and retries"""
    servers = [
        ("8.8.8.8", 53),  # Google DNS
        ("1.1.1.1", 53),  # Cloudflare DNS
        ("208.67.222.222", 53)  # OpenDNS
    ]
    
    for attempt in range(retries):
        try:
            for server in servers:
                try:
                    socket.create_connection(server, timeout=timeout)
                    return True
                except:
                    continue
            time.sleep(1)  # Wait before next retry
        except Exception as e:
            if attempt == retries - 1:
                return False
            time.sleep(1)
    return False

def check_local_connection(retries=3, timeout=2):
    """Check local connection with multiple ports and retries"""
    ports = [8501, 8502, 8503]  # Common Streamlit ports
    
    for attempt in range(retries):
        try:
            for port in ports:
                try:
                    socket.create_connection(("localhost", port), timeout=timeout)
                    return True
                except:
                    continue
            time.sleep(1)  # Wait before next retry
        except Exception as e:
            if attempt == retries - 1:
                return False
            time.sleep(1)
    return False

# Main application code
try:
    # Check connections with retry
    with st.spinner("Checking connections..."):
        local_connected = check_local_connection()
        internet_connected = check_internet_connection()

    if not local_connected:
        st.error("""
        ⚠️ Local connection error!
        
        Please try the following:
        1. Refresh the page
        2. Check if the application is running
        3. Try a different browser
        4. Restart the application
        
        If the problem persists:
        1. Check your firewall settings
        2. Make sure no other application is using port 8501
        3. Try running the application with administrator privileges
        """)
        st.stop()

    # Initialize session state for tasks if it doesn't exist
    if 'tasks' not in st.session_state:
        st.session_state.tasks = []
        try:
            if os.path.exists('tasks.pkl'):
                with open('tasks.pkl', 'rb') as f:
                    st.session_state.tasks = pickle.load(f)
        except Exception as e:
            st.warning("Could not load saved tasks. Starting with empty task list.")

    # Task categories
    CATEGORIES = ["Work", "Personal", "Shopping", "Health", "Education", "Other"]

    # Add loading spinner for initial load
    with st.spinner("Loading JeevaAI..."):
        time.sleep(0.5)  # Simulate loading time

    # Main content with better layout
    st.title("🤖 JeevaAI")
    st.markdown("""
    <div style='background-color: #2d2d2d; padding: 10px; border-radius: 10px; margin: 10px 0;'>
        <p style='color: #ffffff; font-style: italic; text-align: center;'>
            Your intelligent companion for a smarter digital life
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Feature selection with better UI
    selected_feature = st.sidebar.radio(
        "Select a feature:",
        ["Task Manager", "Weather", "Email Sender", "File Explorer", "System Info", "App Launcher"],
        format_func=lambda x: f"📌 {x}",  # Add emoji to each option
        key="feature_selector"
    )

    # Add a divider for better visual separation
    st.markdown("---")

    # Container for main content
    with st.container():
        if selected_feature == "Task Manager":
            st.markdown("""
            <div style='background-color: #2d2d2d; padding: 20px; border-radius: 10px; margin: 20px 0;'>
                <h2 style='color: #ffffff; margin-bottom: 15px;'>📝 Task Manager</h2>
                <p style='color: #ffffff;'>Organize and manage your daily tasks efficiently. Add, complete, and track your tasks with ease.</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.spinner("Loading Task Manager..."):
                # Task filters
                col1, col2, col3 = st.columns(3)
                with col1:
                    filter_category = st.selectbox("Filter by Category", ["All"] + CATEGORIES)
                with col2:
                    filter_priority = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])
                with col3:
                    filter_status = st.selectbox("Filter by Status", ["All", "Active", "Completed"])

                # Add new task form
                with st.expander("➕ Add New Task", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        new_task = st.text_input("Task Description:")
                    with col2:
                        priority = st.selectbox("Priority", ["High", "Medium", "Low"], key="priority")
                    with col3:
                        category = st.selectbox("Category", CATEGORIES, key="category")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        due_date = st.date_input("Due Date", min_value=datetime.now().date())
                    with col2:
                        due_time = st.time_input("Due Time", value=datetime.now().time())

                    if st.button("Add Task"):
                        if new_task:
                            task = {
                                "task": new_task,
                                "priority": priority,
                                "category": category,
                                "due_date": datetime.combine(due_date, due_time).strftime("%Y-%m-%d %H:%M"),
                                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "completed": False
                            }
                            st.session_state.tasks.append(task)
                            # Save tasks to file
                            with open('tasks.pkl', 'wb') as f:
                                pickle.dump(st.session_state.tasks, f)
                            st.success("Task added successfully!")

        elif selected_feature == "Weather":
            st.markdown("""
            <div style='background-color: #2d2d2d; padding: 20px; border-radius: 10px; margin: 20px 0;'>
                <h2 style='color: #ffffff; margin-bottom: 15px;'>🌦️ Weather Updates</h2>
                <p style='color: #ffffff;'>Get real-time weather information for any location. Check temperature, conditions, and forecasts to plan your day better.</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.spinner("Loading Weather..."):
                with st.container():
                    city = st.text_input("Enter city name:")
                    if st.button("Get Weather"):
                        if city:
                            with st.spinner("Fetching weather data..."):
                                weather_data = get_weather(city)
                            if isinstance(weather_data, dict):
                                st.write(f"### Weather in {city}")
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Temperature:** {weather_data['temperature']}°C")
                                    st.write(f"**Feels Like:** {weather_data['feels_like']}°C")
                                    st.write(f"**Condition:** {weather_data['condition']}")
                                    st.write(f"**Humidity:** {weather_data['humidity']}%")
                                    st.write(f"**Cloud Cover:** {weather_data['cloud_cover']}%")
                                with col2:
                                    st.write(f"**Wind Speed:** {weather_data['wind_speed']} km/h")
                                    st.write(f"**Pressure:** {weather_data['pressure']} hPa")
                                    st.write(f"**Visibility:** {weather_data['visibility']} km")
                                    st.write(f"**Precipitation:** {weather_data['precipitation']} mm")
                            else:
                                st.error(weather_data)
                        else:
                            st.warning("Please enter a city name")

        elif selected_feature == "Email Sender":
            st.markdown("""
            <div style='background-color: #2d2d2d; padding: 20px; border-radius: 10px; margin: 20px 0;'>
                <h2 style='color: #ffffff; margin-bottom: 15px;'>📧 Email Sender</h2>
                <p style='color: #ffffff;'>Send emails quickly and efficiently. Compose and send messages to any email address with just a few clicks.</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.spinner("Loading Email Sender..."):
                with st.container():
                    to = st.text_input("To")
                    subject = st.text_input("Subject")
                    body = st.text_area("Message")
                    if st.button("Send Email"):
                        with st.spinner("Preparing email..."):
                            result = send_email(to, subject, body)
                            st.success(result)

        elif selected_feature == "File Explorer":
            st.markdown("""
            <div style='background-color: #2d2d2d; padding: 20px; border-radius: 10px; margin: 20px 0;'>
                <h2 style='color: #ffffff; margin-bottom: 15px;'>📂 File Explorer</h2>
                <p style='color: #ffffff;'>Browse and manage your files with ease. Open files and folders directly from the application.</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.spinner("Loading File Explorer..."):
                with st.container():
                    st.info("""
                    💡 **Path Format Tips:**
                    - Use double backslashes: `C:\\Users\\parag\\OneDrive\\Documents\\shivani bio.pdf`
                    - Or use forward slashes: `C:/Users/parag/OneDrive/Documents/shivani bio.pdf`
                    - Make sure the file exists at the specified path
                    """)

                    path = st.text_input("Enter a file or folder path:")
                    if st.button("Open", key="open_file_explorer"):
                        if path:
                            try:
                                # Convert forward slashes to backslashes for Windows
                                if platform.system() == "Windows":
                                    path = path.replace('/', '\\')
                                
                                # Normalize the path
                                normalized_path = os.path.normpath(path)
                                
                                # Check if path exists
                                if not os.path.exists(normalized_path):
                                    st.error(f"Path not found: {normalized_path}")
                                    st.info("""
                                    Common issues:
                                    1. Check if the file/folder exists
                                    2. Verify the path is correct
                                    3. Try copying the path from File Explorer
                                    4. Make sure you have permission to access the file/folder
                                    """)
                                else:
                                    if os.path.isfile(normalized_path):
                                        # If it's a file, open it with the default application
                                        if platform.system() == "Windows":
                                            os.startfile(normalized_path)
                                        else:
                                            subprocess.call(["open", normalized_path])
                                        st.success(f"Opened file: {normalized_path}")
                                    elif os.path.isdir(normalized_path):
                                        # If it's a directory, open it in File Explorer
                                        if platform.system() == "Windows":
                                            os.system(f'explorer "{normalized_path}"')
                                        else:
                                            subprocess.call(["open", normalized_path])
                                        st.success(f"Opened folder: {normalized_path}")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                                st.info("""
                                Troubleshooting steps:
                                1. Try using the full path
                                2. Check if the file is not in use by another program
                                3. Make sure you have the necessary permissions
                                4. Try restarting the application
                                """)
                        else:
                            st.warning("Please enter a valid path")

        elif selected_feature == "System Info":
            st.markdown("""
            <div style='background-color: #2d2d2d; padding: 20px; border-radius: 10px; margin: 20px 0;'>
                <h2 style='color: #ffffff; margin-bottom: 15px;'>💻 System Information</h2>
                <p style='color: #ffffff;'>Monitor your system's performance and resources. Get detailed information about CPU, memory, disk usage, and more.</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.spinner("Loading System Information..."):
                with st.container():
                    
                    # System Overview
                    st.write("### System Overview")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Operating System:**")
                        st.write(f"- System: {platform.system()} {platform.release()}")
                        st.write(f"- Version: {platform.version()}")
                        st.write(f"- Machine: {platform.machine()}")
                        st.write(f"- Processor: {platform.processor()}")
                        st.write(f"- Python Version: {platform.python_version()}")
                        st.write(f"- Architecture: {platform.architecture()[0]}")
                    
                    with col2:
                        st.write("**System Resources:**")
                        # CPU Information
                        st.write("**CPU:**")
                        st.write(f"- Usage: {psutil.cpu_percent()}%")
                        st.write(f"- Cores: {psutil.cpu_count()} (Physical: {psutil.cpu_count(logical=False)})")
                        st.write(f"- Frequency: {psutil.cpu_freq().current:.2f} MHz")
                        
                        # Memory Information
                        memory = psutil.virtual_memory()
                        st.write("**Memory:**")
                        st.write(f"- Total: {memory.total / (1024**3):.2f} GB")
                        st.write(f"- Available: {memory.available / (1024**3):.2f} GB")
                        st.write(f"- Used: {memory.used / (1024**3):.2f} GB")
                        st.write(f"- Usage: {memory.percent}%")
                    
                    # Disk Information
                    st.write("### Disk Information")
                    try:
                        if platform.system() == "Windows":
                            partitions = psutil.disk_partitions()
                            for partition in partitions:
                                try:
                                    usage = psutil.disk_usage(partition.mountpoint)
                                    st.write(f"**Drive {partition.device}:**")
                                    st.write(f"- Total: {usage.total / (1024**3):.2f} GB")
                                    st.write(f"- Used: {usage.used / (1024**3):.2f} GB")
                                    st.write(f"- Free: {usage.free / (1024**3):.2f} GB")
                                    st.write(f"- Usage: {usage.percent}%")
                                    st.write(f"- File System: {partition.fstype}")
                                except:
                                    continue
                        else:
                            usage = psutil.disk_usage('/')
                            st.write("**Root Partition:**")
                            st.write(f"- Total: {usage.total / (1024**3):.2f} GB")
                            st.write(f"- Used: {usage.used / (1024**3):.2f} GB")
                            st.write(f"- Free: {usage.free / (1024**3):.2f} GB")
                            st.write(f"- Usage: {usage.percent}%")
                    except Exception as e:
                        st.error(f"Error getting disk information: {str(e)}")
                    
                    # Network Information
                    st.write("### Network Information")
                    try:
                        net_io = psutil.net_io_counters()
                        st.write("**Network Usage:**")
                        st.write(f"- Bytes Sent: {net_io.bytes_sent / (1024**2):.2f} MB")
                        st.write(f"- Bytes Received: {net_io.bytes_recv / (1024**2):.2f} MB")
                        st.write(f"- Packets Sent: {net_io.packets_sent}")
                        st.write(f"- Packets Received: {net_io.packets_recv}")
                    except Exception as e:
                        st.error(f"Error getting network information: {str(e)}")
                    
                    # Battery Information (if available)
                    try:
                        battery = psutil.sensors_battery()
                        if battery:
                            st.write("### Battery Information")
                            st.write(f"- Percentage: {battery.percent}%")
                            st.write(f"- Power Plugged: {'Yes' if battery.power_plugged else 'No'}")
                            if battery.secsleft != -1:
                                st.write(f"- Time Left: {battery.secsleft // 3600} hours {(battery.secsleft % 3600) // 60} minutes")
                    except:
                        pass

        elif selected_feature == "App Launcher":
            st.markdown("""
            <div style='background-color: #2d2d2d; padding: 20px; border-radius: 10px; margin: 20px 0;'>
                <h2 style='color: #ffffff; margin-bottom: 15px;'>🚀 App Launcher</h2>
                <p style='color: #ffffff;'>Launch your favorite applications quickly. Access frequently used programs with a single click.</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.spinner("Loading App Launcher..."):
                with st.container():
                    st.info("""
                    💡 **Available Apps:**
                    - Notepad: For text editing
                    - Calculator: For calculations
                    - Paint: For drawing
                    - Command Prompt: For command line operations
                    - File Explorer: To browse files
                    """)
                    
                    app_options = {
                        "Notepad": "notepad",
                        "Calculator": "calc",
                        "Paint": "mspaint",
                        "Command Prompt": "cmd",
                        "File Explorer": "explorer"
                    }
                    
                    selected_app = st.selectbox("Select an application to open:", list(app_options.keys()))
                    if st.button("Open Application"):
                        with st.spinner("Preparing app launcher..."):
                            try:
                                result = open_app(app_options[selected_app])
                                st.success(f"Successfully opened {selected_app}!")
                            except Exception as e:
                                st.error(f"Failed to open {selected_app}: {str(e)}")
                                st.info("""
                                Troubleshooting steps:
                                1. Make sure the application is installed on your system
                                2. Check if you have permission to open the application
                                3. Try running the application manually first
                                """)

    # Add a footer with better styling
    st.markdown("---")
    st.markdown("""
    <div style='
        text-align: center;
        padding: 2rem 0;
        color: #666;
        font-size: 0.9rem;
    '>
        <p style='margin: 0.5rem 0;'>Made with ❤️ by JeevaAI Team</p>
        <p style='margin: 0.5rem 0;'>Version 1.0.0</p>
        <p style='margin: 0.5rem 0;'>© 2024 JeevaAI. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"""
    ❌ An error occurred: {str(e)}
    
    Please try the following:
    1. Refresh the page
    2. Clear your browser cache
    3. Restart the application
    4. Check your system resources
    
    If the problem persists:
    1. Make sure all required ports are available
    2. Check your firewall settings
    3. Try running the application with administrator privileges
    """)
    st.stop() 