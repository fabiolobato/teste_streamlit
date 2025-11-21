import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path

# Try to import utils, handle error if user hasn't set up folders yet
try:
    from utils.consumptions import mri_consumption, computing_consumption
except ImportError:
    # Fallback mocks to prevent crash if utils folder is missing during testing
    def mri_consumption(idle_p, scan_p, scan_d, idle_d): return (idle_p * idle_d + scan_p * scan_d) / 60
    def computing_consumption(cpu_hours, ram_gb, gpu_hours, pue_hpc): return 0.5

# --- Configuration & Paths ---
st.set_page_config(page_title="Neuro Impact Calculator", layout="wide")

# Define paths relative to the script location
HERE = Path(__file__).parent
COUNTRY_CARBON_FILE = HERE / "data/carbon-intensity.csv"
SCANNER_DATA_FILE = HERE / "data/Scanner Power - Main.csv"

# --- Helper Functions (Cached) ---

@st.cache_data
def load_scanner_data(filepath):
    """Loads and processes scanner data."""
    try:
        df_models = pd.read_csv(filepath)
        df_models['model_full'] = df_models['Manufacturer'] + " " + df_models['Model']
        df_models.sort_values(by=['model_full'], inplace=True)
        df_models['Field strength'] = df_models['Field strength'].astype(float)
        return df_models
    except FileNotFoundError:
        st.error(f"File not found: {filepath}")
        return pd.DataFrame(columns=['model_full', 'Field strength', 'Manufacturer', 'Model'])

@st.cache_data
def load_carbon_data(filepath):
    """Loads carbon intensity data."""
    try:
        return pd.read_csv(filepath)
    except FileNotFoundError:
        st.error(f"File not found: {filepath}")
        return pd.DataFrame(columns=['Entity', 'Year'])

# --- Calculation Logic (Adapted from original) ---

def compute_percents(summary, transport_mode):
    # TODO: implement based on original logic
    return 0

def convert_g2kg(grams):
    return grams / 1000.0

def get_statement(summary):
    if summary["year"] != summary["year_eff"]:
        year_text = f"We don't have data for {summary['year']} yet, so the estimation provided is computed based on the closest year available ({summary['year_eff']}) for the country selected, {summary['country']}.\n\n"
    else:
        year_text = ""
    
    if summary["model"] == "Other":
        model_text = f"The value provided below is computed as the median for {summary['field_strength']:.1f}T MRI models in our database.\n\n"
    else:
        model_text = f"You have selected the **{summary['model']}** model.\n\n"

    text = year_text + model_text + (
        f"For the current study, **{summary['scan_power']:.2f} kW** was used for MRI scanning for a duration of active scanning of {summary['scan_duration']:.0f} minutes "
        f"and an additional **{summary['idle_power']:.2f} kW** for idle scanning for a duration of {summary['idle_duration']:.0f} minutes, "
        f"and **{summary['computing_energy']:.2f} kWh** for data processing and analysis.\n\n"
        f"In {summary['country']} in {summary['year_eff']}, with a carbon intensity value of {summary['carbon_intensity']:.2f} grams of carbon dioxide per kWh (gCO2/kWh), "
        f"this amounted to: \n\n"
        f"### {convert_g2kg(summary['carbon_emissions']):.2f} kg CO2e\n\n"
        f"_(kilograms of carbon dioxide-equivalent emissions)_.\n\n"
        f"This is equivalent to {compute_percents(summary, 'flight'):.2f}% of a return flight from London to Paris, "
        f"{compute_percents(summary, 'car'):.2f}% miles driven in a passenger car."
    )
    return text

def compute_scan(modality, model, field_strength, scan_duration, idle_duration, country, year, df_carbon, df_energy):
    
    # 1. Year Logic
    country_data = df_carbon[df_carbon["Entity"] == country]
    
    if country_data.empty:
         raise ValueError(f"No data available for country: {country}")

    if year not in country_data["Year"].values:
        available_years = sorted(country_data["Year"].unique())
        # Find closest year
        year_eff = min(available_years, key=lambda x: abs(x - year))
    else:
        year_eff = year

    mask = (df_carbon["Entity"] == country) & (df_carbon["Year"] == year_eff)
    carbon_intensity = df_carbon.loc[mask, "Carbon intensity of electricity - gCO2/kWh"].iloc[0]

    # 2. Machine Calculations
    # If the model is in our database
    if model in df_energy["model_full"].values:
        scan_power = df_energy.loc[df_energy["model_full"] == model, "scan_mode"].iloc[0]
        idle_power = df_energy.loc[df_energy["model_full"] == model, "idle_mode"].iloc[0]
    
    # If "Other" logic
    elif model == "Other":
        scan_mode_vals = df_energy.loc[df_energy["Field strength"] == field_strength, "scan_mode"].dropna()
        if scan_mode_vals.empty:
            # Fallback or error
            scan_power = 0 
        else:
            scan_power = scan_mode_vals.median()

        idle_mode_vals = df_energy.loc[df_energy["Field strength"] == field_strength, "idle_mode"].dropna()
        if idle_mode_vals.empty:
            idle_power = 0
        else:
            idle_power = idle_mode_vals.median()
    
    else:
        raise ValueError("Model not found in database")

    # Calculate emissions
    # Note: Assuming mri_consumption takes kW and minutes and returns kWh
    carbon_emissions = carbon_intensity * mri_consumption(idle_power, scan_power, scan_duration, idle_duration)

    # 3. Computing Calculations
    computing_energy = computing_consumption(cpu_hours=2, ram_gb=32, gpu_hours=0, pue_hpc=1.56)

    summary = {
        "country": country,
        "year": year,
        "year_eff": year_eff,
        "model": model,
        "field_strength": field_strength,
        "carbon_intensity": carbon_intensity,
        "scan_duration": scan_duration,
        "idle_duration": idle_duration,
        "carbon_emissions": carbon_emissions,
        "scan_power": scan_power,
        "idle_power": idle_power,
        "computing_energy": computing_energy
    }
    return summary

# --- Main Application Layout ---

def main():
    # Load Data
    df_scanner = load_scanner_data(SCANNER_DATA_FILE)
    df_carbon = load_carbon_data(COUNTRY_CARBON_FILE)

    # --- Sidebar (Inputs) ---
    with st.sidebar:
        st.header("Parameters")
        
        scan_duration_base = st.number_input("Duration of active scanning (min)", value=60, min_value=0)
        idle_duration_base = st.number_input("Duration of idle scanning (min)", value=15, min_value=0)
        sample_size = st.number_input("Sample size", value=1, min_value=1)

        # Country Selection
        country_list = df_carbon["Entity"].unique().tolist() if not df_carbon.empty else []
        country = st.selectbox("Country", options=country_list)

        # Year Selection
        year = st.number_input("Year of the scanning", 
                               min_value=2000, 
                               max_value=date.today().year, 
                               value=date.today().year - 1)

        # Modality (Fixed for now, as per original code)
        modality = st.selectbox("Modality", ["MRI"])

        # Field Strength
        if not df_scanner.empty:
            strength_choices = sorted(df_scanner["Field strength"].unique().tolist())
        else:
            strength_choices = []
            
        field_strength = st.selectbox("Field strength", options=strength_choices)

        # Dynamic Model Selection (Logic moved here)
        # We filter models based on the selected field strength immediately
        if field_strength is not None and not df_scanner.empty:
            filtered_models = df_scanner[df_scanner["Field strength"] == float(field_strength)]
            model_choices = filtered_models["model_full"].unique().tolist()
            model_choices.append("Other") # Add the "Other" option explicitly
            
            model = st.selectbox("Model", options=model_choices)
        else:
            model = st.selectbox("Model", options=["Other"])

    # --- Main Panel (Outputs) ---
    st.title("Neuro Impact Calculator")
    
    # Add spacing or logo placeholder if needed
    # st.image("path_to_logo.png", width=200) 

    # Perform Calculation
    if st.button("Calculate") or True: # 'or True' makes it reactive like Shiny, remove if you want explicit button press
        
        # Calculate totals based on sample size
        scan_duration_total = float(scan_duration_base) * float(sample_size)
        idle_duration_total = float(idle_duration_base) * float(sample_size)

        if country and field_strength and model:
            try:
                # Run computation
                result_summary = compute_scan(
                    modality=modality,
                    model=model,
                    field_strength=float(field_strength),
                    scan_duration=scan_duration_total,
                    idle_duration=idle_duration_total,
                    country=country,
                    year=year,
                    df_carbon=df_carbon,
                    df_energy=df_scanner
                )
                
                # Get formatted text
                output_text = get_statement(result_summary)
                
                # Display Result
                st.markdown(output_text)
                
            except Exception as e:
                st.error(f"An error occurred during calculation: {e}")
        else:
            st.info("Please load data and select parameters to calculate.")

if __name__ == "__main__":
    main()