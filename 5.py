import streamlit as st
import pickle
import time
import streamlit.components.v1 as components
import math
from datetime import datetime
import pytz

# Page config
st.set_page_config(page_title="AQI Predictor", page_icon="🌿", layout="centered")

# --- Current Location & Time Logic ---
INDIA_TIMEZONE = 'Asia/Kolkata'
try:
    indian_tz = pytz.timezone(INDIA_TIMEZONE)
    now_in_india = datetime.now(indian_tz)
    current_date_time_str = now_in_india.strftime("%A, %B %d, %Y at %I:%M:%S %p %Z%z")
    current_location_str = "Kottakkal, Kerala, India"
except Exception as e:
    current_date_time_str = f"Error getting time: {e}"
    current_location_str = "Unknown Location"
# --- End Current Location & Time Logic ---

# Initialize 'color' with a default value for the CSS to prevent NameError
# This will be the default color of the needle before any prediction is made.
initial_needle_color = "#6c757d" # A neutral gray

# Enhanced CSS with blue and violet gradient, and advanced meter styling
st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto:wght@300;400;700&display=swap');

        /* Define new gradient colors */
        :root {{
            --gradient-start: #8a2be2; /* BlueViolet */
            --gradient-end: #0000ff;   /* Blue */
            --glow-color: #9370DB;     /* MediumPurple for subtle glow */
            --header-color: #58a6ff;   /* Keep a bright blue for general headers */
            --text-color: #c9d1d9;
            --background-dark: #0d1117;
            --background-medium: #161b22;
        }}

        /* General Body and Font Styling */
        html, body, .stApp {{
            font-family: 'Roboto', sans-serif;
            background-color: var(--background-dark);
            color: var(--text-color);
        }}

        /* Main Title Styling */
        .main-title {{
            font-family: 'Orbitron', sans-serif;
            text-align: center;
            color: var(--gradient-start);
            text-shadow: 0 0 15px var(--gradient-start), 0 0 30px var(--gradient-end);
            font-size: 3.5em;
            margin-bottom: 40px;
            letter-spacing: 2px;
        }}

        /* Current Time and Location */
        .time-location {{
            text-align: center;
            font-family: 'Roboto', sans-serif;
            font-size: 1.1em;
            color: #7B68EE;
            margin-bottom: 30px;
            text-shadow: 0 0 5px rgba(123, 104, 238, 0.5);
        }}

        /* Section Headers */
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Orbitron', sans-serif;
            color: var(--header-color);
            text-shadow: 0 0 8px rgba(88, 166, 255, 0.5);
            margin-top: 30px;
            margin-bottom: 15px;
        }}

        /* Info Box Styling */
        .info-box {{
            background-color: var(--background-medium);
            border: 1px solid #30363d;
            border-left: 5px solid var(--gradient-start);
            padding: 25px;
            border-radius: 8px;
            line-height: 1.7;
            color: var(--text-color);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            margin-bottom: 30px;
        }}

        /* Streamlit Input Widgets */
        .stNumberInput > label, .stButton > div > button > div > p {{
            color: var(--text-color);
            font-family: 'Roboto', sans-serif;
            font-weight: 400;
        }}

        .stNumberInput div[data-baseweb="input"] input {{
            background-color: var(--background-dark);
            border: 1px solid #30363d;
            border-radius: 5px;
            color: var(--gradient-start);
            padding: 10px;
            font-size: 1.1em;
            box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.5);
        }}

        /* Streamlit Button Styling */
        .stButton button {{
            background-image: linear-gradient(to right, var(--gradient-start), var(--gradient-end));
            color: var(--background-dark);
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
            padding: 12px 30px;
            border-radius: 8px;
            border: none;
            box-shadow: 0 0 15px var(--glow-color), 0 0 30px var(--glow-color), 0 0 45px var(--glow-color);
            transition: all 0.3s ease-in-out;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 20px;
        }}

        .stButton button:hover {{
            background-image: linear-gradient(to left, var(--gradient-start), var(--gradient-end));
            box-shadow: 0 0 20px var(--header-color), 0 0 40px var(--header-color);
            transform: translateY(-2px);
        }}

        /* Prediction Result Styling */
        .prediction-result {{
            font-family: 'Orbitron', sans-serif;
            text-align: center;
            margin-top: 40px;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(138, 43, 226, 0.5), 0 0 40px rgba(0, 0, 255, 0.3);
            background-color: var(--background-medium);
            border: 1px solid var(--gradient-start);
        }}

        .prediction-result h3 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            letter-spacing: 1.5px;
        }}

        /* Tree Animation - Now a full forest */
        .tree-animation-container {{
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 400px;
            overflow: hidden;
            z-index: -1;
            display: flex;
            justify-content: center;
            align-items: flex-end;
        }}

        .animated-tree {{
            height: 0;
            opacity: 0;
            animation: growTree 8s ease-out forwards;
            position: absolute;
            bottom: 0;
        }}

        /* Keyframes for the growing tree effect */
        @keyframes growTree {{
            0% {{ height: 0; opacity: 0; transform: translateY(100px); }}
            50% {{ opacity: 0.5; }}
            100% {{ height: 350px; opacity: 1; transform: translateY(0); }}
        }}

        /* Analog Meter SVG Styling - Enlarged and Enhanced */
        .analog-meter-container {{
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 40px;
            margin-bottom: 60px;
        }}

        .meter-svg {{
            width: 500px; /* Slightly larger */
            height: 300px; /* Adjust height accordingly */
            background-color: var(--background-medium);
            border-radius: 15px;
            box-shadow: 0 0 30px rgba(138, 43, 226, 0.6), 0 0 60px rgba(0, 0, 255, 0.4);
            border: 2px solid var(--gradient-start);
            padding: 20px; /* Add some padding inside the SVG container */
        }}

        .meter-dial {{
            stroke: #30363d;
            stroke-width: 10;
        }}

        /* AQI Arc Segments */
        .meter-arc-segment {{
            stroke-width: 30; /* Thicker arcs */
            filter: url(#glow);
            animation: shimmer 2s infinite alternate ease-in-out;
        }}

        /* Define individual glow filters for each color */
        .glow-good {{
            filter: drop-shadow(0 0 10px #00FF00) drop-shadow(0 0 20px rgba(0,255,0,0.6));
        }}
        .glow-moderate {{
            filter: drop-shadow(0 0 10px #ADFF2F) drop-shadow(0 0 20px rgba(173,255,47,0.6));
        }}
        .glow-sensitive {{
            filter: drop-shadow(0 0 10px #FFA500) drop-shadow(0 0 20px rgba(255,165,0,0.6));
        }}
        .glow-unhealthy {{
            filter: drop-shadow(0 0 10px #FF4500) drop-shadow(0 0 20px rgba(255,69,0,0.6));
        }}
        .glow-very-unhealthy {{
            filter: drop-shadow(0 0 10px #FF1493) drop-shadow(0 0 20px rgba(255,20,147,0.6));
        }}
        .glow-hazardous {{
            filter: drop-shadow(0 0 10px #8B0000) drop-shadow(0 0 20px rgba(139,0,0,0.6));
        }}

        /* Shimmer Animation */
        @keyframes shimmer {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
            100% {{ opacity: 1; }}
        }}

        .meter-needle {{
            stroke-width: 8;
            transition: stroke 0.5s ease-in-out, transform 0.5s ease-in-out;
            stroke-linecap: round;
            transform-origin: center center;
            /* Default color for the needle before prediction */
            stroke: {initial_needle_color};
        }}

        .meter-center {{
            fill: var(--text-color);
            stroke: var(--gradient-start);
            stroke-width: 3;
            r: 10;
        }}

        .meter-text {{
            fill: var(--text-color);
            font-family: 'Orbitron', sans-serif;
            font-size: 1.5em;
            text-anchor: middle;
        }}

        .aqi-value-display {{
            fill: var(--header-color);
            font-family: 'Orbitron', sans-serif;
            font-size: 3.5em;
            font-weight: bold;
            text-anchor: middle;
            text-shadow: 0 0 15px var(--header-color), 0 0 25px rgba(88, 166, 255, 0.7);
            animation: pulse 1.5s infinite alternate;
        }}

        @keyframes pulse {{
            0% {{ transform: scale(1); opacity: 1; }}
            100% {{ transform: scale(1.05); opacity: 0.9; }}
        }}

        /* Specific AQI color styles for result text - These remain based on AQI health levels */
        .aqi-good {{ color: #00FF00; text-shadow: 0 0 10px rgba(0,255,0,0.5); }}
        .aqi-moderate {{ color: #ADFF2F; text-shadow: 0 0 10px rgba(173,255,47,0.5); }}
        .aqi-sensitive {{ color: #FFA500; text-shadow: 0 0 10px rgba(255,165,0,0.5); }}
        .aqi-unhealthy {{ color: #FF4500; text-shadow: 0 0 10px rgba(255,69,0,0.5); }}
        .aqi-very-unhealthy {{ color: #FF1493; text-shadow: 0 0 10px rgba(255,20,147,0.5); }}
        .aqi-hazardous {{ color: #8B0000; text-shadow: 0 0 10px rgba(139,0,0,0.5); }}
        .aqi-no-data {{ color: #FFFFFF; text-shadow: 0 0 10px rgba(255,255,255,0.5); }}

        /* AQI Level Labels around the meter */
        .aqi-label {{
            font-family: 'Roboto', sans-serif;
            font-size: 0.8em;
            font-weight: bold;
            text-anchor: middle;
        }}
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1 class='main-title'>🌿 AIR QUALITY INDEX PREDICTION</h1>", unsafe_allow_html=True)

# Display current time and location
st.markdown(f"<p class='time-location'>Current Location: {current_location_str}</p>", unsafe_allow_html=True)
st.markdown(f"<p class='time-location'>Current Time: {current_date_time_str}</p>", unsafe_allow_html=True)


# About Section
st.markdown("### About the Project")
st.markdown("""
<div class='info-box'>
    Air pollution is one of the most critical environmental issues impacting human health and ecosystems globally.
    <br><br>
    This project utilizes advanced Machine Learning techniques to accurately predict the Air Quality Index (AQI)
    based on real-time pollutant concentration data from Continuous Ambient Air Quality Monitoring Stations (CAAQMS)
    across Kerala, India. Our aim is to provide timely and actionable insights into air quality, empowering
    users with critical environmental information.
</div>
""", unsafe_allow_html=True)

# Load Model
@st.cache_resource
def load_model():
    """Loads the pre-trained machine learning model."""
    try:
        with open("li.pkl", 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        st.error("Model file 'li.pkl' not found. Please ensure it's in the same directory.")
        return None
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

classifier = load_model()

# Inputs
st.markdown("### 📊 Enter Pollutant Concentrations:")

# Using columns for better layout of inputs
col1, col2 = st.columns(2)

with col1:
    PM25 = st.number_input("PM2.5 (µg/m³)", min_value=0.0, help="Particulate Matter less than 2.5 micrometers in diameter.")
    NO2 = st.number_input("NO2 (µg/m³)", min_value=0.0, help="Nitrogen Dioxide concentration.")
    CO = st.number_input("CO (mg/m³)", min_value=0.0, help="Carbon Monoxide concentration.")

with col2:
    PM10 = st.number_input("PM10 (µg/m³)", min_value=0.0, help="Particulate Matter less than 10 micrometers in diameter.")
    SO2 = st.number_input("SO2 (µg/m³)", min_value=0.0, help="Sulfur Dioxide concentration.")
    Ozone = st.number_input("O3 (µg/m³)", min_value=0.0, help="Ozone concentration.")

# Prediction
if st.button("🔍 Predict AQI"):
    if classifier is None:
        st.warning("Prediction cannot be performed as the model failed to load.")
    else:
        try:
            input_data = [[PM25, PM10, NO2, SO2, CO, Ozone]]
            prediction = classifier.predict(input_data)
            predicted_aqi = float(prediction[0])

            # Add both balloons and snow
            st.balloons()
            st.snow()

            st.toast("🎉 Prediction complete! Analyzing air quality...", icon="🌳")

            # AQI Category & Color Mapping
            aqi_info = {
                (0, 50): ("Good ✅", "#00FF00", "aqi-good", "glow-good"),
                (51, 100): ("Moderate 🌤", "#ADFF2F", "aqi-moderate", "glow-moderate"),
                (101, 150): ("Unhealthy for Sensitive Groups ⚠", "#FFA500", "aqi-sensitive", "glow-sensitive"),
                (151, 200): ("Unhealthy 🛑", "#FF4500", "aqi-unhealthy", "glow-unhealthy"),
                (201, 300): ("Very Unhealthy ☣", "#FF1493", "aqi-very-unhealthy", "glow-very-unhealthy"),
                (301, 500): ("Hazardous ☠", "#8B0000", "aqi-hazardous", "glow-hazardous")
            }

            category, color, css_class, glow_class = "No Data / Extreme Value 💼", "#FFFFFF", "aqi-no-data", ""

            for (low, high), (cat, col, css, glow) in aqi_info.items():
                if low <= predicted_aqi <= high:
                    category, color, css_class, glow_class = cat, col, css, glow
                    break
                elif predicted_aqi > 500: # Handle values beyond 500
                    category, color, css_class, glow_class = "Hazardous ☠", "#8B0000", "aqi-hazardous", "glow-hazardous"
                    break

            st.markdown(f"""
                <div class='prediction-result'>
                    <h3 class='{css_class}'>
                        Predicted AQI: {predicted_aqi:.2f}<br>
                        Category: {category}
                    </h3>
                </div>
            """, unsafe_allow_html=True)

            # Tree growing with forest ambience
            st.markdown("""
                <div class="tree-animation-container">
                    <img class="animated-tree" style="left: 10%; animation-delay: 0s;" src="https://i.imgur.com/gK5WfC0.png" height="350px"/>
                    <img class="animated-tree" style="left: 40%; animation-delay: 1s;" src="https://i.imgur.com/gK5WfC0.png" height="300px"/>
                    <img class="animated-tree" style="left: 70%; animation-delay: 0.5s;" src="https://i.imgur.com/gK5WfC0.png" height="380px"/>
                </div>
                <audio autoplay loop>
                    <source src="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" type="audio/mpeg">
                    Your browser does not support the audio element.
                </audio>
            """, unsafe_allow_html=True)

            # Analogue Meter with advanced styling
            aqi_normalized = min(max(0, predicted_aqi), 500)

            # Adjusted for larger meter
            cx, cy = 250, 250 # Center of the SVG viewBox
            r = 180 # Radius of the main arc

            start_angle_deg = 210
            end_angle_deg = -30
            angle_range_deg = start_angle_deg - end_angle_deg

            current_angle_deg = start_angle_deg - (aqi_normalized / 500) * angle_range_deg
            current_angle_rad = math.radians(current_angle_deg)

            needle_length = r * 0.8
            needle_tail_length = r * 0.15

            # Needle coordinates
            needle_x1 = cx - needle_tail_length * math.cos(current_angle_rad)
            needle_y1 = cy - needle_tail_length * math.sin(current_angle_rad)
            needle_x2 = cx + needle_length * math.cos(current_angle_rad)
            needle_y2 = cy + needle_length * math.sin(current_angle_rad)

            meter_segments = [
                (0, 50, "#00FF00", "good", "Good"),
                (51, 100, "#ADFF2F", "moderate", "Moderate"),
                (101, 150, "#FFA500", "sensitive", "Sensitive"),
                (151, 200, "#FF4500", "unhealthy", "Unhealthy"),
                (201, 300, "#FF1493", "very-unhealthy", "Very Unhealthy"),
                (301, 500, "#8B0000", "hazardous", "Hazardous")
            ]

            arc_paths = []
            aqi_labels = []

            # Function to calculate arc path (taken from your original code)
            def polarToCartesian(centerX, centerY, radius, angleInDegrees):
                angleInRadians = (angleInDegrees - 90) * math.pi / 180.0
                return centerX + (radius * math.cos(angleInRadians)), centerY + (radius * math.sin(angleInRadians))

            for start_aqi, end_aqi, seg_color, seg_class, label_text in meter_segments:
                seg_start_angle_deg = start_angle_deg - (start_aqi / 500) * angle_range_deg
                seg_end_angle_deg = start_angle_deg - (end_aqi / 500) * angle_range_deg

                # Corrected calculation for SVG arcs (using your original function)
                # For a sweep flag of 0, start_angle_deg should be greater than end_angle_deg
                x1, y1 = polarToCartesian(cx, cy, r, seg_start_angle_deg - 90) # Adjust for polarToCartesian
                x2, y2 = polarToCartesian(cx, cy, r, seg_end_angle_deg - 90)   # Adjust for polarToCartesian

                # Adjust large_arc_flag and sweep_flag for accurate arc drawing
                large_arc_flag = 1 if abs(seg_end_angle_deg - seg_start_angle_deg) > 180 else 0
                sweep_flag = 0 if seg_end_angle_deg < seg_start_angle_deg else 1 # Ensure correct sweep direction

                path_d = f"M {x1:.3f} {y1:.3f} A {r} {r} 0 {large_arc_flag} {sweep_flag} {x2:.3f} {y2:.3f}"
                arc_paths.append(f'<path d="{path_d}" fill="none" stroke="{seg_color}" class="meter-arc-segment {glow_class}"/>')

                # Add labels for each segment
                mid_aqi = (start_aqi + end_aqi) / 2
                label_angle_deg = start_angle_deg - (mid_aqi / 500) * angle_range_deg
                label_angle_rad = math.radians(label_angle_deg)
                label_r = r + 30 # Distance of label from center

                label_x = cx + label_r * math.cos(label_angle_rad)
                label_y = cy - label_r * math.sin(label_angle_rad) # Y-axis inverted for SVG

                aqi_labels.append(f'<text x="{label_x:.1f}" y="{label_y:.1f}" class="aqi-label" fill="{seg_color}">{label_text}</text>')

            all_arcs_svg = "\n".join(arc_paths)
            all_labels_svg = "\n".join(aqi_labels)

            components.html(f"""
                <div class="analog-meter-container">
                    <svg class="meter-svg" viewBox="0 0 500 300">
                        <circle cx="250" cy="250" r="180" class="meter-dial" />

                        <defs>
                            <filter id="glow">
                                <feGaussianBlur in="SourceGraphic" stdDeviation="6" result="blur" />
                                <feColorMatrix in="blur" mode="matrix" values="
                                    1 0 0 0 0
                                    0 1 0 0 0
                                    0 0 1 0 0
                                    0 0 0 15 0" result="colormatrix" />
                                <feMerge>
                                    <feMergeNode in="colormatrix" />
                                    <feMergeNode in="SourceGraphic" />
                                </feMerge>
                            </filter>
                        </defs>

                        {all_arcs_svg}

                        <line x1="{needle_x1:.1f}" y1="{needle_y1:.1f}" x2="{needle_x2:.1f}" y2="{needle_y2:.1f}" stroke="{color}" class="meter-needle" />

                        <circle cx="{cx}" cy="{cy}" r="12" class="meter-center" />

                        <text x="250" y="270" class="meter-text">AQI</text>

                        <text x="250" y="220" class="aqi-value-display">{predicted_aqi:.0f}</text>

                        {all_labels_svg}

                        <text x="70" y="250" fill="#00FF00" font-size="1em" font-family="Orbitron, sans-serif" text-anchor="middle">0</text>
                        <text x="430" y="250" fill="#8B0000" font-size="1em" font-family="Orbitron, sans-serif" text-anchor="middle">500+</text>

                    </svg>
                </div>
            """, height=350)

        except Exception as e:
            st.error(f"An error occurred during prediction: {e}. Please ensure all inputs are valid numbers.")

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: var(--header-color); font-family: 'Roboto', sans-serif; font-size: 0.9em; margin-top: 30px;'>"
    "Developed by JINU,SANJAY AND ABHIRAM."
    "</div>",
    unsafe_allow_html=True
)