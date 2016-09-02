"""DOL & Google Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, GoogleReview, Case, Violation, Business

import os       # for use with keys in different file

app = Flask(__name__)
app.jinja_env.auto_reload = True #this fixes a refresh error bug

# Required to use Flask sessions and the debug toolbar
# this is between the app and the browser to encrypt cookie
# could put in .sh file and load from environment
# make up a random string
app.secret_key = os.environ['APP_SECRET_KEY']
# app.secret_key = "ABC"

# Normally, if you refer to an undefined variable in a Jinja template,
# Jinja silently ignores this. This makes debugging difficult, so the following
# sets an attribute of the Jinja environment that says to make this an
# error.
app.jinja_env.undefined = StrictUndefined


# TO DO LIST IN SERVER FILE
# 1. add a route that handles showing the relevancy (year) to the user
#       this will come from the datetime processing in the seed file

@app.route('/')
def index():
    """Homepage."""

    cases = Case.query.all()
    return render_template("homepage.html", cases=cases)


@app.route("/cases")
def case_list():
    """Show list of cases."""

    cases = Case.query.all()
    # cases = Case.query.order_by('case_id').all()

    #Q: How to link to a specific case and render the next page?


    return render_template("case_list.html", cases=cases)

@app.route("/businesses")
def business_list():
    """Show list of cases."""

    business = Business.query.all()
    # cases = Case.query.order_by('case_id').all()

    #Q: How to link to a specific case and render the next page?
    return render_template("business_list.html", business=business)

@app.route("/about")
def about():
    """About the program text"""

    return render_template("about.html")

@app.route("/dollinks")
def dollinks():
    """Helpful DOL related links"""

    return render_template("dol_links.html")

@app.route("/cases/<int:case_id>")
def case_detail(case_id):
    """Show info about a specific DOL case. For testing only"""

    case = Case.query.get(case_id)
    return render_template("case.html", case=case) # orange is jinja in html, white is variable here



# 1. create route that loads a search form - use ratings or shopping site
# 2. create another route to load the result - get info from form and pass to a query within this route
# look up return redirect how to load movie/profile

# render form (see register_form in ratings)
# # user enters data in form --> when submit (in html) and action has next url 
# that takes to register_process()
# get the form info - bind form info to these variables
# new search = query table
# ... redirect



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
