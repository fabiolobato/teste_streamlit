def mri_consumption(kw_idle, kw_scan, scan_time = 60, idle_time = 15):
  """
  Calculates the energy consumption of an MRI scanner.

  Args:
    kw_idle (float): Power consumption in kilowatts (kW) during idle mode.
    kw_scan (float): Power consumption in kilowatts (kW) during scan mode.
    scan_time (int, optional): Duration of the scan in minutes. Defaults to 60.
    idle_time (int, optional): Duration of idle time in minutes. Defaults to 15.

  Returns:
    float: Total energy consumption in kilowatt-hours (kWh).
  """
  kwh = (scan_time * kw_scan) / 60 + (idle_time * kw_idle) / 60

  return kwh


def cooling_consumption(mri_consumption, scan_time = 60):
  """
  Calculates the energy consumption required for cooling an MRI machine.

  This function models the cooling energy based on the MRI machine's energy consumption
  and a simplified Coefficient of Performance (COP) for cooling systems.

  Args:
    mri_consumption (float): The energy consumption of the MRI machine in kWh.
    scan_time (int, optional): The duration of the MRI scan in minutes. Defaults to 60.

  Returns:
    float: The estimated energy consumption for cooling in kilowatt-hours (kWh).
  """
  #Keeping the Coefficient of Performance (COP) a constant, but following the equation aiming to allows expanding the tool later based on the location and time
  cop_t_amb = 3.0 - 0.05 * (20 - 15)
  h_load = 0.95 * mri_consumption

  e_cool = h_load / cop_t_amb * scan_time


  return e_cool

def storage_consumption(scan_time = 60, years_storage = 5, redundancy = 3):
  """
  Calculates the energy consumption associated with data storage for MRI scans.

  This function estimates storage consumption based on estimated data volume,
  a given energy density for storage, years of storage, and a redundancy factor.

  Args:
    scan_time (int, optional): The duration of the MRI scan in minutes. Defaults to 60.
    years_storage (int, optional): The number of years the data will be stored. Defaults to 5.
    redundancy (int, optional): The redundancy factor for data storage (e.g., for backups).
                                Defaults to 3.

  Returns:
    float: The estimated energy consumption for data storage in kilowatt-hours (kWh).
  """
  volume_estimated = (scan_time / 60) * 5
  kwh = 0.0537 * volume_estimated * years_storage * redundancy
  #converting the estimation of 50kWh/TB/Year to GiB
  return kwh

def computing_consumption(cpu_hours=2, ram_gb=32, gpu_hours=0, pue_hpc = 1.56):
  """
  Calculates the energy consumption of computing resources.

  This function estimates the energy consumption based on CPU hours, RAM usage,
  optional GPU hours, and a Power Usage Effectiveness (PUE) for High-Performance Computing (HPC).

  Args:
    cpu_hours (float): Number of CPU hours used.
    ram_gb (float): Amount of RAM used in gigabytes.
    gpu_hours (float, optional): Number of GPU hours used. Defaults to 0.
    pue_hpc (float, optional): Power Usage Effectiveness for HPC data centers.
                               Defaults to 1.56 (from Uptime Institute survey).

  Returns:
    float: Total estimated energy consumption in kilowatt-hours (kWh).
  """
  # Constants
  w_core = 12.0 #validate value later one
  w_ram_gb = 0.3725 #same constant used by Lannelongue, Loïc, Jason Grealey, and Michael Inouye. "Green algorithms: quantifying the carbon footprint of computation." Advanced science 8.12 (2021): 2100707.
  w_gpu = 500.0 # estimative based on the current and new gpus

  e_cpu = (cpu_hours * w_core) / 1000
  e_ram = (cpu_hours * ram_gb * w_ram_gb) / 1000
  e_gpu = (gpu_hours * w_gpu) / 1000
  kwh = (e_cpu + e_ram + e_gpu) * pue_hpc ## Value from pue_hpc comming from  Uptime Institute 14th annual global data center survey (retrieved DataCenter Knowledge (news platform))
  return kwh