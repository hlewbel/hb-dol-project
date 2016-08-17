# Pull down Google business data and put it inside a file
# make another seed file for google

import requests

from model import connect_to_db, db, GoogleReview, Case, Violation, Business
from flask import Flask, render_template, request, flash, redirect, session

# pseudocode:
# 1. call Place Search API to get place_id using geocoding converting
#       address from DOL file to lat/long (geopy?)
# 2. using place_id call Place details API to get reviews/ratings (cap at 3 each or all?)
# 3. pull down info for indiv google business based on trade name and address search fields
# 4. if trade name and address add matched items to new database (??)

# format for Place Search API: https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=-33.8670,151.1957&radius=500&types=food&name=cruise&key=AIzaSyBANee_piVPcowuyiHLV4sa9kkxUV5vv94

# request to database to get address using SQL alchemy (see ratings)

# http://www.{lkjljklj}.format


# user experience:
# 1. user searches with 3 pulldowns - city, business name

# Notes from Hb API lecture:
# r = requests.get("https://itunes.apple.com/search?term=honeydew")
# adict = r.json()

@app.route("/TBD")
def google_place_search(TBD: address???):
    """Get place_id from Google Place Search."""

    # Create an instance of all the cases
    cases = Case.query.all()

    # get a single case and query to extract address and zipcode
    case_zip = cases.zip_cd 
    case_addr = cases.street_addr_1_txt

    return render_template("case_list.html", cases=cases)

@app.route("/movies/<int:movie_id>", methods=['GET'])
def google_place_details(movie_id):
    """Using place_id as the key, get Google business info.

    Business info includes:
    """
    print "made it here"

    movie = Movie.query.get(movie_id)

    user_id = session.get("user_id")

    if user_id:
        user_rating = Rating.query.filter_by(
            movie_id=movie_id, user_id=user_id).first()

    else:
        user_rating = None

    # Get average rating of movie

    rating_scores = [r.score for r in movie.ratings]
    avg_rating = float(sum(rating_scores)) / len(rating_scores)

    prediction = None

    # Prediction code: only predict if the user hasn't rated it.

    if (not user_rating) and user_id:
        user = User.query.get(user_id)
        if user:
            prediction = user.predict_rating(movie)

    # Either use the prediction or their real rating

    if prediction:
        # User hasn't scored; use our prediction if we made one
        effective_rating = prediction

    elif user_rating:
        # User has already scored for real; use that
        effective_rating = user_rating.score

    else:
        # User hasn't scored, and we couldn't get a prediction
        effective_rating = None

    # Get the eye's rating, either by predicting or using real rating

    the_eye = User.query.filter_by(email="the-eye@of-judgment.com").one()
    eye_rating = Rating.query.filter_by(
        user_id=the_eye.user_id, movie_id=movie.movie_id).first()

    if eye_rating is None:
        eye_rating = the_eye.predict_rating(movie)

    else:
        eye_rating = eye_rating.score

    if eye_rating and effective_rating:
        difference = abs(eye_rating - effective_rating)

    else:
        # We couldn't get an eye rating, so we'll skip difference
        difference = None

    # Depending on how different we are from the Eye, choose a message

    BERATEMENT_MESSAGES = [
        "I suppose you don't have such bad taste after all.",
        "I regret every decision that I've ever made that has brought me" +
            " to listen to your opinion.",
        "Words fail me, as your taste in movies has clearly failed you.",
        "Did you watch this movie in an alternate universe where your taste doesn't suck?",
        "Words cannot express the awfulness of your taste."
    ]

    if difference is not None:
        beratement = BERATEMENT_MESSAGES[int(difference)]

    else:
        beratement = None

    return render_template(
        "movie.html",
        movie=movie,
        user_rating=user_rating,
        average=avg_rating,
        prediction=prediction,
        eye_rating=eye_rating,
        difference=difference,
        beratement=beratement
        )

