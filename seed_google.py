"""Create a seed file to extract Google business data from the Google API
    and seed a database with that data. 

    Pseudocode:
    0. Extract fields from DOL database (name, address) - SQLAlchemy
    1. call Place Search API to get place_id using geocoding converting
          address from DOL file to lat/long (geopy?)
    2. using place_id call Place details API to get reviews/ratings (cap at 3 each or all?)
    3. pull down info for indiv google business based on trade name and address search fields
    4. if trade name and address add matched items to new database (??)

    #TBD: Store Google place_id and long/lat in final output database in conjunction with case ID

"""

# * * * HELPFUL NOTES DURING DEV * * *

# Employee.query.filter_by(name='Liz')
# Employee.query.filter(Employee.name == 'Liz')
# db.session.query(Employee.id, Employee.name).all()

# can get actual restaurant from this: 
# google_places.nearby_search(name="Tai Wu", location="300 El Camino Real, Millbrae, CA")

# * * * * * * * * * * * * * * * * * * *

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
    
    # print latitude, longitude
    
    # test and stop program at this point to check output
    #sys.exit(0)

    return latitude, longitude


def google_place_id(dol_name, latitude, longitude):
    """Get a Google place_id by using incoming business name from DOL data
        and the latitude and longitude acquired in the latlong_from_json()

        >>> dol_name = 'Avanti Pizza & Pasta (Belmont)'
        >>> latitude = 37.5125194
        >>> longitude = -122.2941039
        >>> google_place_id(dol_name, latitude, longitude)
        u'ChIJs_yO1mWfj4ARFzJiFB9k2mY'

    """

    location = str(latitude) + "," + str(longitude)

    # make sure that dictionary key names are the same as URL needs
    place_id_dict = {
        'location' : location,
        'radius' : 1,
        'name' : dol_name,
        'key' : os.environ['GOOGLE_MAP_API']
        }

    data = urllib.urlencode(place_id_dict)
    # print data

    google_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?%s" % data
    
    #TESTING:
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
        #print place_id

        # sys.exit(0)

        # return a google place_id
        return place_id
    except Exception:
        pass

def google_place_details(place_id):
    """Get a Google business review data by using incoming Google place_id

        >>> place_id = 'ChIJs_yO1mWfj4ARFzJiFB9k2mY'
        >>> google_place_details(place_id)
        #TBD: business details...

    """

    #TBD: Check if db already has place_id before running this code
    
    place_details_dict = {
        'placeid' : place_id,
        'key' : os.environ['GOOGLE_MAP_API']
        }

    data = urllib.urlencode(place_details_dict)
    # print data

    #example URL: 
    #https://maps.googleapis.com/maps/api/place/details/json?placeid=ChIJN1t_tDeuEmsRUsoyG83frY4&key=YOUR_API_KEY
    
    google_URL = "https://maps.googleapis.com/maps/api/place/details/json?%s" % data
    # return an object (dictionary) of a business' google business reviews

    req = urllib2.Request(google_URL)
    json_response = urllib2.urlopen(req)
    response = json.loads(json_response.read())
    # print json.dumps(response, indent=4)

    status = response['status']
    print json.dumps(status, indent=4)

    result = response['result']
    # print json.dumps(result, indent=4)
    icon = result['icon']
    print json.dumps(icon, indent=4)
    international_phone_number = result['international_phone_number']
    print json.dumps(international_phone_number, indent=4)    
    name = result['name']
    print json.dumps(name, indent=4)
    opening_hours = result['opening_hours']
    print json.dumps(opening_hours, indent=4)
    # open_now = opening_hours['open_now']
    # print json.dumps(open_now, indent=4)

    json_weekday_text = opening_hours['weekday_text']
    print json.dumps(json_weekday_text, indent=4)
    #convert list to string w/ | delim 
    #(TBD: convert back when read from db, split on |. pass to JS front end)
    weekday_text = '|'.join(json_weekday_text)
    print weekday_text

    overall_rating = result['rating']
    print "overall rating is: "
    print json.dumps(overall_rating, indent=4)
    types = result['types']
    print json.dumps(types, indent=4)
    url = result['url']
    print json.dumps(url, indent=4)
    website = result['website']
    print json.dumps(website, indent=4)
    vicinity = result['vicinity']
    print json.dumps(vicinity, indent=4)

    # #get Google photos for the business
    # #TBD: add a try/except (may not have any photos)

    # photos = result['photos']
    # primary_photo = photos[0]
    # # print json.dumps(primary_photo, indent=4)

    # for photo in photos:
    #     photo_reference = photo['photo_reference']
    #     print json.dumps(photo_reference, indent=4)
    #     height = photo['height']
    #     print json.dumps(height, indent=4)
    #     width = photo['width']
    #     print json.dumps(width, indent=4)
    #     html_attributions = photo['html_attributions']
    #     print json.dumps(html_attributions, indent=4)

    #     # create a dictionary to store all of the google photo details
    #     photo_details_dict = {
    #         'photo_reference' : photo_reference,
    #         'height' : height,
    #         'width' : width,
    #         'html_attributions' : html_attributions,
    #         # 'key' : os.environ['GOOGLE_MAP_API']
    #         }

    #     # data = urllib.urlencode(photo_details_dict)
    #     # photos_base_URL = "https://maps.googleapis.com/maps/api/place/photo?%s" % data

    #     #???? TBD - did i forget to do something here?

    #get Google reviews for the business
    #TBD: add a try/except (may not have any reviews)

    reviews = result['reviews']

    for review in reviews:
        author_name = review['author_name']
        print json.dumps(author_name, indent=4)
        author_url = review['author_url']
        print json.dumps(author_url, indent=4)
        language = review['language']
        print json.dumps(language, indent=4)
        # profile_photo_url = review['profile_photo_url']
        # print json.dumps(profile_photo_url, indent=4)
        rating = review['rating']
        print json.dumps(rating, indent=4)
        text = review['text']
        print json.dumps(text, indent=4)

        # create a dictionary to store all of the google photo details
        reviews_dict = {
            'author_name' : author_name,
            'author_url' : author_url,
            'language' : language,
            # 'profile_photo_url' : profile_photo_url,
            'rating' : rating,
            'text' : text,
            # 'key' : os.environ['GOOGLE_MAP_API']
            }
        
        sys.exit(0)

    # **** STOPPED HERE ****

    # Create a Google Review database with the details...
    # Q: how to take all the info out and put it in columns...???
    # -- create a dictionary with all the info??

    # google_business_review = {
    #         'reviews_dict' : reviews_dict,
    #         'photo_details' : author_url,

    # }

    return international_phone_number
    # except Exception:
    #     print "Something went wrong"

    #TBD: output the google review info to a file!
    #if entry does not exist in database the add it

    # google_business_review = {TBD}
    # # return google review information for a single business in dict
    # return google_business_review

# PLACEHOLDER: group business listings by city for later mapping (nearby?)
def group_by_city():

    return None

def google_map_nearby():

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
        international_phone_number = google_place_details(place_id)




