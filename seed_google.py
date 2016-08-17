# # Create a seed file to extract Google business data from the Google API
# and seed a database with that data0. 

#Steps:
# Extract fields from DOL database (name, address) - SQLAlchemy
# 1. call Place Search API to get place_id using geocoding converting
#       address from DOL file to lat/long (geopy?)
# 2. using place_id call Place details API to get reviews/ratings (cap at 3 each or all?)
# 3. pull down info for indiv google business based on trade name and address search fields
# 4. if trade name and address add matched items to new database (??)

#### bonnie doing:
# dir(google_places)
# help(google_places.place...?)
# google places python wrapper get place id from human readable location
# google places geocode location
# from googleplaces import geocode_location
# geocode_location("address")
# add_place(...) -- see in slimkrazy
# > import googleplaces
# > my_latlong = geocode_location("address")
# #instantiate using key: google_places = GooglePlaces("API key")
# > google_places...
# maybe don't want to add a place

# > google_places.text_search(lat_lng = mylatlng,...)
# > google_places.nearby_search(lat_ng = my_latlng, radius=1)
# >dir(result)
# ****
# myl_atlng = geocode_location("address") --> lat long
# result = google_places.nearby_search(lat_lng = my_latlng, radius=1 )
# result
# first_place = result.places[0] --> this seems to just give city back
#
# result.places[0].get_details()
#result.places[0].review
#myp_place.rating
#

# Employee.query.filter_by(name='Liz')
# Employee.query.filter(Employee.name == 'Liz')
# db.session.query(Employee.id, Employee.name).all()

# can get actual restaurant from this: 
# google_places.nearby_search(name="Tai Wu", location="300 El Camino Real, Millbrae, CA")

from sqlalchemy import func

from model import Business, Case, Violation, GoogleReview, connect_to_db, db
from server import app
from googleplaces import GooglePlaces, types, lang

import sys #for use with sys.exit(0) debugging which stops the program at that point
import urllib2 # for use with the URL handling in address_to_longlat()
import urllib # for urlencode since there is no urllib2.urlencode
import json

#TBD - store this in the secrets file and access how?
API_KEY = ""

def address_to_longlat(street, city, state):

    address = street + ", " + city + ", " + state
    print address

    #convert address to long/latitude
    
    longlat_url_dict = {
        'address' : address,
        'key' : 'AIzaSyBANee_piVPcowuyiHLV4sa9kkxUV5vv94'
        }

    # urlencode to handle the address with its variations
    data = urllib.urlencode(longlat_url_dict)
    google_URL = "https://maps.googleapis.com/maps/api/geocode/json?%s" % data
    # print google_URL
    #print urllib.urlencode(google_URL)
    req = urllib2.Request(google_URL)
    json_response = urllib2.urlopen(req)
    response = json.loads(json_response.read())
    # print json.dumps(response, indent=4)

    results = response['results']
    # print len(results)
    result = results[0]
    # print json.dumps(result, indent=4)
    geometry = result['geometry']
    # print json.dumps(geometry, indent=4)
    location = geometry['location']
    # print json.dumps(location, indent=4)
    latitude = location['lat']
    print latitude
    longitude = location['lng']
    print longitude
    
    # sys.exit(0)

    return latitude, longitude


def google_place_id(dol_name, dol_longlat):

    # return a google place_id

    return place_id

def google_place_search(place_id):

    # return an object (dictionary) of a business' google business reviews

    return None
# PLACEHOLDER: group business listings by city for later mapping (nearby?)
def group_by_city():

    return None

if __name__ == "__main__":
    connect_to_db(app)
    #db.droptable # ??? --- or command line(> dropdb dol_project) or in each table
    db.create_all()

    # Use SQLAlchemy to get all the cases from the dol_project database (seeded by seed.py)
    cases = Case.query.all()

    # get each case details (case_id, street_addr_1_txt, cty_name, st_cd)
    # and store in a dictionary by case_id
    for case in cases:
        dol_longlat = address_to_longlat(case.street_addr_1_txt, case.cty_nm, case.st_cd)
        # place_id = google_place_id(case.trade_nm, dol_longlat)
        # google_business_reviews = google_place_search(place_id)



