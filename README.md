# Neuro Impact Calculator

The actions we take as neuroimaging researchers, including conference travel, data collection, and even data preprocessing and storage, have a carbon footprint and therefore contribute to the climate crisis. Increasingly, funding bodies expect researchers to estimate the environmental impacts of proposed projects, and to take steps where possible to reduce them. There is an absence of tools which allow researchers to estimate their footprint across an entire project. Given that it frequently requires substantial energy to collect data, and results in large datasets and computationally expensive pipelines, human neuroimaging is an ideal discipline for such a tool.

This online calculator is intended to provide an estimate of carbon dioxide (CO2) emissions for MRI scanning. Based on provided input information (see below), it generates an 'Environmental impact statement' which can be pasted into grant applications (rephrased to be prospective) or into a publication after the completion of a study. The tool can be accessed through the following URL (<LINK>). In short, the tool requires the following information as input:

* **Duration of active scanning (in minutes)** - The time spent actively collecting MRI data, with a participant in the scanner. Here, include the cumulative length of all scans run. Set at a default of 60 minutes
* **Duration of idle scanning (in minutes)** - The time during your allocated slot during which the scanner was not actively collecting data (e.g., setting up for scanning, putting the participant in the scanner). Set at a default of 15 minutes
* **Year of the scanning** - The year in which data was collected. In some cases, carbon intensity data for the respective combination of year and country may not be available. In such a case, the carbon intensity value for the nearest available year will be used
* **Country** - The country in which scanning was performed
* **Modality** - The neuroimaging modality used. At present, this is limited to MRI scanning. Future iterations may be expanded to include other modalities (EEG, MEG, CT)
* **Field strength** - The field strength of MRI scanning, currently includes 1.5T, 3T, and 7T
* **Model** - The model of the MRI scanner used, including both the manufacturer and the specific model

The resulting printed statement provides total energy usage (kWh) and carbon emissions (kg). This is contextualised using the following metrics:
* Percent of a return flight from Paris to London. The metric used to do so was derived from the Travel Carbon Fotprint Calculator ([https://travel-footprint-calculator.irap.omp.eu/]).
* Equivilant in both miles and km driven in a passenger car, using a conversion factor of 106.4 gCO2/km and 171 gCO2/mile, as taken from the 2023 value for ‘Average WLTP  CO2 emissions from new passenger cars' from [https://www.eea.europa.eu/en/analysis/indicators/co2-performance-of-new-passenger?activeAccordion=]

The components used for this tool are explained in turn below.


## data

This folder contains input data for running the tool.

### carbon_intensity.csv

This file contains carbon intensity conversion factors for countries and overseas territories across the world. Columns include:

* **Entity** - The resepctive country/territory
* **Code** - A shortened code for the respective entity
* **Year** - The year for which carbon intensity is reported
* **Carbon intensity of electricity - gCO2/kWh** - Carbon intensity conversion factor

This data was accessed via Our World in Data [https://ourworldindata.org/grapher/carbon-intensity-electricity]:

Source: Ember (2025), Energy Institute - Statistical Review of World Energy (2025) – with major processing by Our World In Data.

It was edited such that carbon intensity factors for entities larger than countries (e.g., Asia, Africa, the EU) were removed.

This data allows for country-specific carbon footprint estimates, whereby energy usage in kWh can be multiplied by the respective conversion factor to produce an estimate of carbon emissions

### Scanner Power - Sheet3.csv

This file contains power consumption factors for varying models of MRI field strengths and model types. This includes:

* **Manufacturer** - The manufacturer of the MRI scanner used (Siemens, GE, Philips, and Canon)
* **Field strength** - The field strength of the MRI scanner used (1.5T, 3T, 7T)
* **Model** - The specific model of scanner used
* **Off mode (kW)** - The power consumer by the scanner when in 'off' mode. Currently not used in calculations
* **Standby (no scan) mode (kW)** - Reported kW while the scanner is in standby mode
* **Ready-to-scan mode (kW)** - Reported kW while the scanner is in a ready to scan state, not actively collecting data
* **idle_mode** - A kW value for the scanner while not actively collecting data. A separate column has been made for this given that manufacturers variably provide data for the two above fields, and the real term difference between them is not always clear. When one value is provided, this is taken to be idle scanning power. When values are provided for both of the above fields, they are averaged to produce this estimate
* **Scan mode (kW)** - Reported kW during active MRI scanning of patients
* **scan_mode** - As the field above, but adjusted as needed. This is only relevant when a range of values have been provided by the manufacturer. In such cases, the average of the minimum and maximum value is taken.
* **Source** - A URL reflecting where this information has been extracted

Currently, the data in this file has been taken from environmental declarations and poduct specifications provided for the respective model by manufacturers. The estmations derived using this method may be more applicable to clinical scanning than research scanning.

## utils

### consumptions.py

This Python script contains functions used to:

* Estimate MRI energy consumption. Arguments contain:
  * kw_idle (float): Power consumption in kilowatts (kW) during idle mode.
  * kw_scan (float): Power consumption in kilowatts (kW) during scan mode.
  * scan_time (int, optional): Duration of the scan in minutes. Defaults to 60.
  * idle_time (int, optional): Duration of idle time in minutes. Defaults to 15.
  This returns an estimate of energy usage of active and idle scanning time combined, converted to kWh

* Estimate scanner cooling energy consumption. This function models the cooling energy based on the MRI machine's energy consumption and a simplified Coefficient of Performance (COP) for cooling systems. Arguments include:
  * mri_consumption (float): The energy consumption of the MRI machine in kWh.
  * scan_time (int, optional): The duration of the MRI scan in minutes. Defaults to 60.
    
* Estimate data storage energy consumption. This function estimates storage consumption based on estimated data volume, a given energy density for storage, years of storage, and a redundancy factor. Arguments include:
  * scan_time (int, optional): The duration of the MRI scan in minutes. Defaults to 60.
  * years_storage (int, optional): The number of years the data will be stored. Defaults to 5.
  * redundancy (int, optional): The redundancy factor for data storage (e.g., for backups).                 Defaults to 3.

* Estimate computing energy consumption. This function estimates the energy consumption based on CPU hours, RAM usage, optional GPU hours, and a Power Usage Effectiveness (PUE) for High-Performance Computing (HPC). Arguments include:
  * cpu_hours (float): Number of CPU hours used.
  * ram_gb (float): Amount of RAM used in gigabytes.
  * gpu_hours (float, optional): Number of GPU hours used. Defaults to 0.
  * pue_hpc (float, optional): Power Usage Effectiveness for HPC data centers.                             Defaults to 1.56 (from Uptime Institute survey).

## shiny_app.py

This Python script is used to run the calculator dashboard, using the shiny app package.
Functions

* Get choices. Displays choices for dropdown menus of data entry inputs by pooling unique values from data files.
* Load scanner data. Loads data about scanner manufacturers, model, field strength, and energy consumption in kW. All data is linked to original sources.
* compute_percents // work in progress
* convert_g2kg // work in progress
* Get statement. Prints the environmental impact statement.
* Compute scan. Computes carbon emissions and computing energy given the input parameters. Outputs a summary of computed values for the statement. Arguments include:
  *  modality: MRI // (could add other modalities such as EEG or MEG)
  *  model: information about the company and the model of the machine
  *  field_strength: magnetic field strength in Tesla
  *  scan_duration: duration of active scanning in minutes
  *  idle_duration: time in between acquisitions when MRI is in idle mode (e.g.: rest or breaks)
  *  country: the location of where the data was collected
  *  year: information about the time at which the data was collected
  *  scannerData_filename: filename of the file with scanner-related specs
  *  countryCarbonIntensity_filename: filename of the file with carbon intesity specs per countries and years

## Running 
### Requirements
Prerequisites: datetime, pandas, pathlib
pip install shiny

\>\>\>  python shiny_app.py   

Link to access: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
