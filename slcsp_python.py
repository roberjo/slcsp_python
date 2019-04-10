import pkg_resources
from pkg_resources import DistributionNotFound, VersionConflict

# dependencies can be any iterable with strings, 
# e.g. file line-by-line iterator
dependencies = [
  'pandas>=0.24.1',
  'tabulate>=0.8.3'
]

# Here, if a pip package dependency is not met, 
# a DistributionNotFound or VersionConflict
# exception is thrown. 
try:
    pkg_resources.require(dependencies)
except Exception as e: 
    print("**ERROR** Package not found!")
    print(e)
    print("Please install the missing package with \'pip install [x]\'")
    print(" where [x] is the package name.")
    raise SystemExit

import struct
import pandas as pd
from datetime import datetime
from tabulate import tabulate
from enum import Enum
from decimal import Decimal

TWOPLACES = Decimal(10) ** -2       # same as Decimal('0.01')

class PlanMetal(Enum):
    # Enum of Health Care plans metal name
    Bronze = 'Bronze'
    Silver = 'Silver'
    Gold = 'Gold'
    Platinum = 'Platinum'
    Catastrophic = 'Catastrophic'

def get_slcsp(silver_plans, state, ratearea):
    # Build a rate tuple for filtering plans
    rate_tuple = [(state, ratearea)]

    # Filter plans by this state and rate area tuple
    ratearea_plans = silver_plans[silver_plans.set_index(['state','rate_area']).index.isin(rate_tuple)]
    
    # Sort the silver plans by rate ascending
    # and remove duplicate rates
    ratearea_plans = ratearea_plans.sort_values(by=['rate'], ascending=True).drop_duplicates(subset=['rate'])
    
    # DEBUG - print out the matching silver plans for the rate area
    #print(tabulate(ratearea_plans, headers='keys', tablefmt='psql'))

    # If only one plan, return empty string
    if(len(ratearea_plans.index) < 2):
        return ""
    
    # Else return the second lowest cost silver plan rate
    return Decimal(ratearea_plans['rate'].iloc[1]).quantize(TWOPLACES)

# Get State and Rate Area value for a given Zip Code
def get_ratearea(zipcode, zips):
    is_zipcode = zips['zipcode'] == zipcode
    target_zips = zips[is_zipcode]
    ziprateareas = target_zips.drop_duplicates(subset=['state','rate_area'])

    # DEBUG - Print out rate area match
    #print('\r\nRate Area Found: {state} {ratearea}'.format(
    #    state=ziprateareas['state'].iloc[0], ratearea=ziprateareas['rate_area'].iloc[0]
    #))
    #print(ziprateareas['state'],ziprateareas['rate_area'])

    # DEBUG - Test for multiple matched rate areas
    #if(len(ziprateareas.index) > 1):
    #    print('Multiple RateAreas Found: {state} {ratearea}'.format(
    #        state=ziprateareas['state'].iloc[0], ratearea=ziprateareas['rate_area'].iloc[0]
    #    ))
    return ziprateareas

# Main Entry Point of the Application
def main():
#     print("""\
#    _____ _      _____  _____ _____  
#   / ____| |    / ____|/ ____|  __ \ 
#  | (___ | |   | |    | (___ | |__) |
#   \___ \| |   | |     \___ \|  ___/ 
#   ____) | |___| |____ ____) | |     
#  |_____/|______\_____|_____/|_|     
#                                     """)
                                    
    #print("\r\nLoad CSV Files")

    # Parse the Plans, Zips, and SLCSP csv files
    plans = pd.read_csv('plans.csv')
    zips = pd.read_csv('zips.csv')
    slcsp = pd.read_csv('slcsp.csv')

    # Filter the plans to only the SILVER plans
    is_silver = plans['metal_level'] == "Silver"
    silver_plans = plans[is_silver]
    
    # DEBUG - print out the filtered silver plans
    #print(silver_plans)

    # Print required header row
    print("zipcode,rate")
    
    # For each zipcode in slcsp
    # lookup the state and rate area values.
    # Caveats:
    # If zip code is in more than one rate area
    # ignore that zip code
    for row in slcsp.itertuples():
        # Reset our targets
        TargetState = ""
        TargetRateArea = ""
        ratearea_slcsp_plans = ""

        # Resolve our zip code value to a rate area
        foundratearea = get_ratearea(row.zipcode,zips)
        
        # DEBUG - Print rate areas found
        #print('\r\nRate Area Found: {state} {ratearea}'.format(
        #    state=foundratearea['state'].iloc[0], ratearea=foundratearea['rate_area'].iloc[0]
        #))

        # DEBUG - Check for multiple rate areas in returned value
        #print('foundratearea.index length: ', len(foundratearea.index), 'Rate_area: {state} {ratearea}'.format(
        #    state=foundratearea['state'].iloc[0], ratearea=foundratearea['rate_area'].iloc[0]
        #))
        
        # Check if we returned multiple rate areas
        if(len(foundratearea.index) == 1):
            TargetState = foundratearea['state'].iloc[0]
            TargetRateArea = foundratearea['rate_area'].iloc[0]
            # Lookup the SLCSP plan rate
            # for the given State and Rate Area
            ratearea_slcsp_plans = get_slcsp(silver_plans, TargetState, TargetRateArea)
        
        # DEBUG - Print out the zipcode and rate unformatted
        #print(row.zipcode, ratearea_slcsp_plans)
        
        # Print out the resulting zipcode and rate
        print('{zipcode},{rate}'.format(
            zipcode=row.zipcode, rate=ratearea_slcsp_plans
        ))
    
    # DEBUG - Look up unique zip values
    #zips_unique = zips

    # DEBUG - Print out the loaded csv values
    #print(plans)
    #print(zips)
    #print(slcsp)

if __name__ == '__main__':
    main()