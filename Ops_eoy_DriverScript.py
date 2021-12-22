# Operations End of Year Analysis
# Driver Script

# This script reads in the year from the command line and applies all analyses to that year.

import typer
import ops_eoy_stats_utility
from ops_eoy_stats_utility import read_file, pick_year, add_provider, total_scans, total_GW, total_time, scans_provider, scans_client, scans_FC

def run_stats(year: int):
    year_list = [2017, 2018, 2019, 2020, 2021] # This list will need to be updated annually
    if year in year_list: # Add in some defensive programming to help users run script
        df=read_file() # if year requested is in scanning logbook, analyze the data.
        df=pick_year(df, year)
        df=add_provider(df)
        total_scans(df, year)
        total_GW(df, year)
        total_time(df, year)
        scans_provider(df)
        scans_client(df)
        scans_FC(df)
        print("Processing complete.")
    else:
        print("There is no data for that year. Data exists for either 2017, 2018, 2019, 2020, or 2021.") # This will need to be updated annually
    return

#Use typer to pass through command line argument
if __name__ == "__main__":
    typer.run(run_stats)
