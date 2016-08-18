"""Create a seed file to extract Google business data from the Google API
    and seed a database with that data. 

    Pseudocode:
    0. Extract fields from DOL database (name, address) - SQLAlchemy
    1. call Place Search API to get place_id using geocoding converting
          address from DOL file to lat/long (geopy?)
    2. using place_id call Place details API to get reviews/ratings (cap at 3 each or all?)
    3. pull down info for indiv google business based on trade name and address search fields
    4. if trade name and address add matched items to new database (??)

"""

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

import sys      #for use with sys.exit(0) debugging which stops the program at that point
import urllib2  # for use with the URL handling in address_to_longlat()
import urllib   # for urlencode since there is no urllib2.urlencode
import json
import os       # for use with keys in different file

#Google Maps API Key (activated) for GeoCoding
API_KEY = os.environ['GOOGLE_MAP_API']

def google_maps_address_to_json(street, city, state):
    """Convert individual DOL address to Google Maps API Geocoded JSON object"""

    address = street + ", " + city + ", " + state
    print address
    
    # TEST: use hard coded address to generate doctest in latlong_from_json()
    # longlat_url_dict = {
    #     'address' : '1095  Carolan Avenue, Burlingame, CA',
    #     'key' : os.environ['GOOGLE_MAP_API']
    #     }

    longlat_url_dict = {
        'address' : address,
        'key' : os.environ['GOOGLE_MAP_API']
        }

    # urlencode to handle the address with its variations (extra commas etc.)
    data = urllib.urlencode(longlat_url_dict)
    google_URL = "https://maps.googleapis.com/maps/api/geocode/json?%s" % data
    #print google_URL
    #print urllib.urlencode(google_URL)
    req = urllib2.Request(google_URL)
    json_response = urllib2.urlopen(req)
    response = json.loads(json_response.read())
    # print json.dumps(response, indent=4)


    # Note: Put the lat/long json parsing in separate function. Keep to test.
    # results = response['results']
    # # print len(results)
    # result = results[0]
    # # print json.dumps(result, indent=4)
    # geometry = result['geometry']
    # # print json.dumps(geometry, indent=4)
    # location = geometry['location']
    # # print json.dumps(location, indent=4)
    # latitude = location['lat']
    # print latitude
    # longitude = location['lng']
    # print longitude
    
    # test and stop program at this point to check output
    # print "unformatted response:"
    # print response
    # sys.exit(0)

    # return latitude, longitude

    return response

def latlong_from_json(response):
    """Get latitude and longitude from JSON.

        >>> input = {u'status': u'OK', u'results': [{u'geometry': {u'location': {u'lat': 37.587666, u'lng': -122.3623954}, u'viewport': {u'northeast': {u'lat': 37.58901498029149, u'lng': -122.3610464197085}, u'southwest': {u'lat': 37.5863170197085, u'lng': -122.3637443802915}}, u'location_type': u'ROOFTOP'}, u'address_components': [{u'long_name': u'1095', u'types': [u'street_number'], u'short_name': u'1095'}, {u'long_name': u'Carolan Avenue', u'types': [u'route'], u'short_name': u'Carolan Ave'}, {u'long_name': u'Burlingame Gardens', u'types': [u'neighborhood', u'political'], u'short_name': u'Burlingame Gardens'}, {u'long_name': u'Burlingame', u'types': [u'locality', u'political'], u'short_name': u'Burlingame'}, {u'long_name': u'San Mateo County', u'types': [u'administrative_area_level_2', u'political'], u'short_name': u'San Mateo County'}, {u'long_name': u'California', u'types': [u'administrative_area_level_1', u'political'], u'short_name': u'CA'}, {u'long_name': u'United States', u'types': [u'country', u'political'], u'short_name': u'US'}, {u'long_name': u'94010', u'types': [u'postal_code'], u'short_name': u'94010'}], u'place_id': u'ChIJUe9S2yV2j4ARuudMEeoZ1fQ', u'formatted_address': u'1095 Carolan Ave, Burlingame, CA 94010, USA', u'types': [u'street_address']}]}
        >>> latlong_from_json(input)
        (37.587666, -122.3623954)

    """

    results = response['results']
    # print len(results)
    result = results[0]
    # print json.dumps(result, indent=4)
    geometry = result['geometry']
    # print json.dumps(geometry, indent=4)
    location = geometry['location']
    # print json.dumps(location, indent=4)
    latitude = location['lat']
    # print latitude
    longitude = location['lng']
    
    print latitude, longitude
    
    # test and stop program at this point to check output
    #sys.exit(0)

    return latitude, longitude


def google_place_id(dol_name, latitude, longitude):
    """Get a Google place_id from the business name (from DOL data)
        and the latitude and longitude

        >>> place_id = 
        >>> print place_id


    """

    # google_places.nearby_search(name="Tai Wu", location="300 El Camino Real, Millbrae, CA")

    # # make sure that dictionary key names are the same as 
    # place_id_dict = {
    #     'name' : dol_name,
    #     'lat' : latitude,
    #     'lng' : longitude,
    #     'key' : os.environ['GOOGLE_MAP_API']
    #     }

    location = str(latitude) + "," + str(longitude)

    # make sure that dictionary key names are the same as 
    place_id_dict = {
        'location' : location,
        'radius' : 1,
        'name' : dol_name,
        'key' : os.environ['GOOGLE_MAP_API']
        }

    # https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=
    # -33.8670522,151.1957362&radius=500&type=restaurant&name=cruise&key=
    # AIzaSyBANee_piVPcowuyiHLV4sa9kkxUV5vv94

    data = urllib.urlencode(place_id_dict)
    # print data

    # data.lat or data = encoding(place_id_dict.latitude)??

    # structure the google URL with the place_id_dict fill-ins:
    # google_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + str(data['latitude']) + "," + str(data['longitude']) + "&radius=1&name=" + data['dol_name'] + "&key=" + data['key']


    google_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?%s" % data
    

    #google_URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=37.587666,-122.3623954&radius=1&name=Auto+Pride+Car+Wash,+Inc.&key=AIzaSyBANee_piVPcowuyiHLV4sa9kkxUV5vv94'

    #print "Place ID Google URL: " + google_URL

    # sys.exit(0)

    req = urllib2.Request(google_URL)
    json_response = urllib2.urlopen(req)
    response = json.loads(json_response.read())
    # print json.dumps(response, indent=4)

    results = response['results']
    # print len(results)
    # sys.exit(0)

    try:
        result = results[0]
        # print json.dumps(result, indent=4)
        place_id = result['place_id']
        # print json.dumps(place_id, indent=4)
        print place_id

        # sys.exit(0)

        # return a google place_id
        return place_id
    except Exception:
        pass
        #Q: Sarah suggested continue but this keeps failing and saying wrong place
        # SyntaxError: 'continue' not properly in loop

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

        response = google_maps_address_to_json(case.street_addr_1_txt, case.cty_nm, case.st_cd)
        latitude, longitude = latlong_from_json(response)
        place_id = google_place_id(case.trade_nm, latitude, longitude)
        # google_business_reviews = google_place_search(place_id)



