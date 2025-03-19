import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import requests
from dotenv import load_dotenv
from common import graphicalResponseEngine as gpe
import seaborn as sns
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static
import datetime

# --- Load Environment Variables ---
load_dotenv()
api_host = os.getenv("HOST", "api")
api_port = int(os.getenv("PORT", 8080))

# --- Load Dataset ---
data = pd.read_csv('data/df_common_app_dyn.csv')
df_common = pd.DataFrame(data)

def calculate_aqi(pm_25):
    if pm_25 <= 50:
        return "Good"
    elif pm_25 <= 100:
        return "Moderate"
    elif pm_25 <= 150:
        return "Unhealthy for Sensitive Groups"
    elif pm_25 <= 200:
        return "Unhealthy"
    elif pm_25 <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"

def get_color(pm_25):
    if pm_25 <= 50:
        return "green"
    elif pm_25 <= 100:
        return "yellow"
    elif pm_25 <= 150:
        return "orange"
    elif pm_25 <= 200:
        return "red"
    elif pm_25 <= 300:
        return "purple"
    else:
        return "brown"

# Function to plot top locations
def plot_top_locations(df, category, top_n=10):
    """Plots the top locations for a given category."""
    df_category = df[df['category'] == category]
    
    if df_category.empty:
        st.warning(f"No data available for {category}.")
        return

    location_counts = df_category['location'].value_counts().reset_index()
    location_counts.columns = ['location', 'count']
    
    # Plotting
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x='count', y='location', data=location_counts.head(top_n), palette="Blues_r", ax=ax)
    ax.set_xlabel("Frequency")
    ax.set_ylabel("Location")
    ax.set_title(f"Top {top_n} Locations with {category}")
    
    st.pyplot(fig)

# --- Constants for Navigation ---
MENU_OPTIONS = {
    "Air Quality Dashboard": "air_quality",
    "Top Impacted Location Categories": "top_locations",
    "AQI Levels Dashboard": "aqi_levels",
    "Ask AI (ft OpenAI, Pathway)": "ai_chatbot",
    "Mitigation Strategies - Pollution Sources": "mitigation_pollution",
    "Mitigation Strategies - Impacted Population": "mitigation_population"
}

# --- Sidebar Menu ---
st.sidebar.title("🌍 VAYUASSIST Menu")
option = st.sidebar.selectbox("Choose an option", list(MENU_OPTIONS.keys()))

# --- Helper Functions ---
def reset_page():
    """Reruns the Streamlit app."""
    st.rerun()

def plot_bar_chart(df, x, y, title, color='count', orientation='h'):
    """Reusable function for bar charts."""
    fig = px.bar(
        df, 
        x=x, 
        y=y, 
        orientation=orientation, 
        title=title, 
        labels={x: "Frequency", y: "Location"},
        color=color, 
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig)

def plot_pie_chart(df, values, names, title):
    """Reusable function for pie charts."""
    fig = px.pie(
        df, 
        values=values, 
        names=names, 
        title=title,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig)

def plot_seaborn_bar(df, x, y, title, top_n=10):
    """Reusable function for Seaborn bar charts."""
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=x, y=y, data=df.head(top_n), palette="Blues_r", ax=ax)
    ax.set_xlabel("Frequency")
    ax.set_ylabel("Location")
    ax.set_title(title)
    st.pyplot(fig)

# --- Main Sections ---
if MENU_OPTIONS[option] == "ai_chatbot":
    st.title("🤖 AI Chatbot")
    
    question = st.text_input(
        "Clear Answers for Clear Skies: Your Air Quality Information Hub",
        placeholder="Breathe Easy: Ask VayuAssist Anything About Air Quality"
    )

    if st.button("Submit Question"):
        if question:
            url = f'http://{api_host}:{api_port}/'
            data = {"query": question}
            
            response = requests.post(url, json=data)
            
            if response.status_code == 200:
                st.write("### 🤖 AI Response:")
                st.markdown(
                    f'<div style="padding:10px; border-radius:10px; background-color:#222831; color:#EEEEEE; font-size:1.2em;">{response.json()}</div>', 
                    unsafe_allow_html=True
                )
                
                image = gpe.extract_relevant_image_from_dropbox(question)
                if image:
                    st.image(image, caption="📊 Extracted from PDF", use_column_width=True)
            else:
                st.error(f"Failed to send data. Status: {response.status_code}")
        else:
            st.warning("Please enter a question.")

elif MENU_OPTIONS[option] == "mitigation_pollution":
    st.title("🛑 Mitigation Strategies - Pollution Sources")
    
    prompt = (
        "Describe all the Long-Term and Short-Term Measures related to "
        "Waste Burning, Construction & Demolition (C&D) Waste, Vehicle Pollution, "
        "Brick Kilns, and Industrial Pollution."
    )

    url = f'http://{api_host}:{api_port}/'
    data = {"query": prompt}
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        st.markdown(f"### 🤖 AI Response: {response.json()}")
    else:
        st.warning("Failed to fetch mitigation strategies.")

elif MENU_OPTIONS[option] == "mitigation_population":
    st.title("👥 Mitigation Strategies - Impacted Population")
    
    prompt = (
        "Describe all the Long-Term and Short-Term Measures related to "
        "Children, Women, Pregnant Women, and the Elderly."
    )

    url = f'http://{api_host}:{api_port}/'
    data = {"query": prompt}
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        st.markdown(f"### 🤖 AI Response: {response.json()}")
    else:
        st.warning("Failed to fetch mitigation strategies.")

elif MENU_OPTIONS[option] == "air_quality":
    st.title("📊 Air Quality Dashboard")
    
    st.sidebar.header("Filter Options")
    
    selected_category = st.sidebar.selectbox("Select Category", df_common['category'].unique(), key="category_filter")
    selected_location = st.sidebar.selectbox("Select Location", df_common['location'].unique(), key="location_filter")
    
    # Filter data
    df_category = df_common[df_common['category'] == selected_category]
    df_location = df_common[df_common['location'] == selected_location]
    
    # Bar chart
    st.subheader(f"Top Locations in {selected_category}")
    location_counts = df_category['location'].value_counts().reset_index()
    location_counts.columns = ['location', 'count']
    plot_bar_chart(location_counts, 'count', 'location', f"Top Locations with {selected_category}")
    
    # Pie chart
    st.subheader(f"Category Distribution in {selected_location}")
    category_counts = df_location['category'].value_counts().reset_index()
    category_counts.columns = ['category', 'count']
    plot_pie_chart(category_counts, 'count', 'category', f"Category Distribution in {selected_location}")
    
    # Data table
    st.subheader(f"Details for {selected_location}")
    st.dataframe(df_location[['category', 'description', 'pm_25', 'no2']])

if option == "Top Impacted Location":
    st.title("Top Impacted Location Categories")
    # Sidebar filters
    st.sidebar.title("Filters")
    top_n = st.sidebar.slider("Select number of top locations", min_value=5, max_value=20, value=10)
    for category in df_common['category'].unique():
        st.subheader(f"{category}")
        plot_top_locations(df_common, category, top_n)

elif MENU_OPTIONS[option] == "aqi_levels":
    st.title("🌬️ AQI Levels Dashboard")

    df_common['data_created_time'] = pd.to_datetime(df_common['data_created_time'])
    df_common['date'] = df_common['data_created_time'].dt.date
    df_common['month'] = df_common['data_created_time'].dt.to_period('M')
    df_common['AQI'] = df_common['pm_25'].apply(calculate_aqi)
    st.sidebar.title("Pollution Analysis Dashboard")

    start_date = st.sidebar.date_input("Start Date", df_common['date'].min())
    end_date = st.sidebar.date_input("End Date", df_common['date'].max())
    aggregation_level = st.sidebar.radio("Aggregation Level", ["Daily", "Monthly"])
    df_filtered = df_common[(df_common['date'] >= start_date) & (df_common['date'] <= end_date)]
    # --- BAR CHART ---
    st.subheader("Top Categories at Each Location")
    category_counts = df_filtered.groupby(['location', 'category']).size().reset_index(name='count')
    top_categories = category_counts.loc[category_counts.groupby('location')['count'].idxmax()]

    fig_bar = px.bar(
    top_categories, 
    x='location', 
    y='count', 
    color='category',
    title="Most Frequent Category at Each Location",
    labels={'count': 'Occurrences', 'location': 'Location'},
    barmode='group'
    )
    st.plotly_chart(fig_bar)

# --- SUMMARY TABLE ---
    st.subheader("Summary Table")
    summary = df_filtered.groupby('location').agg(
    top_category=('category', lambda x: x.value_counts().idxmax()),
    avg_pm25=('pm_25', 'mean'),
    AQI=('AQI', lambda x: x.value_counts().idxmax())).reset_index()
    st.dataframe(summary)

    st.subheader("PM2.5 & AQI Levels on Map")
    
    m = folium.Map(location=[28.6139, 77.2090], zoom_start=10)
    for _, row in df_filtered.iterrows():
        folium.CircleMarker(
            location=[row['lat_x'], row['long_x']],
            radius=6,
            color='red',
            fill=True,
            fill_opacity=0.7,
            popup=f"PM2.5: {row['pm_25']}, AQI: {row['AQI']}"
        ).add_to(m)

    folium_static(m)
