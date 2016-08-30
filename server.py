"""DOL & Google Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, GoogleReview, Case, Violation, Business

import os       # for use with keys in different file

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
# this is between the app and the browser to encrypt cookie
# could put in .sh file and load from environment
# make up a random string
app.secret_key = os.environ['APP_SECRET_KEY']
# app.secret_key = "ABC"

# Q: did this get fixed?? pull down my code for Ratings to check. (TBD)
# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


# TO DO LIST IN SERVER FILE
# 1. add a route that handles showing the relevancy (year) to the user
#       this will come from the datetime processing in the seed file

@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route("/cases")
def case_list():
    """Show list of cases."""

    cases = Case.query.all()
    # cases = Case.query.order_by('case_id').all()

    return render_template("case_list.html", cases=cases)


@app.route("/cases/<int:case_id>")
def case_detail(case_id):
    """Show info about a specific DOL case. For testing only"""

    case = Case.query.get(case_id)
    return render_template("case.html", case=case) #Q: What is the white case??

# Show an individual business
@app.route("/business/<int:bus_id>")
def business_detail(bus_id):
    """Show info about an individual business.

    This encompasses both Google Business info and DOL data
    """

    # TBD: Could use a mock data source here for testing/getting FE to work
    # hard code it... online json editor to create json file and put it in here as paste

    # Business object that has all the underlying fields/attributes
    # business = Business.query.get(bus_id)
    business = {"trade_nm": "My Business", "bus_id": 1234, "address": "1 Infinite Loop",\
            "city": "Cupertino", "state": "CA", "zipcode": 95014,\
            "g_overall_rating":4, "g_international_phone_number": "+1.408.974.6400",\
            "g_weekday_text": "weekday text", "g_maps_url": "http://maps.google.com",\
            "g_website":"http://www.apple.com", "g_vicinity": 4, "latitude":34.2,\
            "longitude":47.3, "place_id": 234}

    # business = {"name": "My Business", "bus_id": 1234, "place_id": 234}
    # business = Business.query.get(bus_id)
    return render_template("bus-review.html", business=business)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(host='0.0.0.0') #need the host specification 0.0.0.0 for vagrant
