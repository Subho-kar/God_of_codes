import os
import sys
from astropy.io import fits
from astropy import units as u
from astropy.coordinates import SkyCoord
from astroquery.simbad import Simbad


def Loadfitsfile(fits_filename):

    with fits.open(fits_filename) as hdul:
        header = hdul[0].header

        ra_str = header["RA"]
        dec_str = header["DEC"]
        #object_name = header.get("OBJECT", "Unknown Target")

    print(f"File: {fits_filename}")
    #print(f"Target Header Name: {object_name}")
    print(f"Header Coordinates: RA = {ra_str}, DEC = {dec_str}")


    coord = SkyCoord(ra_str, dec_str, unit=(u.hourangle, u.deg), frame="icrs")

    radius = 0.5 * u.arcmin
    print(f"\nSearching SIMBAD within {radius} of parsed position...")

    result_table = Simbad.query_region(coord, radius=radius)

    if result_table is not None:

        found_coords = SkyCoord(
            result_table["ra"], 
            result_table["dec"], 
            unit=(u.hourangle, u.deg), 
            frame="icrs"
        )
        
        # Calculate angular separation between target and retrieved sources
        separations = coord.separation(found_coords).to(u.arcsec)
        
        # Add calculated distance column (rounded to 2 decimal places)
        result_table["distance_arcsec"] = separations.round(2)
        
        # Sort results by closest distance
        result_table.sort("distance_arcsec")
        
        print(f"\nFound {len(result_table)} source(s):\n")
        result_table.pprint_all()
    else:
        print("No sources found within the specified radius.")

def AskAndLoadData(toask="Enter the name of science star spectrum file (ending with u1we.fits) :", inpfilename=None):
    """ Asks user to enter filename """
    
    while True:  #Keep asking till a file is properly loaded
        filename = input(toask).strip(' ') if inpfilename is None else inpfilename
        try :
            if os.path.splitext(filename)[1] == '.fits' : #User has inputed a fits file
                Loadfitsfile(filename)
            else: 
                print("Error: Cannot find the file, Please give the correct file name.")
                break
        except IOError :
            print("Error: Cannot find the file %s, Please give the correct file name."%(filename))
            inpfilename = None
        else:
            sys.exit(1)

def KeyboardInterrupt_handler():
    print('\nYou pressed Ctrl+C!')
    print('Stopping the tool...')
    sys.exit(2)
    
def main():

    PARENT_DIR = os.getcwd()
    print('Working on the directory : ', PARENT_DIR)

    try:
    
        scifname = None     #File initialisation
        AskAndLoadData(toask="Enter the name of science star spectrum file (ending with u1we.fits):", inpfilename=scifname)
    except KeyboardInterrupt:
        KeyboardInterrupt_handler()
    
    print("Thank you for using the name search tool.")    

if __name__ == "__main__":
    main() 
