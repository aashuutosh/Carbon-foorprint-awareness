import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuration & Constants ---
st.set_page_config(page_title="EcoTrack: Carbon Footprint Platform", page_icon="🌍", layout="wide")

# Approximate global emission factors (kg CO2e)
EMISSION_FACTORS = {
    "car_km": 0.2,           # kg CO2e per km driven
    "transit_km": 0.05,      # kg CO2e per km on public transit
    "flight_hr": 250.0,      # kg CO2e per hour of flight
    "electricity_kwh": 0.5,  # kg CO2e per kWh (varies by grid)
    "diet": {
        "Meat-heavy": 100.0, # Monthly kg CO2e
        "Average Omnivore": 75.0,
        "Vegetarian": 50.0,
        "Vegan": 40.0
    },
    "waste_bag": 10.0        # kg CO2e per standard trash bag sent to landfill
}

# --- Helper Functions ---
def calculate_footprint(inputs):
    transport = (inputs['car_km'] * EMISSION_FACTORS['car_km']) + \
                (inputs['transit_km'] * EMISSION_FACTORS['transit_km']) + \
                (inputs['flight_hr'] * EMISSION_FACTORS['flight_hr'])
    
    energy = inputs['electricity_kwh'] * EMISSION_FACTORS['electricity_kwh']
    
    diet = EMISSION_FACTORS['diet'][inputs['diet_type']]
    
    waste = inputs['waste_bags'] * EMISSION_FACTORS['waste_bag']
    
    return transport, energy, diet, waste

def generate_insights(categories):
    # Find the highest emitting category
    max_category = max(categories, key=categories.get)
    
    st.subheader("💡 Actionable Insights")
    if max_category == "Transportation":
        st.info("**Top Emitter: Transportation**\n* Consider carpooling, biking, or switching to public transit for short trips.\n* If you fly frequently, look into carbon offset programs or virtual meetings.")
    elif max_category == "Energy":
        st.info("**Top Emitter: Home Energy**\n* Switch to LED bulbs and unplug phantom energy drainers (chargers, appliances).\n* Consider adjusting your thermostat by 1-2 degrees to save massive amounts of grid power.")
    elif max_category == "Diet":
        st.info("**Top Emitter: Diet**\n* Introducing just one or two plant-based days a week (like Meatless Mondays) can drastically cut your dietary footprint.\n* Source local produce to reduce transportation emissions.")
    else:
        st.info("**Top Emitter: Waste**\n* Start composting organic waste; it reduces methane emissions from landfills.\n* Audit your trash: switch to reusable containers and avoid single-use plastics.")

# --- Main UI ---
st.title("🌍 EcoTrack: Personal Carbon Footprint Tracker")
st.markdown("Assess your monthly environmental impact and discover ways to shrink your carbon footprint.")

# Sidebar for User Inputs
st.sidebar.header("📊 Your Monthly Activity")

with st.sidebar.expander("🚗 Transportation"):
    car_km = st.number_input("Kilometers driven (Car)", min_value=0, value=200, step=50)
    transit_km = st.number_input("Kilometers via Public Transit", min_value=0, value=50, step=10)
    flight_hr = st.number_input("Hours flown", min_value=0.0, value=0.0, step=1.0)

with st.sidebar.expander("⚡ Home Energy"):
    electricity_kwh = st.number_input("Electricity consumed (kWh)", min_value=0, value=300, step=50)

with st.sidebar.expander("🍔 Diet & Food"):
    diet_type = st.selectbox("Describe your diet", ["Meat-heavy", "Average Omnivore", "Vegetarian", "Vegan"])

with st.sidebar.expander("🗑️ Waste"):
    waste_bags = st.number_input("Garbage bags thrown away", min_value=0, value=4, step=1)

# Package inputs
user_inputs = {
    "car_km": car_km,
    "transit_km": transit_km,
    "flight_hr": flight_hr,
    "electricity_kwh": electricity_kwh,
    "diet_type": diet_type,
    "waste_bags": waste_bags
}

# --- Calculation & Dashboard ---
transport_co2, energy_co2, diet_co2, waste_co2 = calculate_footprint(user_inputs)
total_co2 = transport_co2 + energy_co2 + diet_co2 + waste_co2

category_data = {
    "Transportation": transport_co2,
    "Energy": energy_co2,
    "Diet": diet_co2,
    "Waste": waste_co2
}

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Your Total Emissions")
    # Display total in large text
    st.metric(label="Monthly Carbon Footprint", value=f"{total_co2:.1f} kg CO2e", delta="- Goal: < 350 kg", delta_color="inverse")
    
    st.markdown("### How you compare")
    # Global average is roughly 400 kg per month per person
    if total_co2 < 400:
        st.success("You are below the global average! Great job! 🌱")
    else:
        st.warning("You are currently above the global average. Check the insights below to improve! 📉")

with col2:
    st.subheader("Emissions Breakdown")
    # Create a donut chart using Plotly
    df = pd.DataFrame({
        "Category": list(category_data.keys()),
        "Emissions (kg CO2e)": list(category_data.values())
    })
    
    fig = px.pie(df, values="Emissions (kg CO2e)", names="Category", hole=0.4, 
                 color_discrete_sequence=px.colors.sequential.Greens_r)
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --- Dynamic Insights ---
generate_insights(category_data)

st.markdown("---")
st.caption("Data source: Simplified proxy values based on standard EPA and GHG Protocol averages for educational purposes.")
