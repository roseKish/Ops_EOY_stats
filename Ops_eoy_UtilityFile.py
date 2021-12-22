# Operations End of Year Analysis
# Utility File


# import all necessary packages
import pandas as pd
import numpy as np
import glob
import os
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from lxml import etree
from shapely.geometry import Polygon
from shapely.wkb import dumps, loads

# change current working directory to where csv files are stored
# os.chdir('C:/Users/Heliolytics/Documents/Ops_EOY_stats')

# Read in kmls (Dont actually use this function in the script though.)
def read_kml(kml_path):
    with open(kml_path, 'r') as infile:
        kml_string = infile.read()
    kml_data = etree.XML(kml_string.encode('ascii'))  # Read in KML
    coordinate_sets = []
    for node in kml_data.iter(tag=etree.Element):
        if 'coordinates' in node.tag:
            coordinate_sets.append(node.text.strip())
    if len(coordinate_sets) == 0:
        return False
    else:
        polygon_list = []
        for coordinates in coordinate_sets:
            coord_set_list = [coords.split(',') for coords in coordinates.split(' ')]
            coord_list = [(float(coord[0]), float(coord[1])) for coord in coord_set_list]
            if coord_list[0] != coord_list[-1]:  # complete the polygon if it's just a set of lines
                coord_list.append(coord_list[0])
            polygon_list.append(coord_list)
        poly =Polygon([p[::-1] for p in polygon_list[0]])
    return poly

# define a function that reads the data and sorts the df
def read_file():
    print("Gathering data from the sites spreadsheet and scanning logbook") # tell users whats happening
    print('...')
    sites = pd.read_csv("Scans - Sites.csv")
    sites = sites.rename(columns={' ':'SID'})
    sites = sites.rename(columns={'Client Who Provided Site Info':'client'})
    scans = pd.read_csv('Scans - Scanning Logbook.csv')
    scans = scans.rename(columns={'FlightCrew1':'flightcrew_member'})
    data = {'SID': scans['Site ID'],
             'fg': scans['Flight Group (need uniqueness and flyability true)'],
             'date': scans.apply(lambda row: datetime.strptime(row['Actual Scan Date SL'], '%Y-%m-%d'), axis = 1),
             'start': scans.apply(lambda row: datetime.strptime(str(row['Actual Scan Date SL']) + ' ' + str(row['StartTime']), '%Y-%m-%d %H:%M') if not type(row.StartTime) == float else None, axis = 1),
             'end': scans.apply(lambda row: datetime.strptime(str(row['Actual Scan Date SL']) + ' ' + str(row['EndTime']), "%Y-%m-%d %H:%M") if not type(row.EndTime) == float else None, axis = 1),
             'passes': scans['Number of Passes/Passes that cover site?'],
             'flightcrew_member': scans.flightcrew_member,
             'FlightCrew2': scans.FlightCrew2,
             'Pilot': scans.Pilot,
             }
    df = pd.DataFrame(data) # put data into pandas df
    df['year'] = df['date'].apply(lambda x: x.year) # make year column to divide up the data
    df['week_num'] = df['date'].dt.isocalendar().week # make week number column for rescan data
    extracted_sizes = [sites.loc[sites.SID == str(sid)]['Site Size (DC)'] for sid in df['SID']]
    # make the size of sites its own column in the df and only add a value to the size column if the size is specified in the sites db.
    sizes = [i.values[0] if len(i.values) > 0 else None for i in extracted_sizes]
    # add the size column to the df (which is mainly from scans)
    df['size_mw'] = sizes
    # repreat steps for clients, lat, and lon
    extracted_clients = [sites.loc[sites.SID == str(sid)]['client'] for sid in df['SID']]
    client = [i.values[0] if len(i.values) > 0 else None for i in extracted_clients]
    df['client'] = client
    extracted_lat = [sites.loc[sites.SID == str(sid)]['Lat'] for sid in df['SID']]
    lat = [i.values[0] if len(i.values) > 0 else None for i in extracted_lat]
    df['lat'] = lat
    extracted_lon = [sites.loc[sites.SID == str(sid)]['Lon'] for sid in df['SID']]
    lon = [i.values[0] if len(i.values) > 0 else None for i in extracted_lon]
    df['lon'] = lon
    # Calculate Scan duration
    # fix end times that are screwed up b/c of timezones
    df['end'] = df.apply(lambda row: row.end + timedelta(days=1) if row.start > row.end else row.end, axis = 1)
    # calculate scan duration
    df['duration'] = df.apply(lambda row: row.end - row.start if row.start < row.end else row.start - row.end, axis = 1)
    # any scan that is 0 minutes was likely done in under a minute so change to 1 minute
    df['duration'] = df.apply(lambda row: timedelta(minutes=1) if row.duration == timedelta(minutes=0) else row.duration, axis = 1)
    # translate duration to seconds
    df['seconds_duration'] = df.duration.apply(lambda x: x.seconds)
    # Calculate Seconds/MW
    df['mw_sec'] = df.apply(lambda x: x.size_mw / x.seconds_duration if x.seconds_duration != None and x.size_mw != None else None, axis=1)
    return df

# create a function the uses the year specified in the command line and slices the df to the year of interest
def pick_year(df, year):
    #seperate out all rows that contain the year of interest
    df = df.loc[lambda df: df['year'] == year]
    # reset index of dataframe so from row starts at 0
    df.reset_index(drop=True, inplace=True)
    return df

# This is where we will need to update new flightcrew members. These are hard coded.
def add_provider(df):
    df.loc[df['flightcrew_member'] == ('Jaden'), 'provider'] = 'AFTC' # for AFTC
    df.loc[df['flightcrew_member'] == ('Mark L.'), 'provider'] = 'AFTC'
    df.loc[df['flightcrew_member'] == ('Kunhee'), 'provider'] = 'AFTC'
    df.loc[df['flightcrew_member'] == ('Keegan'), 'provider'] = 'AFTC'
    df.loc[df['flightcrew_member'] == ('Matt DeRuzza'), 'provider'] = 'AFTC'
    df.loc[df['flightcrew_member'] == ('Alex Kathrins'), 'provider'] = 'AFTC'
    df.loc[df['flightcrew_member'] == ('Tim Grant'), 'provider'] = 'TFS'     # for TFS
    df.loc[df['flightcrew_member'] == ('Simon Liter'), 'provider'] = 'TFS'
    df.loc[df['flightcrew_member'] == ('Joe'), 'provider'] = 'TFS'
    df.loc[df['flightcrew_member'] == ('Roland'), 'provider'] = 'TFS'
    df.loc[df['flightcrew_member'] == ('Noah'), 'provider'] = 'TFS'
    df.loc[df['flightcrew_member'] == ('Colton'), 'provider'] = 'TFS'
    df.loc[df['flightcrew_member'] == ('Chris H.'), 'provider'] = 'TFS'
    df.loc[df['flightcrew_member'] == ('Chris M.'), 'provider'] = 'TFS'
    df.loc[df['flightcrew_member'] == ('Sam'), 'provider'] = 'Helio'     #for Heliolytics
    df.loc[df['flightcrew_member'] == ('Leah'), 'provider'] = 'Helio'
    df.loc[df['flightcrew_member'] == ('Mason'), 'provider'] = 'Helio'
    df.loc[df['flightcrew_member'] == ('Graeme'), 'provider'] = 'Helio'
    df.loc[df['flightcrew_member'] == ('Sarah'), 'provider'] = 'Helio'
    df.loc[df['flightcrew_member'] == ('Turner'), 'provider'] = 'Helio'
    df.loc[df['flightcrew_member'] == ('Anthony'), 'provider'] = 'Helio'
    df.loc[df['flightcrew_member'] == ('Nikita'), 'provider'] = 'Helio'
    df.loc[df['flightcrew_member'] == ('Scott'), 'provider'] = 'Helio'
    df.loc[df['flightcrew_member'] == ('Matt'), 'provider'] = 'Helio'
    df.loc[df['flightcrew_member'] == ('Ali'), 'provider'] = 'Helio'
    df.loc[df['flightcrew_member'] == ('Harley'), 'provider'] = 'Helio'
    df.loc[df['flightcrew_member'] == ('Rosie'), 'provider'] = 'Helio'
    df.loc[df['flightcrew_member'] == ('Amr'), 'provider'] = 'Helio'
    df.loc[df['flightcrew_member'] == ('Gillian'), 'provider'] = 'Helio'
    df.loc[df['flightcrew_member'] == ('Ida'), 'provider'] = 'Helio'
    df.loc[df['flightcrew_member'] == ('Jeremy'), 'provider'] = 'Helio'
    df.loc[df['flightcrew_member'] == ('Alexandre'), 'provider'] = 'Soframo'     # for soframo
    df.loc[df['flightcrew_member'] == ('Boris'), 'provider'] = 'Soframo'
    df.loc[df['flightcrew_member'] == ('Dean'), 'provider'] = 'Aus'     #for aus
    df.loc[df['flightcrew_member'] == ('Hudson Valley Drones'), 'provider'] = 'Drones'     # for all drone providers
    df.loc[df['flightcrew_member'] == ('Drones Mexico'), 'provider'] = 'Drones'
    df.loc[df['flightcrew_member'] == ('Drone Solutions PR'), 'provider'] = 'Drones'
    df.loc[df['flightcrew_member'] == ('DroneGenuity'), 'provider'] = 'Drones'
    df.loc[df['flightcrew_member'] == ('AUAV'), 'provider'] = 'Drones'
    df.loc[df['flightcrew_member'] == ('FlyMotion'), 'provider'] = 'Drones'
    df.loc[df['flightcrew_member'] == ('SkySkopes'), 'provider'] = 'Drones'
    df.loc[df['flightcrew_member'] == ('Rohl Drones'), 'provider'] = 'Drones'
    df.loc[df['flightcrew_member'] == ('WhiteCloud'), 'provider'] = 'Drones'
    df.loc[df['flightcrew_member'] == ('Hawaii Drone Services'), 'provider'] = 'Drones'
    return df

def total_scans(df, year):
    # save the length of the df into a variable
    scans = len(df)
    print(f"The total number of sites scanned in {year} is {scans}")
    print('...')
    return

def total_GW(df, year):
    # sum the size_mw column contents to get total MW
    MW = df.size_mw.sum()
    # divide total MW by 1000 to get GW
    GW = MW/1000
    print(f"In {year}, operations scanned {GW} GW of solar pannels globally")
    print('...')
    return

def total_time(df, year):
    # sum the duration column of the df and save into variable
    time = df.duration.sum()
    print(f"In {year}, operations scanned for a total of {time}")
    print('...')
    return

def scans_provider(df):
    # group data by provider to find stats of interest
    provider_count = df.groupby('provider').count()
    provider_MW = df.groupby('provider').size_mw.sum()
    provider_time = df[pd.notnull(df['duration'])].groupby('provider').duration.sum()
    print(f"Here are the total number of scans by each {provider_count['SID']}")
    print("...")
    print(f"Here are the total number of MW scanned by each {provider_MW}")
    print('...')
    print(f"Here is the duration of time spent scanning by each {provider_time}")
    print('...')
    return

def scans_client(df):
    client = df.groupby('client').count()
    print(f"Here are the total number of scans for each {client['SID']}")
    print('...')
    return

def scans_FC(df):
    FC_count = df.groupby('flightcrew_member').count()
    FC_MW = df.groupby('flightcrew_member').size_mw.sum()
    print(f"Here are the total number of scanned sites by each {FC_count['SID']}")
    print('...')
    print(f"Here are the total number of MW scanned by each {FC_MW}")
    print('...')
    return
