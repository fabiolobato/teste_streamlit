import streamlit as st

# Define the mri_consumption function (ensure it's accessible or defined here)
def mri_consumption(kw_idle, kw_scan, scan_time =60, idle_time = 60):
  """
  Calculates the energy consumption of an MRI scanner.

  Args:
    kw_idle (float): Power consumption in kilowatts (kW) during idle mode.
    kw_scan (float): Power consumption in kilowatts (kW) during scan mode.
    scan_time (int, optional): Duration of the scan in minutes. Defaults to 60.
    idle_time (int, optional): Duration of idle time in minutes. Defaults to 60.

  Returns:
    float: Total energy consumption in kilowatt-hours (kWh).
  """
  kwh = (scan_time*kw_scan)/60 + (idle_time*kw_idle)/60
  return kwh

st.set_page_config(layout="wide")
st.title("MRI Scanner Energy Consumption Estimator")

st.write("Enter the parameters below to estimate the energy consumption of an MRI scanner.")

# Input widgets for the parameters
with st.sidebar:
    st.header("Input Parameters")
    kw_idle = st.number_input("Idle Mode Power (kW)", min_value=0.0, value=8.45, step=0.1)
    kw_scan = st.number_input("Scan Mode Power (kW)", min_value=0.0, value=21.45, step=0.1)
    scan_time = st.number_input("Scan Time (minutes)", min_value=1, value=60, step=1)
    idle_time = st.number_input("Idle Time (minutes)", min_value=1, value=60, step=1)

if st.button("Calculate Consumption"):
    if kw_idle is not None and kw_scan is not None and scan_time is not None and idle_time is not None:
        estimation = mri_consumption(kw_idle, kw_scan, scan_time, idle_time)
        st.success(f"### Estimated Energy Consumption: {estimation:.2f} kWh")
    else:
        st.error("Please enter all required parameters.")

st.markdown("---")
st.info("This tool estimates energy consumption based on the provided power and time parameters.")
