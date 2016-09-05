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

    return render_template("homepage.html")


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

    businesses = Business.query.all()
    # cases = Case.query.order_by('case_id').all()

    #Q: How to link to a specific case and render the next page?
    return render_template("business_list.html", businesses=businesses)

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
@app.route("/business")
def business_detail():
    """Show info about an individual business.

    This encompasses both Google Business info and DOL data
    """

    # import ipdb; ipdb.set_trace()

    search_trade_nm = request.args.get("trade_nm")
    search_cty_nm = request.args.get("cty_nm")

    # Get a single case with matching trade name and city
    case = Case.query.filter(Case.trade_nm==search_trade_nm,Case.cty_nm==search_cty_nm).first()

    if not case:
        #add a flash message (shopping cart)
        return redirect('/')

    # Use the case.bus_id FK to uniquely select a business
    bus_id = case.bus_id 

    # Business object that has all the underlying fields/attributes
    business = Business.query.get(bus_id)
    if not business:
        #add a flash message (shopping cart)
        return redirect('/')

    # DOL case relevancy (subjective and determined by year)
    if (int(case.end_date.year) < 2000):
        dol_relevancy = "This business had wage violations before the year 2000"
    elif (int(case.end_date.year) >= 2000):
        dol_relevancy = "This business had wage violations after the year 2000"

    #DOL Severity is determined by $ amount per employee 
    dol_amt_paid_per_employee = int(case.bw_atp_amt/case.ee_atp_cnt)

    if (dol_amt_paid_per_employee == 0):
        dol_severity = 'Violation Level = Green: Employer was not found to violate employee wages or data was insufficient to determine if there was a violation'
        dol_rating = 5
    elif (dol_amt_paid_per_employee > 1000):
        dol_severity = 'Violation Level = Red: Employer had to pay more than $1000 per employee'
        dol_rating = 1
    elif (dol_amt_paid_per_employee > 499) and (amt_paid_per_employee < 1001):
        dol_severity = 'Violation Level = Orange: Employer had to pay each employee between $500-$1000'
        dol_rating = 3
    elif (dol_amt_paid_per_employee < 500):
        dol_severity = 'Violation Level = Yellow: Employer had to pay each employee less than $500'
        dol_rating = 4


    # #rating,severity,relevancy
    # dol_calc_dict = {
    #     'dol_amt_paid_per_employee' : dol_amt_paid_per_employee,
    #     'dol_severity' : dol_severity,
    #     'dol_rating' : dol_rating,
    #     'dol_relevancy' : dol_relevancy
    #     }

    business.dol_severity = dol_severity
    business.dol_rating = dol_rating
    business.dol_relevancy = dol_relevancy

    db.session.add(business)
    db.session.commit()

    cases_for_business = Case.query.filter(bus_id==business.bus_id).all()

    # * * * STOPPED HERE 9/4 * * *

    # TBD: Could use a mock data source here for testing/getting FE to work
    # hard code it... online json editor to create json file and put it in here as paste

    # business = {"trade_nm": "My Business", "bus_id": 1234, "address": "1 Infinite Loop",\
    #         "city": "Cupertino", "state": "CA", "zipcode": 95014,\
    #         "g_overall_rating":4, "g_international_phone_number": "+1.408.974.6400",\
    #         "g_weekday_text": "weekday text", "g_maps_url": "http://maps.google.com",\
    #         "g_website":"http://www.apple.com", "g_vicinity": 4, "latitude":34.2,\
    #         "longitude":47.3, "place_id": 234}


    # return render_template("bus-review.html", business=business, case=case, dol_calc_dict=dol_calc_dict)
    return render_template("bus-review.html", business=business, case=case, cases_for_business=cases_for_business)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(host='0.0.0.0') #need the host specification 0.0.0.0 for vagrant
