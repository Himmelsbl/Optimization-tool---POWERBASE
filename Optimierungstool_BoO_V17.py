# -*- coding: utf-8 -*-
"""
@author: Leon Himmelsbach 
Version 16: Optimierungstool BoO - simulationsbeginn 12 uhr 
Datum: 16.04.2025
"""
# import python libraries
import pandas as pd
import numpy as np
import pypsa
import tkinter as tk
import math
import requests
import json
from io import StringIO
from tkcalendar import Calendar
from datetime import datetime
from tkinter import ttk
from tkinter import Canvas

#set parameters for dieselgenerator used in further calculation: 
'''parameters for Dieselgenerator can be set here!!'''
kw_diesel_generator = 4.8 # Active power provision of the used Diesel-generator in kW!
kg_diesel_generator = 150 #weight of the used Diesel-generator in KG
co2_emissions_diesel_generator = 829.69 #CO2-Emissions of the Diesel-generator in g/kWh 
#set parameters for PV-Generator
'''parameters for PV-Generator can be set here!!'''
kWp_pv_generator = 0.5 #peak power of the used (single) pv-module in kWp 
kg_pv_generator = 10.5 #weight of the used (single) pv-module in KG
maximum_power_pv_generator = 60 #maximum power of PV-Generator in kwp for optimization (limited by technical/logistic potential) -> enter "float('inf')" for no limits
modular_power_pv_generator = 6 #modular expandability of the pv generator (e.g. output per pallet) in kW -> set 0 for non modular expansion / set 'kwp_pv_generator' for modular expansion in steps of the used pv-module
#set parameters for wind-Generator
'''parameters for wind-Generator can be set here!!'''
kW_wind_generator = 0.2 # nominal power of the used (single) wind-generator unit in kw 
kg_wind_generator = 12 #weight of the used (single) wind-generator unit in KG
maximum_power_wind_generator = 2 #maximum power of wind-Generator in kw for optimization (limited by technical/logistic potential) -> enter "float('inf')" for no limits 
modular_power_wind_generator = kW_wind_generator #modular expandability of the wind-generator (e.g. output per pallet) in kW -> set 0 for non modular expansion / set 'kw_wind_generator' for modular expansion in steps of the used wind-generator unit
#set parameters used for windspeed conversion:
hub_height_wind_generator = 4 #hub height in meters for the used model of the windgenerator 
roughness_factor = 0.25 #roughness factor depending on the ground surface ued for logharithmic height formular -> table of different roughness factors can be found in: Volker Quaschning, Regenerative Energiesysteme: Technologie - Berechnung - Klimaschutz, 12. Aufl. München: Carl Hanser Verlag GmbH & Co. KG, 2024, page 300
offset_boundary_layer = 0 # offset of the boundary layer in meters -> can be set to zero for large distances to obstacles, otherwise it can be determined by 70% of the obstacle height
#set parameters for Battery: 
'''parameters for Battery can be set here!!'''
kWh_battery = 30 # usable capacity of the used battery-module in kWh
kg_battery = 900  #weight of the used battery-module in KG
maximum_capacity_battery = 150 #maximum capacity of battery-modules in kWh for optimization (limited by technical/logistic potential) -> set 'inf' for no limits
modular_capacity_battery = kWh_battery #modular expandability of the battery in optimization (e.g. output per pallet) in kWh -> set 0 for non modular expansion / set 'kWh_battery' for modular expansion in steps of the used battery unit
discharge_power_battery = 30 #discharge power of the batery-module in kW
charge_power_battery = 16.67 #charge power if the batery-module in kW
#set factor for CO2-Emissions for each vehicle 
'''parameters for CO2-Emissions can be set here!!''' #-> co2-factors can be found in: Smart Freight Centre; https://smart-freight-centre-media.s3.amazonaws.com/documents/GLEC_FRAMEWORK_v3_UPDATED_02_04_24.pdf
co2_flight = 817 #co2-emissions in g CO2e/tkm
co2_truck = 210 #co2-emissions in g CO2e/tkm
co2_train = 7 #co2-emissions in g CO2e/tkm
co2_ship = 89 #co2-emissions in g CO2e/tkm

#preset dates for scenario 1: 
preset_startdate_scenario_1 = '2025-06-03'
preset_enddate_scenario_1 = '2025-07-08'
#preset dates for scenario 2: 
preset_startdate_scenario_2 = '2025-01-10'
preset_enddate_scenario_2 = '2025-02-14'
#preset dates for scenario 3: 
preset_startdate_scenario_3 = '2025-03-13'
preset_enddate_scenario_3 = '2025-03-30'

# preset hours for loadprofile input for scenario 1 
preset_hours_list_scenario_1 = [
    [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17], # load1
    [12], # load2
    [17, 18, 19, 20], # load3#
    [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], # load4
    [5, 6, 7, 17, 18, 19], #load5
    [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21], #load6
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23], # load7
    [18, 19, 20, 21, 22, 23], # load8
    [13, 14], # load9
    [6, 7, 12, 13, 17, 18], # load10
]
# preset hours for loadprofile input for scenario 2 
preset_hours_list_scenario_2 = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23], #load1
    [0, 1, 2, 3, 4, 5, 6, 19, 20, 21, 22, 23], # load2
    [0, 1, 2, 3, 4, 5, 6, 19, 20, 21, 22, 23], # load3
    [0, 1, 2, 3, 4, 5, 6, 19, 20, 21, 22, 23], # load4
    [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18], # load5
    [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18], # load6
    [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], # load7
    [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], # load8
    [5, 6, 7, 12, 13, 16,17,18], # load9
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23] #load1
]
# preset hours for loadprofile input for scenario 3 
preset_hours_list_scenario_3 = [
    [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23], #load1
    [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18], # load2
    [8, 9, 10, 11, 12, 13, 14, 15, 16, 17], # load3
    [11, 12, 13, 14], # load4
    [8, 9, 10, 11, 12, 13, 14, 15, 16, 17], # load5
    [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18], # load6
    [11, 12, 16, 17, 18, 19], # load7
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23], #load8
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23], #load9
    [8, 9, 12, 13, 17, 18] # load10
]

def scenario_preset(): #function gets activated by radiobuttons -> presets Scenario 1,2,3
    
    if selected_scenario.get() == 1: #Scenarion 1
        #deactivation of all hours of the loadprofile selection
        for set_index in range(10):
            for hour in range(24):
                hour_states[set_index][hour].set(0)
                buttons[set_index][hour].config(style='Inactive.TButton')
        #activiation of the preset hours of the loadprofile selection 
        for set_index in range(10):
            for hour in preset_hours_list_scenario_1[set_index]:  
                hour_states[set_index][hour].set(1)
                buttons[set_index][hour].config(style='Active.TButton' if 1 else 'Inactive.TButton')
    
        entry_var_lat.set('42.42423130107311')
        entry_var_lon.set('8.964693028300228')
        entry_var_truck.set('1760')
        entry_var_fligt.set('0')
        entry_var_ship.set('500')
        entry_var_train.set('0')
        entry_var_loadprofile_name1.set('Computers/laptops + radios and charging stations')
        entry_var_loadprofile_power1.set('0.18')
        entry_var_loadprofile_name2.set('Printer/scanner + microwave oven')
        entry_var_loadprofile_power2.set('2.7')
        entry_var_loadprofile_name3.set('Battery chargers')
        entry_var_loadprofile_power3.set('0.3')
        entry_var_loadprofile_name4.set('Radios and charging stations')
        entry_var_loadprofile_power4.set('0.1')
        entry_var_loadprofile_name5.set('Filtration pumps')
        entry_var_loadprofile_power5.set('0.7')
        entry_var_loadprofile_name6.set('Cellphone chargers')
        entry_var_loadprofile_power6.set('0.02')
        entry_var_loadprofile_name7.set('Refrigerators + ventilation')
        entry_var_loadprofile_power7.set('1.4')
        entry_var_loadprofile_name8.set('Outdoor lighting + lighting')
        entry_var_loadprofile_power8.set('1')
        entry_var_loadprofile_name9.set('Medical devieces')
        entry_var_loadprofile_power9.set('0.4')
        entry_var_loadprofile_name10.set('Electric stove')
        entry_var_loadprofile_power10.set('3')
        
        start_calendar.selection_set(preset_startdate_scenario_1)
        end_calendar.selection_set(preset_enddate_scenario_1)
        selection_period()
        
    elif selected_scenario.get() == 2: #scenario 2
        
        for set_index in range(10):
            for hour in range(24):
                hour_states[set_index][hour].set(0)
                buttons[set_index][hour].config(style='Inactive.TButton')
        
        for set_index in range(10):
            for hour in preset_hours_list_scenario_2[set_index]:  
                hour_states[set_index][hour].set(1)
                buttons[set_index][hour].config(style='Active.TButton' if 1 else 'Inactive.TButton')
        
        entry_var_lat.set('49.8964984124631')
        entry_var_lon.set('18.197426065186807')
        entry_var_truck.set('1800')
        entry_var_fligt.set('0')
        entry_var_ship.set('0')
        entry_var_train.set('0')
        entry_var_loadprofile_name1.set('Command center + sanitary container')
        entry_var_loadprofile_power1.set('9')
        entry_var_loadprofile_name2.set('Sleeping container')
        entry_var_loadprofile_power2.set('16')
        entry_var_loadprofile_name3.set('Storage tents')
        entry_var_loadprofile_power3.set('2')
        entry_var_loadprofile_name4.set('Security')
        entry_var_loadprofile_power4.set('3')
        entry_var_loadprofile_name5.set('Accommodation Team')
        entry_var_loadprofile_power5.set('0.7')
        entry_var_loadprofile_name6.set('Meeting tent')
        entry_var_loadprofile_power6.set('2')
        entry_var_loadprofile_name7.set('Kitchen tent')
        entry_var_loadprofile_power7.set('3')
        entry_var_loadprofile_name8.set('Canteen and recreation tent')
        entry_var_loadprofile_power8.set('2')
        entry_var_loadprofile_name9.set('Water supply')
        entry_var_loadprofile_power9.set('2')
        entry_var_loadprofile_name10.set('Medical tents and other')
        entry_var_loadprofile_power10.set('3')
        
        start_calendar.selection_set(preset_startdate_scenario_2)
        end_calendar.selection_set(preset_enddate_scenario_2)
        selection_period()
          
    elif selected_scenario.get() == 3: #scenario 3
        
        for set_index in range(10):
            for hour in range(24):
                hour_states[set_index][hour].set(0)
                buttons[set_index][hour].config(style='Inactive.TButton')
            
        for set_index in range(10):
            for hour in preset_hours_list_scenario_3[set_index]:  
                hour_states[set_index][hour].set(1)
                buttons[set_index][hour].config(style='Active.TButton' if 1 else 'Inactive.TButton')
        
        entry_var_lat.set('27.77656712430752')
        entry_var_lon.set('85.69584710831923')
        entry_var_truck.set('100')
        entry_var_fligt.set('6800')
        entry_var_ship.set('0')
        entry_var_train.set('0')
        entry_var_loadprofile_name1.set('Command center')
        entry_var_loadprofile_power1.set('2.2')
        entry_var_loadprofile_name2.set('Accommodation Team')
        entry_var_loadprofile_power2.set('0.7')
        entry_var_loadprofile_name3.set('Warehouse equipment')
        entry_var_loadprofile_power3.set('2')
        entry_var_loadprofile_name4.set('Medical unit')
        entry_var_loadprofile_power4.set('0.5')
        entry_var_loadprofile_name5.set('Recreation area')
        entry_var_loadprofile_power5.set('2.5')
        entry_var_loadprofile_name6.set('Transportation and supply')
        entry_var_loadprofile_power6.set('0.7')
        entry_var_loadprofile_name7.set('Decontamination zone')
        entry_var_loadprofile_power7.set('1.2')
        entry_var_loadprofile_name8.set('Communication system')
        entry_var_loadprofile_power8.set('1')
        entry_var_loadprofile_name9.set('Water and sanitary')
        entry_var_loadprofile_power9.set('2')
        entry_var_loadprofile_name10.set('Mobility and transportation')
        entry_var_loadprofile_power10.set('2')
        
        start_calendar.selection_set(preset_startdate_scenario_3)
        end_calendar.selection_set(preset_enddate_scenario_3)
        selection_period()
        
        
    elif selected_scenario.get() == 0: #custom input, no preset input 
        
        for set_index in range(10):
            for hour in range(24):
                hour_states[set_index][hour].set(0)
                
                buttons[set_index][hour].config(style='Inactive.TButton')
            
        entry_var_lat.set('')
        entry_var_lon.set('')
        entry_var_truck.set('')
        entry_var_fligt.set('')
        entry_var_ship.set('')
        entry_var_train.set('')
        entry_var_loadprofile_name1.set('load1')
        entry_var_loadprofile_power1.set('0.00')
        entry_var_loadprofile_name2.set('load2')
        entry_var_loadprofile_power2.set('0.00')
        entry_var_loadprofile_name3.set('load3')
        entry_var_loadprofile_power3.set('0.00')
        entry_var_loadprofile_name4.set('load4')
        entry_var_loadprofile_power4.set('0.00')
        entry_var_loadprofile_name5.set('load5')
        entry_var_loadprofile_power5.set('0.00')
        entry_var_loadprofile_name6.set('load6')
        entry_var_loadprofile_power6.set('0.00')
        entry_var_loadprofile_name7.set('load7')
        entry_var_loadprofile_power7.set('0.00')
        entry_var_loadprofile_name8.set('load8')
        entry_var_loadprofile_power8.set('0.00')
        entry_var_loadprofile_name9.set('load9')
        entry_var_loadprofile_power9.set('0.00')
        entry_var_loadprofile_name10.set('load10')
        entry_var_loadprofile_power10.set('0.00')
        
# Function to change the selection for each hour (active/inactive)
def toggle_hour(hour, frame):#Switches the status of the hour buttons (green = active, gray = inactive)
    if hour_states[frame][hour].get():
        buttons[frame][hour].config(style='Inactive.TButton')  # grey = inactive
        hour_states[frame][hour].set(0)
    else:
        buttons[frame][hour].config(style='Active.TButton')  # green = active
        hour_states[frame][hour].set(1)
        
# function for entering the start and end date -> with check whether the entry is correct
def selection_period(event=None):
    startdate = start_calendar.get_date()
    enddate = end_calendar.get_date()

    # check if startdate is before enddate:
    if startdate > enddate:
        label_startdate.config(
            text='Start date must be before the end date!')
        label_startdate.config(fg='red')
        label_enddate.config(text='')
        label_enddate.config(fg='black')
    else:
        # Convert date to German format (DD.MM.) for display -> programmed for THW
        start_day, start_month = startdate.split(
            "-")[2], startdate.split("-")[1]
        end_day, end_month = enddate.split("-")[2], enddate.split("-")[1]

        startdate_display = f'{start_day}.{start_month}.'
        enddate_display = f'{end_day}.{end_month}.'

        # update label on the input surface:
        label_startdate.config(text=f'Startdate: {startdate_display}')
        label_startdate.config(fg='black')
        label_enddate.config(text=f'Enddate: {enddate_display}')
        label_enddate.config(fg='black')

# Function to check the received data from Renewables Ninja
def data_check(df, start_str, end_str, label):
    print(f'Checking the {label}-data:')
    
    if df.empty:
        error_message = f'{label}-DataFrame is empty!'
        print(f'{error_message}')
        tk.messagebox.showerror(' Error', error_message)
        return False  # Error detected, return False
    
    # Check if 'index' column exists
    if 'index' not in df.columns:
        error_message = f'"index" column missing in {label}-data!'
        print(f'{error_message}')
        tk.messagebox.showerror('Error', error_message)
        return False  # Error detected, return False

    df['index'] = pd.to_datetime(df['index'])
    start = pd.to_datetime(start_str)
    end = pd.to_datetime(end_str)

    expected_hours = pd.date_range(start=start, end=end + pd.Timedelta(hours=23), freq='h')
    actual_hours = pd.to_datetime(df['index'])

    if len(df) != len(expected_hours):
        missing = set(expected_hours) - set(actual_hours)
        error_message = f'Expected: {len(expected_hours)} rows, received: {len(df)}.\nMissing timestamps: {list(missing)[:5]}'
        print(f'{error_message}')
        tk.messagebox.showerror(' Error', error_message)
        return False  # Error detected, return False
    else:
        print('Time series is complete.')

    if 'electricity' in df.columns:
        min_val = df['electricity'].min()
        max_val = df['electricity'].max()
        if min_val < 0 or max_val > 1.2:
            error_message = f'Implausible values: Min={min_val}, Max={max_val}'
            print(f'{error_message}')
            tk.messagebox.showerror(' Error', error_message)
            return False  # Error detected, return False
        else:
            print(f'Values plausible: Min={min_val:.3f}, Max={max_val:.3f}')

        missing_count = df['electricity'].isna().sum()
        if missing_count > 0:
            error_message = f'{missing_count} missing values (NaN) in "electricity".'
            print(f'{error_message}')
            tk.messagebox.showerror('Error', error_message)
            return False  # Error detected, return False
        else:
            print('No missing values in "electricity".')
    else:
        error_message = f'"electricity" column missing in {label}-data!'
        print(f'{error_message}')
        tk.messagebox.showerror('Error', error_message)
        return False  # Error detected, return False

    return True  # If no errors found, return True

        
#main calculation, including data input and optimization of the energysystem:
def calculation():#started by pressing calculation button on the input surface
    if start_calendar.get_date() > end_calendar.get_date():# Check if startdate is before enddate
        tk.messagebox.showerror(
            'Error: Start date must be before the end date!')
    elif (datetime.strptime(
            end_calendar.get_date(), '%Y-%m-%d') - datetime.strptime(
                start_calendar.get_date(), '%Y-%m-%d')).days > 365:#check if selected period of simulation is not longer than one year
        tk.messagebox.showerror(
            'Error', 'the period of use must not exceed one year!')
    else:#excecution of the main simulation
        try:
            #transfer input parameter to variables used in further calculation:
            transfer_selected_startdate = start_calendar.get_date()
            transfer_selected_enddate = end_calendar.get_date()
            transfer_selected_startdate_month_day = '-'.join(start_calendar.get_date().split('-')[1:])#thus only date and month are transferred -> can then be used as start and end day in the simulation
            transfer_selected_enddate_month_day = '-'.join(end_calendar.get_date().split('-')[1:])
            transfer_entry_lat = float(entry_lat.get())
            transfer_entry_lon = float(entry_lon.get())
            transfer_entry_truck = float(entry_truck.get())
            transfer_entry_flight = float(entry_flight.get())
            transfer_entry_train = float(entry_train.get())
            transfer_entry_ship = float(entry_ship.get())
            transfer_entry_name1 = entry_loadprofile_name1.get()
            transfer_entry_name2 = entry_loadprofile_name2.get()
            transfer_entry_name3 = entry_loadprofile_name3.get()
            transfer_entry_name4 = entry_loadprofile_name4.get()
            transfer_entry_name5 = entry_loadprofile_name5.get()
            transfer_entry_name6 = entry_loadprofile_name6.get()
            transfer_entry_name7 = entry_loadprofile_name7.get()
            transfer_entry_name8 = entry_loadprofile_name8.get()
            transfer_entry_name9 = entry_loadprofile_name9.get()
            transfer_entry_name10 = entry_loadprofile_name10.get()
            transfer_entry_power1 = float(entry_loadprofile_power1.get()) * 0.001 
            transfer_entry_power2 = float(entry_loadprofile_power2.get()) * 0.001
            transfer_entry_power3 = float(entry_loadprofile_power3.get()) * 0.001
            transfer_entry_power4 = float(entry_loadprofile_power4.get()) * 0.001
            transfer_entry_power5 = float(entry_loadprofile_power5.get()) * 0.001
            transfer_entry_power6 = float(entry_loadprofile_power6.get()) * 0.001 
            transfer_entry_power7 = float(entry_loadprofile_power7.get()) * 0.001
            transfer_entry_power8 = float(entry_loadprofile_power8.get()) * 0.001
            transfer_entry_power9 = float(entry_loadprofile_power9.get()) * 0.001
            transfer_entry_power10 = float(entry_loadprofile_power10.get()) * 0.001
        
            # Determine simulation period
            startdate_datetime = datetime.strptime(transfer_selected_startdate, '%Y-%m-%d')#converting from str to datetime
            enddate_datetime = datetime.strptime(transfer_selected_enddate, '%Y-%m-%d')
            period_simulation_days = (enddate_datetime - startdate_datetime).days + 1 #including the day of selected enddate
            period_simulation_snapshots = period_simulation_days * 24 #24 snapshots per day (hourly resolition of weatherdata

            if period_simulation_snapshots < 8760:  # limitation of the maximum number of snapshots to 8760 (1 Year)
                number_snapshots = period_simulation_snapshots
            else:
                number_snapshots = 8760
                
            # creating the load profile in a dataframe from the information entered:
            column_names = [transfer_entry_name1, transfer_entry_name2, transfer_entry_name3, transfer_entry_name4, transfer_entry_name5, transfer_entry_name6, transfer_entry_name7, transfer_entry_name8, transfer_entry_name9, transfer_entry_name10] #using the input names for the columns of the df 
            set_values = [transfer_entry_power1,transfer_entry_power2,transfer_entry_power3,transfer_entry_power4, transfer_entry_power5, transfer_entry_power6,transfer_entry_power7,transfer_entry_power8,transfer_entry_power9, transfer_entry_power10] #using the input power values for creating the loa profile
            
            #Saves all selections of the activated hours in a DataFrame with named columns and individual values.
            df = pd.DataFrame(0, index=range(24), columns=column_names) # Create an empty DataFrame with 24 rows (one per hour) and named columns
            
            for set_index, column_name in enumerate(column_names):# Fill the DataFrame with the selected hours
                for hour in range(24):
                    if hour_states[set_index][hour].get():  # If hour is activated
                        df[column_name] = df[column_name].astype(float)  
                        df.at[hour, column_name] = float(set_values[set_index])
                        #df.at[hour, column_name] = set_values[set_index]  #enter the input power values
        
            df['Total_Load'] = df.sum(axis=1) # Add new column: Sum of all values per hour
            df = pd.concat([df] * period_simulation_days, ignore_index=True)# Duplicate the rows of the DataFrame depending of the selected period of use
            
            #converting set parameters of the dieselgenerator for further calculation:
            power_diesel_generator = kw_diesel_generator * 0.001 # kW converted to MW 
            weight_diesel_generator = kg_diesel_generator * 0.001  #kg in tonns 
            co2_per_mwh_el_diesel_generator = co2_emissions_diesel_generator *0.001 # -> in t/MWh
            
            #converting set parameters of PV-Generator for further calculation
            power_pv = kWp_pv_generator * 0.001 #kw per unit converted to MW 
            weight_pv = kg_pv_generator * 0.001  #kg in tonns    
            p_nom_max_pv = maximum_power_pv_generator * 0.001 #maximum power of PV-Generator in MW (limited by technical/logistic potential)
            p_nom_mod_pv = modular_power_pv_generator * 0.001 #nominal power of the generator Module in MW
            
            #converting set parameters of Wind-Generator for further calculation: 
            power_wind = kW_wind_generator * 0.001 #kW per unit converted to MW    
            weight_wind = kg_wind_generator * 0.001  #kg converted to tonns
            hub_height = hub_height_wind_generator #hub height in meters -> used for conversion of wind-speed data 
            p_nom_max_wind = maximum_power_wind_generator * 0.001 #maximum power of Wind-Generator in MW (limited by technical/logistic potential)
            p_nom_mod_wind = modular_power_wind_generator  * 0.001 #nominal power of the generator Module in MW
            
            #converting set parameters for Battery: 
            capacity_battery = kWh_battery * 0.001 #kwh per unit converted to MWh
            weight_battery = kg_battery * 0.001  # weight in kg converted to tonns  
            e_nom_max_battery = maximum_capacity_battery * 0.001 #maximum capacity of battery in MWh (limited by technical/logistic potential)
            e_nom_mod_battery = capacity_battery #nominal cpacity of the Battery Module in MW
            discharge_power = discharge_power_battery * 0.001 #discharge power if the batery in MW
            charge_power = charge_power_battery * 0.001 #charge power if the batery in MW
            p_min_pu_battery = -round((charge_power/capacity_battery),2)
            p_max_pu_battery = round((discharge_power/capacity_battery),2)
            
            #converting set factor for CO2-Emissions for each vehicle 
            co2_per_tkm_flight = co2_flight * 0.001 * 0.001 #emissions per t weight and km flown in t co2 
            co2_per_tkm_truck = co2_truck * 0.001 * 0.001 #emissions per t weight and km flown in t co2
            co2_per_tkm_train = co2_train * 0.001 * 0.001 #emissions per t weight and km flown in t co2
            co2_per_tkm_ship = co2_ship * 0.001 * 0.001 #emissions per t weight and km flown in t co2
            
            #use input distances for further calculation
            distance_flight = transfer_entry_flight  #distance in km -> includes return flight 
            distance_truck = transfer_entry_truck  #distance in km -> includes return flight
            distance_train = transfer_entry_train  #distance in km -> includes return flight
            distance_ship = transfer_entry_ship  #distance in km -> includes return flight
            
            #calculate using set parameters -> number of Generators/Battery per MW 
            number_pv_per_mw = math.ceil(1/power_pv) #1 MW 
            number_battery_per_mw = math.ceil(1 / capacity_battery)  #1 MW
            number_wind_per_mw = math.ceil(1/ power_wind)  #1 MW 
            number_diesel_generators_per_mw = math.ceil(1/power_diesel_generator)
            
            # determine co2 factors (transport) for optimization -> is used as 'capital cost':   
            co2_per_mw_diesel_generator = ((number_diesel_generators_per_mw *
                                          weight_diesel_generator * distance_flight *
                                          co2_per_tkm_flight) +
                                          (number_diesel_generators_per_mw *
                                          weight_diesel_generator * distance_truck *
                                          co2_per_tkm_truck) +
                                          (number_diesel_generators_per_mw *
                                          weight_diesel_generator * distance_train *
                                          co2_per_tkm_train)+
                                          (number_diesel_generators_per_mw *
                                          weight_diesel_generator * distance_ship *
                                          co2_per_tkm_ship))
            
            co2_per_mw_pv = ((number_pv_per_mw *
                              weight_pv * distance_flight *
                              co2_per_tkm_flight) +
                             (number_pv_per_mw * weight_pv * distance_truck *
                              co2_per_tkm_truck)+
                             (number_pv_per_mw *
                              weight_pv * distance_train *
                              co2_per_tkm_train) +
                             (number_pv_per_mw * weight_pv * distance_ship *
                              co2_per_tkm_ship))  

            co2_per_mw_wind = ((number_wind_per_mw *
                               weight_wind * distance_flight *
                               co2_per_tkm_flight) +
                               (number_wind_per_mw * weight_wind *
                                distance_truck *
                                co2_per_tkm_truck)+
                               (number_wind_per_mw *
                                weight_wind * distance_train *
                                co2_per_tkm_train) +
                               (number_wind_per_mw * weight_wind *
                                distance_ship * co2_per_tkm_ship))

            co2_per_mw_battery = ((number_battery_per_mw * weight_battery *
                                   distance_flight * co2_per_tkm_flight) +
                                   (number_battery_per_mw * weight_battery *
                                    distance_truck * co2_per_tkm_truck)+
                                   (number_battery_per_mw * weight_battery *
                                    distance_train * co2_per_tkm_train) +
                                   (number_battery_per_mw * weight_battery *
                                    distance_ship * co2_per_tkm_ship))
            
            # Create network for optimaization actual system:
            network_actual = pypsa.Network()
            network_actual.set_snapshots(range(12, number_snapshots))
            network_actual.add('Carrier', name = 'electricity' )
            network_actual.add('Bus', name='electricity',
                            carrier='electricity')  # electrical bus
            network_actual.add('Load', name='electrical_load', bus='electricity', carrier='electricity', 
                            p_set= df['Total_Load'].iloc[12:number_snapshots].to_numpy().flatten())  # electrical load 
            network_actual.add('Generator', name='Dieselgenerator', bus='electricity', carrier='electricity', 
                            p_nom_extendable=True, p_nom_mod= power_diesel_generator,
                            capital_cost=co2_per_mw_diesel_generator,
                            marginal_cost= co2_per_mwh_el_diesel_generator)
            network_actual.optimize(solver_name='highs') #optimization actual system using solver
                      
            # Recieve PV data
            print('\nRecieving PV Data')
            token = 'a7ccf3b89a387df7f2cd2f3b8351bf96f264f2d9'
            api_base = 'https://www.renewables.ninja/api/'
            s = requests.session()
            s.headers = {'Authorization': 'Token ' + token}
                
            url_pv = api_base + 'data/pv'
            args_pv = {
                'lat': transfer_entry_lat,
                'lon': transfer_entry_lon,
                'date_from': '2019-01-01',
                'date_to': '2019-12-31',
                'dataset': 'merra2',
                'capacity': 1.0,
                'system_loss': 0.1,
                'tracking': 0,
                'tilt': 35,
                'azim': 180,
                'format': 'json'
            }
            
            try:
                r = s.get(url_pv, params=args_pv)
                r.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
                parsed = json.loads(r.text)
                if 'data' in parsed:
                    data_pv = pd.read_json(StringIO(json.dumps(parsed['data'])), orient='index').reset_index()
                    if not data_check(data_pv, args_pv['date_from'], args_pv['date_to'], "PV"):
                        return  # Error detected, calculation is aborted
                else:
                    print('Error: "data" not in PV response.')
                    tk.messagebox.showerror('Error', 'Error: "data" not in PV response.')
                    return  # Error detected, calculation is aborted
            except requests.exceptions.RequestException as e:
                print(f'Error recieving PV data: {e}')
                tk.messagebox.showerror(' Error', f'Error recieving PV data: {e}')
                return  # Error detected, calculation is aborted
            
            #Recieve Wind-data
            print('\nRecieving Wind-data')
            url_wind = api_base + 'data/wind'
            args_wind = {
                'lat': transfer_entry_lat,
                'lon': transfer_entry_lon,
                'date_from': '2019-01-01',
                'date_to': '2019-12-31',
                'capacity': 1.0,
                'height': 10,
                'turbine': 'XANT M21 100',
                'raw': 'true',
                'format': 'json'
            }
            
            try:
                r = s.get(url_wind, params=args_wind)
                r.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
                parsed = json.loads(r.text)
                if 'data' in parsed:
                    data_wind = pd.read_json(StringIO(json.dumps(parsed['data'])), orient='index').reset_index()
                    if not data_check(data_wind, args_wind['date_from'], args_wind['date_to'], "Wind"):
                        return  # Error detected, calculation is aborted
                else:
                    print('Error: "data" not in Wind response.')
                    tk.messagebox.showerror('Error', 'Error: "data" not in Wind response.')
                    return  # Error detected, calculation is aborted
            except requests.exceptions.RequestException as e:
                print(f'Error retrieving Wind data: {e}')
                tk.messagebox.showerror(' Error', f'Error retrieving Wind data: {e}')
                return  # Error detected, calculation is aborted

            # Convert wind speed from 10 m to 4m hight using the logarithmic height formula 
            z0 = roughness_factor # Roughness factor -> can be set here -> source: Volker Quaschning, Regenerative Energiesysteme: Technologie - Berechnun - Klimaschutz, 12. Aufl. München: Carl Hanser Verlag GmbH & Co. KG, 2024 (p.300)
            h1 = 10 #hight of the requested wind data 
            h2 = hub_height #depeding on the hight of the used wind turbine 
            d = offset_boundary_layer 
            logz = ((math.log((h2-d)/z0)) / (math.log((h1-d)/z0))) #logarithmic height formula
            data_wind[f'{h2}m_speed'] = (data_wind['wind_speed'] * logz)#saving converted wind speed as a new coloumn in data_wind            
            data_wind[f'{h2}m_speed_rounded'] = data_wind[f'{h2}m_speed'].round(1)
            
            #calculation of the energy yield of the WTG depending on the wind speed
            ''' can be set here -> depending on the details of the used Wind-Generator'''
            wind_speed_ranges = [
                (0, 2.5), (2.5, 3), (3, 3.5), (3.5, 4), (4, 4.5), (4.5, 5),
                (5.5, 12.5),  #full yield betrween 5.5 und 12.5 m/s
                (12.5, 13), (13, 13.5), (13.5, 14), (14, 14.5), (14.5, 15)
                ]
            
            # yield for each range per unit (yield/nominal power) 
            ''' can be set here -> depending on the details of the used Wind-Generator'''
            choices = [
                0,       # 0 to < 2.5 m/s
                25/200,  # 2.5 to < 3 m/s
                50/200,  # 3 to < 3,5 m/s
                80/200,  # 3.5 to < 4 m/s'
                115/200, # 4 to < 4.5 m/s
                145/200, # 4.5 to < 5 m/s
                200/200, # 5.5 to < 12.5 m/s -> full yield
                160/200, # 12.5 to < 13 m/s
                120/200, # 13 to < 13.5 m/s
                80/200,  # 13.5 to < 14 m/s
                40/200,  # 14 to < 14.5 m/s
                0        # >= 14.5 m/s 
                ]

            # generate condition
            conditions = [
                np.logical_and(data_wind[f'{h2}m_speed_rounded'] >= low, data_wind[f'{h2}m_speed_rounded'] < high)
                for low, high in wind_speed_ranges
                ]

            # fill new collum 
            data_wind[f'yield_{h2}m_pu'] = np.select(conditions, choices, default=0) # Add new column in DF with the energy yields depending on the wind speed
            
            #Weather data processing: filtering weathadata depending on the input start- and enddate 
            start_datetime = f'2019-{transfer_selected_startdate_month_day} 00:00:00' #startdate used to filter the weatherdata from 2019 
            end_datetime = f'2019-{transfer_selected_enddate_month_day} 23:00:00' #endtdate used to filter the weatherdata from 2019 
        
            transfer_selected_startdate_month_day = datetime.strptime(
                transfer_selected_startdate_month_day, '%m-%d') #rewind the entered dates in datetime format (month+day) -> is required for comparison:
            transfer_selected_enddate_month_day = datetime.strptime(
                transfer_selected_enddate_month_day, '%m-%d') #rewind the entered dates in datetime format (month+day) -> is required for comparison:
            
            if start_datetime > end_datetime: #loop to filter the data of the input period correctly, even if the period is between two years
                # pv-data:
                filtered_data_pv1 = data_pv[(data_pv['index'] >= start_datetime) & (
                    data_pv['index'] <= '2019-12-31 23:00:00')]
                filtered_data_pv2 = data_pv[(
                    data_pv['index'] >= '2019-01-01 00:00:00') & (data_pv['index'] <= end_datetime)]
                filtered_data_pv = pd.concat(
                    [filtered_data_pv1, filtered_data_pv2])
                filtered_data_pv = filtered_data_pv.reset_index(drop=True)
                # Wind-data:
                filtered_data_wind1 = data_wind[(data_wind['index'] >= start_datetime) & (
                    data_wind['index'] <= '2019-12-31 23:00:00')]
                filtered_data_wind2 = data_wind[(
                    data_wind['index'] >= '2019-01-01 00:00:00') & (data_wind['index'] <= end_datetime)]
                filtered_data_wind = pd.concat(
                    [filtered_data_wind1, filtered_data_wind2])
                filtered_data_wind = filtered_data_wind.reset_index(drop=True)
            else:
                #pv-data:
                filtered_data_pv = data_pv[(data_pv['index'] >= start_datetime) & (
                    data_pv['index'] <= end_datetime)]
                filtered_data_pv = filtered_data_pv.reset_index(drop=True)
                #wind-data:
                filtered_data_wind = data_wind[(data_wind['index'] >= start_datetime) & (
                    data_wind['index'] <= end_datetime)]
                filtered_data_wind = filtered_data_wind.reset_index(drop=True)

            #compare periods before and after the input period and filter the lowest values to get the "whorst case" weatherdata
            filtered_data_pv['electricity_min'] =  filtered_data_pv['electricity'].copy() #pv-data:
            filtered_data_pv['electricity_min'] = np.inf #initialise df with infinite values
            filtered_data_pv['electricity_sum'] = filtered_data_pv['electricity'].copy()
            filtered_data_pv['electricity_sum'] = 0 #df for adding all values seperatly to get the average value -> probably not going to be used!
            filtered_data_pv['electricity_compared'] = filtered_data_pv['electricity_min'].copy() #df to compare sum of timesteps an write the lowest into df
            min_sum_data_pv = float('inf') 
            
            filtered_data_wind[f'yield_{h2}m_pu_min'] = filtered_data_wind[f'yield_{h2}m_pu'].copy() #wind-data:
            filtered_data_wind[f'yield_{h2}m_pu_min'] = np.inf #initialise df with infinite values
            filtered_data_wind[f'yield_{h2}m_pu_sum'] = filtered_data_wind[f'yield_{h2}m_pu'].copy()
            filtered_data_wind[f'yield_{h2}m_pu_sum'] = 0 #df for adding all values seperatly to get the average value -> probably not going to be used!
            filtered_data_wind[f'yield_{h2}m_pu_compared'] =  filtered_data_wind[f'yield_{h2}m_pu_min'].copy() #df to compare sum of timesteps an write the lowest into df
            min_sum_data_wind = float('inf') 
            
            
            if  transfer_selected_startdate_month_day >  transfer_selected_enddate_month_day: #examine the period of use in days-> day of the enddate included!
                period_of_use = 365 + (
                    (transfer_selected_enddate_month_day -  transfer_selected_startdate_month_day).days + 1)
            else:
                period_of_use = (
                    (transfer_selected_enddate_month_day -  transfer_selected_startdate_month_day).days + 1)
                
            timestep = pd.Timedelta(days=period_of_use) #define timestep for comparison of timesteps before and after the selected period
            
            
            if timestep <= pd.Timedelta(days=1): #vary the number of periods of use to be compared depending on the length of the period of use:
                compared_periods = 31
            elif timestep == pd.Timedelta(days=2):
                compared_periods = 15
            elif timestep == pd.Timedelta(days=3):
                compared_periods = 11
            elif timestep == pd.Timedelta(days=4):
                compared_periods = 9
            elif timestep == pd.Timedelta(days=5):
                compared_periods = 7
            elif pd.Timedelta(days=5) < timestep <= pd.Timedelta(days=9):
                compared_periods = 5
            elif pd.Timedelta(days=9) < timestep <= pd.Timedelta(days=29):
                compared_periods = 3
            elif timestep >= pd.Timedelta(days=30):
                compared_periods = 1

            startdate_comparison =  transfer_selected_startdate_month_day - \
                (timestep * int((compared_periods - 1)/2))#determine the start date for the comparison so that the entered period of use is in the middle
            enddate_comparison =  transfer_selected_enddate_month_day - \
                (timestep * int((compared_periods - 1)/2))#determine the end date for the comparison so that the entered period of use is in the middle
            #filter and compare the set number of timesteps starting from the start date of the comparison
            for i in range(compared_periods):  
                startdata_comparison_loop = (
                    startdate_comparison + (timestep*i)).strftime('%m-%d')
                enddata_comparison_loop = (
                    enddate_comparison + (timestep*i)).strftime('%m-%d')
                start_datetime_comparison = f'2019-{startdata_comparison_loop} 00:00:00'
                end_datetime_comparison = f'2019-{enddata_comparison_loop} 23:00:00'

                if start_datetime_comparison > end_datetime_comparison:
                    #pv-data:
                    current_data_pv1 = data_pv[(data_pv['index'] >= start_datetime_comparison) & (
                        data_pv['index'] <= '2019-12-31 23:00:00')]
                    current_data_pv2 = data_pv[(
                        data_pv['index'] >= '2019-01-01 00:00:00') & (data_pv['index'] <= end_datetime_comparison)]
                    current_data_pv = pd.concat(
                        [current_data_pv1, current_data_pv2])
                    current_data_pv = current_data_pv.reset_index(drop=True)
                    #wind-data:
                    current_data_wind1 = data_wind[(data_wind['index'] >= start_datetime_comparison) & (
                        data_wind['index'] <= '2019-12-31 23:00:00')]
                    current_data_wind2 = data_wind[(
                        data_wind['index'] >= '2019-01-01 00:00:00') & (data_wind['index'] <= end_datetime_comparison)]
                    current_data_wind = pd.concat(
                        [current_data_wind1, current_data_wind2])
                    current_data_wind = current_data_wind.reset_index(
                        drop=True)
                else:
                    #pv-data:
                    current_data_pv = data_pv[(data_pv['index'] >= start_datetime_comparison) & (
                        data_pv['index'] <= end_datetime_comparison)]
                    current_data_pv = current_data_pv.reset_index(drop=True)
                    #wind-data:
                    current_data_wind = data_wind[(data_wind['index'] >= start_datetime_comparison) & (
                        data_wind['index'] <= end_datetime_comparison)]
                    current_data_wind = current_data_wind.reset_index(
                        drop=True)
                    
                filtered_data_pv[f'electricity_period{i}'] = current_data_pv['electricity']  # add filtered data in df as column in each step of the loop
                filtered_data_pv["electricity_min"] = np.minimum(
                    filtered_data_pv["electricity_min"], filtered_data_pv[f'electricity_period{i}'])#comparison of the values an transfer the lower values
                filtered_data_pv['electricity_sum'] = filtered_data_pv["electricity_sum"] + \
                    current_data_pv['electricity']
                sum_data_pv = filtered_data_pv[f'electricity_period{i}'].to_numpy().sum() 
                if sum_data_pv < min_sum_data_pv:
                    min_sum_data_pv = sum_data_pv
                    filtered_data_pv['electricity_compared'] = filtered_data_pv[f'electricity_period{i}']
                
                #wind-data:
                filtered_data_wind[f'yield_{h2}m_pu_period{i}'] = current_data_wind[f'yield_{h2}m_pu']
                # copare the values of 'electricity' and take the lower value
                filtered_data_wind[f'yield_{h2}m_pu_min'] = np.minimum(
                    filtered_data_wind[f'yield_{h2}m_pu_min'], filtered_data_wind[f'yield_{h2}m_pu_period{i}'])
                filtered_data_wind[f'yield_{h2}m_pu_sum'] = filtered_data_wind[f'yield_{h2}m_pu_sum'] + \
                    current_data_wind[f'yield_{h2}m_pu']
                sum_data_wind =  filtered_data_wind[f'yield_{h2}m_pu_period{i}'].to_numpy().sum() 
                if sum_data_wind < min_sum_data_wind:
                    min_sum_data_wind = sum_data_wind
                    filtered_data_wind[f'yield_{h2}m_pu_compared'] =  filtered_data_wind[f'yield_{h2}m_pu_period{i}']
           
            filtered_data_pv['electricity_avg'] = filtered_data_pv['electricity_sum'] / \
                compared_periods #calculating the average values over the compared number of periods
            filtered_data_wind[f'yield_{h2}m_pu_avg'] = filtered_data_wind[f'yield_{h2}m_pu_sum'] / \
                compared_periods  #calculating the average values over the compared number of periods

            #building a network for optimizing energysystem with integrated wind, pv and battery:
            #transfer processed wind an pv data into df for further optimization     
            pv_p_max_pu = filtered_data_pv['electricity_compared']
            wind_p_max_pu = filtered_data_wind[f'yield_{h2}m_pu_compared']
            
            #build network for optimization of the new energysystem (wind, pv, battery):
            network_new = pypsa.Network()
            network_new.set_snapshots(range(12, number_snapshots))
            df = df.iloc[12:number_snapshots]
            pv_p_max_pu = pv_p_max_pu.iloc[12:number_snapshots]
            wind_p_max_pu = wind_p_max_pu.iloc[12:number_snapshots]
            df.index = network_new.snapshots
            pv_p_max_pu.index = network_new.snapshots
            wind_p_max_pu.index = network_new.snapshots
            #electrical pypsa system:
            network_new.add('Carrier', name= 'electricity')    
            network_new.add('Bus', name='electricity', carrier= 'electricity')
            network_new.add('Bus', name='store', carrier = 'electricity')
            network_new.add('Load', name='electrical_load', bus='electricity', carrier='electricity',
                            p_set= df['Total_Load'].to_numpy().flatten())
            network_new.add('Generator', name='Dieselgenerator', bus='electricity', carrier='electricity',
                            p_nom_extendable=True, p_nom_mod= power_diesel_generator,
                            capital_cost= co2_per_mw_diesel_generator,
                            marginal_cost= co2_per_mwh_el_diesel_generator)
            network_new.add('Generator', name='PV-Generator', bus='electricity', carrier='electricity', p_nom_max= p_nom_max_pv,
                            p_nom_extendable=True, p_max_pu=pv_p_max_pu.to_numpy().flatten(),
                            capital_cost=co2_per_mw_pv, p_nom_mod= p_nom_mod_pv,
                            marginal_cost=0)
            network_new.add('Generator', name='Windturbine', bus='electricity', carrier='electricity',
                            p_nom_extendable=True, p_nom_max= p_nom_max_wind, p_max_pu=wind_p_max_pu.to_numpy().flatten(),
                            capital_cost=co2_per_mw_wind, p_nom_mod = p_nom_mod_wind,
                            marginal_cost=0)
            network_new.add('Store', name='Battery', bus='store', carrier='electricity',
                            e_nom_extendable=True, e_nom_max = e_nom_max_battery, e_nom_mod = e_nom_mod_battery,
                            capital_cost= co2_per_mw_battery, 
                            marginal_cost=0)
            network_new.add('Link', name='Battery_power', bus1='electricity', carrier='electricity', 
                            bus0='store', efficiency=1, marginal_cost=0,
                            p_min_pu= p_min_pu_battery, p_max_pu = p_max_pu_battery, p_nom_extendable=True)
            network_new.optimize(solver_name='highs')#optimization of the new energysystem

            #results of the optimization: 
            #actual system: 
            co2_total_actual = round((network_actual.objective), 2)
            
            co2_transport_actual = round((network_actual.generators['p_nom_opt'] *    
                                       network_actual.generators['capital_cost']).sum(),2)
            co2_operation_actual = round((network_actual.generators_t.p *  
                                      network_actual.generators['marginal_cost']).sum().sum(),2)
            power_generator_actual = round((network_actual.generators.at['Dieselgenerator', 'p_nom_opt'] * 1000),2)
            number_generator_actual_opt = int(power_generator_actual / kw_diesel_generator)
            # new system: 
            co2_total_new = round((network_new.objective), 2)
            
            co2_transport_new = round((network_new.generators['p_nom_opt'] *    
                           network_new.generators['capital_cost']).sum() +  
                          (network_new.stores['e_nom_opt'] * network_new.stores['capital_cost']).sum(), 2)
            co2_operation_new = round((network_new.generators_t.p *  
                                      network_new.generators['marginal_cost']).sum().sum(),2)
            diesel_generator_opt_new = round((network_new.generators.at['Dieselgenerator', 'p_nom_opt'] * 1000),2)
            pv_opt = round((network_new.generators.at['PV-Generator', 'p_nom_opt'] * 1000))
            wind_opt = round((network_new.generators.at['Windturbine', 'p_nom_opt'] * 1000))
            battery_opt = round((network_new.stores.at['Battery', 'e_nom_opt'] * 1000))
            number_diesel_generator_opt_new = int(diesel_generator_opt_new / kw_diesel_generator)
            number_battery_opt = int(battery_opt / kWh_battery)
            number_pv_opt = int(pv_opt / kWp_pv_generator)
            number_wind_opt = int(wind_opt / kW_wind_generator)
            reduction_co2_total = round((co2_total_actual - co2_total_new), 2)
            reduction_co2_percent = round(((1 - (co2_total_new / co2_total_actual)) * 100), 2)
            reduction_co2_transport = round((co2_transport_actual - co2_transport_new), 2)
            reduction_co2_transport_percent = round(((1 - (co2_transport_new / co2_transport_actual)) * 100), 2)
            reduction_co2_operation =  round((co2_operation_actual - co2_operation_new), 2)
            reduction_co2_operation_percent = round(((1 - (co2_operation_new / co2_operation_actual)) * 100), 2)
            
            #lables for output of both systems 
            label_diesel_opt.config(text=f'({number_diesel_generator_opt_new}* {kw_diesel_generator} kW) -> {diesel_generator_opt_new} kW')
            label_pv_opt.config(text=f'({number_pv_opt}*{kWp_pv_generator} kWp) -> {pv_opt} kWp')
            label_wind_opt.config(text=f'({number_wind_opt}*{kW_wind_generator} kW) -> {wind_opt} kW')
            label_battery_opt.config(text=f'({number_battery_opt}*{kWh_battery} kWh) -> {battery_opt} kWh')
            label_reduction_value.config(text=f'{reduction_co2_total} t -> {reduction_co2_percent} %')
            label_reduction_transport_value.config(text=f'{reduction_co2_transport} t -> {reduction_co2_transport_percent} %')
            label_reduction_operation_value.config(text=f'{reduction_co2_operation} t -> {reduction_co2_operation_percent} %')
            label_number_generator_actual.config(text=f'({number_generator_actual_opt}*{kw_diesel_generator} kW) -> {power_generator_actual} kW')
            label_co2_actual_value.config(text=f'{co2_total_actual} t')
            label_co2_actual_transport_value.config(text=f'{co2_transport_actual} t')
            label_co2_actual_operation_value.config(text=f'{co2_operation_actual} t')
        except Exception as e:
            tk.messagebox.showerror('Fehler', str(e))


#function of closebutton
def close():
    surface.destroy()

# Main surface for input
surface = tk.Tk()
surface.title('Optimization of the BoO energy system')

screen_width = int(surface.winfo_screenwidth())
screen_height = int(surface.winfo_screenheight())
surface.geometry(f"{screen_width}x{screen_height}")

# create scrollbars using canvas -> in case the display-resulution is too small to display the complete content of the GUI
canvas = Canvas(surface)
canvas.grid(row=0, column=0, sticky="nsew")

scrollbar_y = tk.Scrollbar(surface, orient="vertical", command=canvas.yview)
scrollbar_y.grid(row=0, column=1, sticky='ns')
scrollbar_x = tk.Scrollbar(surface, orient="horizontal", command=canvas.xview)
scrollbar_x.grid(row=1, column=0, sticky='ew')

canvas.configure(yscrollcommand=scrollbar_y.set)
canvas.configure(xscrollcommand=scrollbar_x.set)

canvas_frame = tk.Frame(canvas)

canvas.create_window((0, 0), window= canvas_frame, anchor="nw")

def update_scrollregion(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

canvas_frame.bind("<Configure>", update_scrollregion)

surface.grid_rowconfigure(0, weight=1)
surface.grid_columnconfigure(0, weight=1)

#creating the main GUI inside of the canvas_frame:  
label_input_frame = tk.Frame(canvas_frame, padx=2.5)
label_input_frame.grid(row=0, column=0)

# Show results on main surface
label_input = tk.Label(label_input_frame, text='Input:', font=('Arial', 12, 'bold'))
label_input.grid(row=0, column=0, padx= 5, sticky= 'w')

selected_scenario =  tk.IntVar(value=0)
checkbutton_custom = tk.Radiobutton(label_input_frame, text='custom', variable=selected_scenario, value=0, command=scenario_preset)
checkbutton_custom.grid(row=0, column=1, padx=5, pady=5, sticky= 'w')
checkbutton_scenario_1 = tk.Radiobutton(label_input_frame, text='Scenario 1', variable=selected_scenario, value=1, command=scenario_preset)
checkbutton_scenario_1.grid(row=0, column=2, padx=5, pady=5, sticky= 'w')
checkbutton_scenario_2 = tk.Radiobutton(label_input_frame, text='Scenario 2', variable=selected_scenario, value=2, command=scenario_preset)
checkbutton_scenario_2.grid(row=0, column=3, padx=5, pady=5, sticky= 'w')
checkbutton_scenario_3 = tk.Radiobutton(label_input_frame, text='Scenario 3', variable=selected_scenario, value=3, command=scenario_preset)
checkbutton_scenario_3.grid(row=0, column=4, padx=5, pady=5, sticky= 'w')

# Buttons for calculation and closing
calculation_button = tk.Button(label_input_frame, text='Start Calculation', command=calculation)
calculation_button.grid(row=0, column=5, padx=5)

close_button = tk.Button(label_input_frame, text='Close', command=close)
close_button.grid(row=0, column=8, padx=5)

#show results in frame
input_frame = tk.Frame(canvas_frame, borderwidth=2, relief='solid', padx=2.5, pady=2.5)
input_frame.grid(row=1, column=0, pady=5, padx=5)

# Label and input for coordinates
label_coordinates = tk.Label(input_frame, text='Coordinates:', font=('Arial', 12, 'bold'))
label_coordinates.grid(row=0, column=0, sticky='w', pady=5)

# Latitude
entry_var_lat = tk.StringVar()
entry_lat = tk.Entry(input_frame,textvariable=entry_var_lat, width=10)
entry_lat.grid(row=0, column=1, pady=5, padx=(5, 2), sticky='w')
label_lat = tk.Label(input_frame, text='° Latitude')
label_lat.grid(row=0, column=1, padx=(75, 0), sticky='w')

# Longitude
entry_var_lon = tk.StringVar()
entry_lon = tk.Entry(input_frame,textvariable=entry_var_lon,  width=10)
entry_lon.grid(row=1, column=1, pady=5, padx=(5, 2), sticky='w')
label_lon = tk.Label(input_frame, text='° Longitude')
label_lon.grid(row=1, column=1, padx=(75,0), sticky='w')

# Label and input for transportation route
label_transport = tk.Label(input_frame, text='Transport:', font=('Arial', 12, 'bold'))
label_transport.grid(row=0, column=2, sticky='w', pady=5)

# Truck Transport
entry_var_truck = tk.StringVar()
entry_truck = tk.Entry(input_frame, textvariable= entry_var_truck, width=10)
entry_truck.grid(row=0, column=2, pady=5, padx=(100, 2), sticky='w')
label_truck = tk.Label(input_frame, text='km by Truck')
label_truck.grid(row=0, column=2, padx=(150, 0), sticky='w')

# Airplane Transport
entry_var_fligt = tk.StringVar()
entry_flight = tk.Entry(input_frame, textvariable= entry_var_fligt, width=10)
entry_flight.grid(row=1, column=2, pady=5, padx=(100, 2), sticky='w')
label_flight = tk.Label(input_frame, text='km by Airplane')
label_flight.grid(row=1, column=2, padx=(150, 0), sticky='w')

# ship transport
entry_var_ship = tk.StringVar()
entry_ship = tk.Entry(input_frame, textvariable= entry_var_ship, width=10)
entry_ship.grid(row=0, column=2, pady=5, padx=(250,5 ), sticky='w')
label_ship = tk.Label(input_frame, text='km by ship')
label_ship.grid(row=0, column=2, padx=(300, 5), sticky='w')

# train Transport
entry_var_train = tk.StringVar()
entry_train = tk.Entry(input_frame, textvariable= entry_var_train, width=10)
entry_train.grid(row=1, column=2, pady=5, padx=(250, 5), sticky='w')
label_train = tk.Label(input_frame, text='km by train')
label_train.grid(row=1, column=2, padx=(300, 5), sticky='w')

# Label and input for loadprofile
label_loadprofile_name = tk.Label(input_frame, text='Loadprofile:', font=('Arial', 12, 'bold'))
label_loadprofile_name.grid(row=4, column=0, sticky='w', pady=5)

label_loadprofile = tk.Label(input_frame, text='name:')
label_loadprofile.grid(row=4, column=1, sticky='w', pady=5)
label_loadprofile_power = tk.Label(input_frame, text='power (kW):')
label_loadprofile_power.grid(row=4, column=1, sticky='e', pady=5, padx= (2,5))
label_loadprofile_time = tk.Label(input_frame, text='time of use:')
label_loadprofile_time.grid(row=4, column=2, sticky='w', pady=5)

entry_var_loadprofile_name1 = tk.StringVar()
entry_loadprofile_name1 = tk.Entry(input_frame, textvariable= entry_var_loadprofile_name1, width=15)
entry_loadprofile_name1.grid(row=5, column=1, pady=5, padx=(5, 75), sticky='w')
entry_loadprofile_name1.insert(0, 'load1')
entry_var_loadprofile_power1 = tk.StringVar()
entry_loadprofile_power1 = tk.Entry(input_frame, textvariable= entry_var_loadprofile_power1, width= 5)
entry_loadprofile_power1.grid(row=5, column=1, pady=5, padx=(2, 10), sticky='e')
entry_loadprofile_power1.insert(0, 0.00)

entry_var_loadprofile_name2 = tk.StringVar()
entry_loadprofile_name2 = tk.Entry(input_frame, textvariable= entry_var_loadprofile_name2, width=15)
entry_loadprofile_name2.grid(row=6, column=1, pady=5, padx=(5, 75), sticky='w')
entry_loadprofile_name2.insert(0, 'load2')
entry_var_loadprofile_power2 = tk.StringVar()
entry_loadprofile_power2 = tk.Entry(input_frame, textvariable= entry_var_loadprofile_power2, width= 5)
entry_loadprofile_power2.grid(row=6, column=1, pady=5, padx=(2, 10), sticky='e')
entry_loadprofile_power2.insert(0, 0.00)

entry_var_loadprofile_name3 = tk.StringVar()
entry_loadprofile_name3 = tk.Entry(input_frame, textvariable= entry_var_loadprofile_name3, width=15)
entry_loadprofile_name3.grid(row=7, column=1, pady=5, padx=(5, 75), sticky='w')
entry_loadprofile_name3.insert(0, 'load3')
entry_var_loadprofile_power3 = tk.StringVar()
entry_loadprofile_power3 = tk.Entry(input_frame, textvariable= entry_var_loadprofile_power3, width= 5)
entry_loadprofile_power3.grid(row=7, column=1, pady=5, padx=(2, 10), sticky='e')
entry_loadprofile_power3.insert(0, 0.00)

entry_var_loadprofile_name4 = tk.StringVar()
entry_loadprofile_name4 = tk.Entry(input_frame, textvariable= entry_var_loadprofile_name4, width=15)
entry_loadprofile_name4.grid(row=8, column=1, pady=5, padx=(5, 75), sticky='w')
entry_loadprofile_name4.insert(0, 'load4')
entry_var_loadprofile_power4 = tk.StringVar()
entry_loadprofile_power4 = tk.Entry(input_frame, textvariable= entry_var_loadprofile_power4, width= 5)
entry_loadprofile_power4.grid(row=8, column=1, pady=5, padx=(2, 10), sticky='e')
entry_loadprofile_power4.insert(0, 0.00)

entry_var_loadprofile_name5 = tk.StringVar()
entry_loadprofile_name5 = tk.Entry(input_frame, textvariable= entry_var_loadprofile_name5, width=15)
entry_loadprofile_name5.grid(row=9, column=1, pady=5, padx=(5, 75), sticky='w')
entry_loadprofile_name5.insert(0, 'load5')
entry_var_loadprofile_power5 = tk.StringVar()
entry_loadprofile_power5 = tk.Entry(input_frame, textvariable= entry_var_loadprofile_power5, width= 5)
entry_loadprofile_power5.grid(row=9, column=1, pady=5, padx=(2, 10), sticky='e')
entry_loadprofile_power5.insert(0, 0.00)

entry_var_loadprofile_name6 = tk.StringVar()
entry_loadprofile_name6 = tk.Entry(input_frame, textvariable= entry_var_loadprofile_name6, width=15)
entry_loadprofile_name6.grid(row=10, column=1, pady=5, padx=(5, 75), sticky='w')
entry_loadprofile_name6.insert(0, 'load6')
entry_var_loadprofile_power6 = tk.StringVar()
entry_loadprofile_power6 = tk.Entry(input_frame, textvariable= entry_var_loadprofile_power6, width= 5)
entry_loadprofile_power6.grid(row=10, column=1, pady=5, padx=(2, 10), sticky='e')
entry_loadprofile_power6.insert(0, 0.00)

entry_var_loadprofile_name7 = tk.StringVar()
entry_loadprofile_name7 = tk.Entry(input_frame, textvariable= entry_var_loadprofile_name7, width=15)
entry_loadprofile_name7.grid(row=11, column=1, pady=5, padx=(5, 75), sticky='w')
entry_loadprofile_name7.insert(0, 'load7')
entry_var_loadprofile_power7 = tk.StringVar()
entry_loadprofile_power7 = tk.Entry(input_frame, textvariable= entry_var_loadprofile_power7, width= 5)
entry_loadprofile_power7.grid(row=11, column=1, pady=5, padx=(2, 10), sticky='e')
entry_loadprofile_power7.insert(0, 0.00)

entry_var_loadprofile_name8 = tk.StringVar()
entry_loadprofile_name8 = tk.Entry(input_frame, textvariable= entry_var_loadprofile_name8, width=15)
entry_loadprofile_name8.grid(row=12, column=1, pady=5, padx=(5, 75), sticky='w')
entry_loadprofile_name8.insert(0, 'load8')
entry_var_loadprofile_power8 = tk.StringVar()
entry_loadprofile_power8 = tk.Entry(input_frame, textvariable= entry_var_loadprofile_power8, width= 5)
entry_loadprofile_power8.grid(row=12, column=1, pady=5, padx=(2, 10), sticky='e')
entry_loadprofile_power8.insert(0, 0.00)

entry_var_loadprofile_name9 = tk.StringVar()
entry_loadprofile_name9 = tk.Entry(input_frame, textvariable= entry_var_loadprofile_name9, width=15)
entry_loadprofile_name9.grid(row=13, column=1, pady=5, padx=(5, 75), sticky='w')
entry_loadprofile_name9.insert(0, 'load9')
entry_var_loadprofile_power9 = tk.StringVar()
entry_loadprofile_power9 = tk.Entry(input_frame, textvariable= entry_var_loadprofile_power9, width= 5)
entry_loadprofile_power9.grid(row=13, column=1, pady=5, padx=(2, 10), sticky='e')
entry_loadprofile_power9.insert(0, 0.00)

entry_var_loadprofile_name10 = tk.StringVar()
entry_loadprofile_name10 = tk.Entry(input_frame, textvariable= entry_var_loadprofile_name10, width=15)
entry_loadprofile_name10.grid(row=14, column=1, pady=5, padx=(5, 75), sticky='w')
entry_loadprofile_name10.insert(0, 'load10')
entry_var_loadprofile_power10 = tk.StringVar()
entry_loadprofile_power10 = tk.Entry(input_frame, textvariable= entry_var_loadprofile_power10, width= 5)
entry_loadprofile_power10.grid(row=14, column=1, pady=5, padx=(2, 10), sticky='e')
entry_loadprofile_power10.insert(0, 0.00)

# define style
style = ttk.Style()
style.configure('Inactive.TButton', font=('Arial', 9), padding=[0, 0], width=2, borderwidth=1, relief='solid', background='lightgray', foreground='gray')
style.configure('Active.TButton', font=('Arial', 9), padding=[0, 0], width=2, borderwidth=2, relief='solid', background='green', foreground='green')

# frame for selection for selection of hours
frames = []
buttons = []
hour_states = []

# creation of 10 frames with hour-selection 
for i in range(10):
    frame = tk.Frame(input_frame, bg='white')
    frame.grid(row=5+i, column=2, padx=5, pady=5)

    # List for buttons and states
    frame_buttons = {}
    frame_hour_states = {}

    for hour in range(24):
        frame_hour_states[hour] = tk.IntVar(value=0)
        btn = ttk.Button(frame, text=f'{hour:02d}', style='Inactive.TButton', command=lambda h=hour, f=i: toggle_hour(h, f))
        btn.grid(row=0, column=hour, padx=0, pady=0, ipadx=0, ipady=0, sticky='nsew')  
        frame_buttons[hour] = btn

    # adding list for buttons and frames to the mainstorage
    buttons.append(frame_buttons)
    hour_states.append(frame_hour_states)

# Period selection via calendar
label_period = tk.Label(input_frame, text='Period of Use:', font=('Arial', 12, 'bold'))
label_period.grid(row= 26, column=0, sticky='nw', pady=5)

label_startdate = tk.Label(input_frame, text='Start Date:')
label_startdate.grid(row=26, column=2, padx=10, pady=5, sticky='w')
start_calendar = Calendar(input_frame, date_pattern='yyyy-mm-dd', showweeknumbers=False)
start_calendar.grid(row=27, column=2, padx=10, pady=10, sticky='w')

label_enddate = tk.Label(input_frame, text='End Date:')
label_enddate.grid(row=26, column=2, padx=(270,5), pady=5, sticky='w')
end_calendar = Calendar(input_frame, date_pattern='yyyy-mm-dd', showweeknumbers=False)
end_calendar.grid(row=27, column=2, padx=(270,10), pady=10, sticky='w')
start_calendar.bind("<<CalendarSelected>>", selection_period)
end_calendar.bind("<<CalendarSelected>>", selection_period)

# Show results on main surface
label_results = tk.Label(canvas_frame, text='Results:', font=('Arial', 12, 'bold'))
label_results.grid(row=0, column=3, columnspan=4)

#show results in frame
result_frame = tk.Frame(canvas_frame, borderwidth=2, relief="solid", padx=2.5, pady=2.5)
result_frame.grid(row=1, column=3, pady=5, padx=5, sticky= 'n')

label_results_power = tk.Label(result_frame, text='Actual System:', font=('Arial', 12, 'bold'))
label_results_power.grid(row=1, column=0, pady=5, sticky='w')

label_number_actual = tk.Label(result_frame, text='Power of diesel generator:')
label_number_actual.grid(row=2, column=0, sticky='w')
label_number_generator_actual= tk.Label(result_frame, text=f'(xx*{kw_diesel_generator} kW) -> xx kW')
label_number_generator_actual.grid(row=2, column=1, sticky='e')

label_co2_actual = tk.Label(result_frame, text='CO2 Emissions (total):')
label_co2_actual.grid(row=3, column=0, sticky='w')
label_co2_actual_value = tk.Label(result_frame, text='xx t')
label_co2_actual_value.grid(row=3, column=1, sticky='e')

label_co2_actual_transport = tk.Label(result_frame, text='CO2 Emissions (transport):')
label_co2_actual_transport.grid(row=4, column=0, sticky='w')
label_co2_actual_transport_value = tk.Label(result_frame, text='xx t')
label_co2_actual_transport_value.grid(row=4, column=1, sticky='e')

label_co2_actual_operation = tk.Label(result_frame, text='CO2 Emissions(operation):')
label_co2_actual_operation.grid(row=5, column=0, sticky='w')
label_co2_actual_operation_value = tk.Label(result_frame, text='xx t')
label_co2_actual_operation_value.grid(row=5, column=1, sticky='e')

label_emissions = tk.Label(result_frame, text='Optimized System:', font=('Arial', 12, 'bold'))
label_emissions.grid(row=6, column=0, pady=5, sticky='w')

label_diesel = tk.Label(result_frame, text='Power of diesel generator:')
label_diesel.grid(row=10, column=0, sticky='w')
label_diesel_opt = tk.Label(result_frame, text=f'(xx*{kw_diesel_generator} kW) -> xx kW')
label_diesel_opt.grid(row=10, column=1, sticky='e')

label_pv = tk.Label(result_frame, text='Power of pv generator:')
label_pv.grid(row=11, column=0, sticky='w')
label_pv_opt = tk.Label(result_frame, text=f'(xx*{kWp_pv_generator} kWp) -> xx kWp')
label_pv_opt.grid(row=11, column=1, sticky='e')

label_wind = tk.Label(result_frame, text='Power of wind generator:')
label_wind.grid(row=12, column=0, sticky='w')
label_wind_opt = tk.Label(result_frame, text=f'(xx*{kW_wind_generator} kW) -> xx kW')
label_wind_opt.grid(row=12, column=1, sticky='e')

label_battery = tk.Label(result_frame, text='Capacity of battery storage:')
label_battery.grid(row=13, column=0, sticky='w')
label_battery_opt = tk.Label(result_frame, text=f'(xx*{kWh_battery} kWh) -> xx kWh')
label_battery_opt.grid(row=13, column=1, sticky='e')

label_reduction = tk.Label(result_frame, text='CO2 Reduction (total):')
label_reduction.grid(row=14, column=0, sticky='w')
label_reduction_value = tk.Label(result_frame, text='xx t -> xx %')
label_reduction_value.grid(row=14, column=1, sticky='e')

label_reduction_transport = tk.Label(result_frame, text='CO2 Reduction (transport):')
label_reduction_transport.grid(row=15, column=0, sticky='w')
label_reduction_transport_value = tk.Label(result_frame, text='xx t -> xx %')
label_reduction_transport_value.grid(row=15, column=1, sticky='e')

label_reduction_operation = tk.Label(result_frame, text='CO2 Reduction (operation):')
label_reduction_operation.grid(row=16, column=0, sticky='w')
label_reduction_operation_value = tk.Label(result_frame, text='xx t -> xx %')
label_reduction_operation_value.grid(row=16, column=1, sticky='e')

# Start Mainloop
surface.mainloop()