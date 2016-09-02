"""Seed file for the Business database using both DOL data and Google data

    Pseudocode
    0. Get a DOL case & extract name and address fields (SQLAlchemy)
    1. Use DOL address for Google Maps API to get geocoded JSON
    2. Parse Google Maps API JSON to get latitude and longitude
    3. Use latitude and longitude for new Google API call to get place_id
    4. Call Google Place Details API using place_id to get business details, reviews, ratings
    5. If trade name and address add matched items to new database (??)

    #TBD: Store Google place_id and long/lat in final output database in conjunction with case ID

"""

import datetime
import csv
import sys      #for use with sys.exit(0) debugging which stops the program at that point
import urllib2  # for use with the URL handling in address_to_longlat()
import urllib   # for urlencode since there is no urllib2.urlencode
import json
import os       # for use with keys in different file

from sqlalchemy import func
from model import Business, Case, Violation, GoogleReview, connect_to_db, db
from server import app
from googleplaces import GooglePlaces, types, lang


#Google Maps API Key (activated) for GeoCoding
API_KEY = os.environ['GOOGLE_MAP_API']

def seed_db():
    """Seed database with case and business info using dol_data_subset.csv and Google business info."""
    # i think this should be cases

    # print to console
    print "Seeding Database Tables"

    # Delete all rows in tables, so if we need to run this a second time,
    # we wont be trying to add duplicate items
    Case.query.delete()
    Business.query.delete()
    Violation.query.delete()
    GoogleReview.query.delete()

    # Parse csv file this wayrather than using rstrip and split on ","
    # because some of the addresses have commas & suites and special chars
    with open('test_data/dol_data_subset.csv') as csvfile:
        dol_file = csv.reader(csvfile)
        for row in dol_file:
            case_id, trade_nm, legal_name, street_addr_1_txt, cty_nm, \
            st_cd, zip_cd, naic_cd, naics_code_description, case_violtn_cnt, \
            cmp_assd_ee_violtd_cnt, ee_violtd_cnt, bw_atp_amt, ee_atp_cnt, \
            findings_start_date, findings_end_date = row[:16]

            # The date is in the file as daynum-month_abbreviation-year;
            # Convert to datetime object. Date comes in as M/DD/YY (%m/%d/%y)
            start_date = datetime.datetime.strptime(findings_start_date, "%m/%d/%y")
            end_date = datetime.datetime.strptime(findings_end_date, "%m/%d/%y")

            # * * * TBD: EXTRACT YEAR FROM START_DATE & END_DATE * * *
            # Use this for calculating dol_relevancy
            #   If start date exists, then extract year and month (don't care about day)
            #   If end date exists, then extract year and month (don't care about day)

            #Making an instance of Violation and adding to violation table
            # only if naic_cd doesn't exist yet
            if (Violation.query.filter_by(naic_cd=naic_cd).first() == None):
                violation = Violation(naic_cd=naic_cd,
                            naics_code_description=naics_code_description)
                db.session.add_all([violation])


            # Call Google functions to get Google business and review data via APIs
            response = google_maps_address_to_json(street_addr_1_txt, cty_nm, st_cd)
            latitude, longitude = latlong_from_json(response)
            place_id = google_place_id(trade_nm, latitude, longitude)
            g_business_dict, reviews_list = google_place_details(place_id):


            # Seed business table with case info from row (local vars) + g_business_dict
            # Do not specify bus_id (PK) here as it's autoincrementing and doesn't need to be passed in
            business = Business(place_id=place_id,
                                latitude=latitude,
                                longitude=longitude,
                                trade_nm=trade_nm,
                                legal_nm=legal_nm,
                                street_addr_1_txt=street_addr_1_txt,
                                cty_nm=cty_nm,
                                st_cd=st_cd,
                                zip_cd=zip_cd,
                                g_international_phone_number=g_business_dict.g_international_phone_number,
                                g_primary_img_url=g_business_dict.g_primary_img_url,
                                g_weekday_text=g_business_dict.g_weekday_text,
                                g_overall_rating=g_business_dict.g_overall_rating,
                                g_maps_url=g_business_dict.g_maps_url,
                                g_website=g_business_dict.g_website,
                                g_vicinity=g_business_dict.g_vicinity,
                                dol_rating=dol_rating,
                                dol_severity=dol_severity,
                                dol_relevancy=dol_relevancy
                                )

            db.session.add(business)
            db.session.commit(business)

            # Create instance review of GoogleReview and seed googlereviews table
            # (orange model.py=white seed_business.py)
            review = GoogleReview(bus_id=bus_id,
                                author_name=author_name,
                                author_url=author_url,
                                language=language,
                                rating=rating,
                                text=text
                                )


            db.session.add(review)
            db.session.commit(review)

            # Create an instance case of Case and seed cases table
            # (orange model.py=white seed_business.py)
            case = Case(case_id=case_id,
                        bus_id=business.bus_id,
                        start_date=start_date,
                        end_date=end_date,
                        trade_nm=trade_nm,
                        legal_name=legal_name,
                        street_addr_1_txt=street_addr_1_txt,
                        cty_nm=cty_nm,
                        st_cd=st_cd,
                        zip_cd=zip_cd,
                        naic_cd=naic_cd,
                        case_violtn_cnt=case_violtn_cnt,
                        cmp_assd_ee_violtd_cnt=cmp_assd_ee_violtd_cnt,
                        ee_violtd_cnt=ee_violtd_cnt,
                        bw_atp_amt=bw_atp_amt,
                        ee_atp_cnt=ee_atp_cnt
                        )

            db.session.add(case)
            db.session.commit(case)


    # Commit the update to the database. Only do this once.
    #Q: is this still needed since above committed by instance??
    db.session.commit()

    return None


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
    """Get latitude and longitude from JSON. Return latitude, longitude.

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

        # >>> place_id = 'ChIJs_yO1mWfj4ARFzJiFB9k2mY'
        # >>> google_place_details(place_id)
        # #TBD: business details...

    """

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

    # Create dictionary to store all the g_business info and return to main function
    g_business_dict = {'status':status,
                        'icon'=icon,
                        'g_international_phone_number' = international_phone_number



    }
    # ****************************
    # TBD: Return 2 things:
    # 1. Create dictionary to store all the g_business info and return to main function
    # 2. Return reviews to main function with another function call to do the review processing separately from here down
    # named: g_business_dict, reviews_list

    # dictionary to store all the g_business info and return to main function
    reviews_list = {}
    # TBD: BREAK THIS OUT

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

        # * * * TBD: Seed my review table here not create dictionary and access by bus_id (FK)
        
        seed_google_review_table(author_name, author_url, language, rating, text)
        # create a dictionary to store all of the google photo details
        # reviews_dict = {
        #     'author_name' : author_name,
        #     'author_url' : author_url,
        #     'language' : language,
        #     # 'profile_photo_url' : profile_photo_url,
        #     'rating' : rating,
        #     'text' : text,
        #     # 'key' : os.environ['GOOGLE_MAP_API']
        #     }
        
        # sys.exit(0)

    # **** STOPPED HERE ****


    return g_business_dict, reviews_list

    # except Exception:
    #     print "Something went wrong"

    #TBD: output the google review info to a file!
    #if entry does not exist in database the add it

    # google_business_review = {TBD}
    # # return google review information for a single business in dict
    # return google_business_review

# PLACEHOLDER: group business listings by city for later mapping (nearby?)
# def group_by_city():

#     return None

# def google_map_nearby():

#     return None

if __name__ == "__main__":

    connect_to_db(app)
    #db.droptable # ??? --- or command line(> dropdb dol_project) or in each table
    db.create_all()

    seed_db()

