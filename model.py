"""Models and database functions for DOL & Google project."""
#import heapq #what is this?
#import time
from flask_sqlalchemy import SQLAlchemy
#import correlation

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions written in Python using SQLAlchemy syntax
# db is inheriting from the .Model class and gives the structure

class Business(db.Model):
    """User of ratings website."""

    __tablename__ = "businesses"

    # column is a method on db that allows you to create a column in database
    bus_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    bus_address = db.Column(db.String(64), nullable=False)
    bus_city = db.Column(db.String(64), nullable=False)
    bus_state = db.Column(db.String(64), nullable=False)
    bus_phone = db.Column(db.String(64), nullable=False)
    bus_url = db.Column(db.String(255), nullable=True)
    bus_zipcode = db.Column(db.String(15), nullable=True)
    google_img = db.Column(db.String(255), nullable=True)
    
    # Define relationship from Business to GoogleReview table for each business
    # using it exp: google_review_instance.businesses
    google_review = db.relationship("GoogleReview",
        backref=db.backref("businesses"))
    # stick order_by in quotes

    #previously getting a reviewer_username not defined
    # google_review = db.relationship("GoogleReview",
    #     backref=db.backref("businesses", order_by="reviewer_username"))    

    def __repr__(self):
        """Provide helpful representation when printed to console rather
        than just saying it's an object"""

        return "<Business bus_id=%s bus_address=%s, %s, %s, %s>" % (
            self.bus_id, self.bus_address, self.bus_city, self.bus_state, 
            self.bus_zipcode)

    
    # def predict_rating(self, movie):
    #     """Predict user's rating of a movie."""

    #     other_ratings = movie.ratings

    #     similarities = [
    #         (self.similarity(r.user), r)
    #         for r in other_ratings
    #     ]

    #     similarities.sort(reverse=True)

    #     similarities = [(sim, r) for sim, r in similarities if sim > 0]

    #     if not similarities:
    #         return None

    #     numerator = sum([r.score * sim for sim, r in similarities])
    #     denominator = sum([sim for sim, r in similarities])

    #     return numerator/denominator

    # def similarity(self, other):
    #     """Return Pearson rating for user compared to other user."""

    #     u_ratings = {}
    #     paired_ratings = []

    #     for r in self.ratings:
    #         u_ratings[r.movie_id] = r

    #     for r in other.ratings:
    #         u_r = u_ratings.get(r.movie_id)
    #         if u_r:
    #             paired_ratings.append( (u_r.score, r.score) )

    #     if paired_ratings:
    #         return correlation.pearson(paired_ratings)

    #     else:
    #         return 0.0


class Case(db.Model):
    """Case is an individual case record of a business' violation """

    __tablename__ = "cases"

    case_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    
    # columns below come from DOL data - *** check the datatypes!!
    trade_nm = db.Column(db.String(100), nullable=False)
    legal_name = db.Column(db.String(100), nullable=True)
    street_addr_1_txt = db.Column(db.String(255), nullable=False)
    cty_nm = db.Column(db.String(100), nullable=False)
    st_cd = db.Column(db.String(2), nullable=False)
    zip_cd = db.Column(db.Integer, nullable=False)
    # change violation_code to the column name
    naic_cd = db.Column(db.Integer, db.ForeignKey('violations.naic_cd'), nullable=False)
    # number of violations found
    case_violtn_cnt = db.Column(db.Integer, nullable=False)
    # number of employees violated, can be 0
    cmp_assd_ee_violtd_cnt = db.Column(db.Numeric(12,2), nullable=False)
    ee_violtd_cnt = db.Column(db.Integer, nullable=False)
    bw_atp_amt =  db.Column(db.Numeric(12,2), nullable=False)
    ee_atp_cnt = db.Column(db.Integer, nullable=False)
 
    # start_date and end_date are the datetime formatted versions
    #   of DOL data columns findings_start_date and findings_end_date
    #   processed in the seed.py file
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    #violation_code = db.Column(db.Integer, db.ForeignKey(Violation.violation_code), nullable=False)
    #number_violations = db.Column(db.Integer, nullable=True)
    #employees_violated = db.Column(db.Integer, nullable=True)
    # Foreign keys should have specificity for nullable when not primary key
    bus_id = db.Column(db.Integer, db.ForeignKey('businesses.bus_id'), nullable=True)

    # ### NOTES - RELATIONSHIPS ###
    # Define relationships between tables to make it easier to navigate
    # the database by referring to other tables from given table without manual joins
    
    # Define relationship from Case to Violation table and Case to Business table
    # for each case. Call like this: case is an instance of Case class.
    #   case = Case.query.get(primary_key)
    #   python query example: case.violation.cases
    # backref is whatever I want to use to get the info back from Cases (not a table name)
    
    # New variable "violation" is an attribute of Cases class.
    # The backref("thingy",...) --> thingy is attribute in the Violation class.
    # Reference it as an attribute in violation: violation_instance.cases (attr)
    # order by column from the Case table
    violation = db.relationship("Violation",
                           backref=db.backref("cases", order_by=case_id))

    # # Define relationship from Case to Business
    business = db.relationship("Business",
                            backref=db.backref("cases", order_by=case_id))



    def __repr__(self):
        """Provide helpful representation when printed to console rather
        than just saying it's an object"""

        return "<Case trade_nm=%s street_addr_1_txt=%s>" % (
            self.trade_nm, self.street_addr_1_txt)


class Violation(db.Model):
    """Violation code and description list."""

    __tablename__ = "violations"

    # naic_cd maps to DOL column of naic_cd
    # naics_code_description maps to DOL column of naics_code_description
    naic_cd = db.Column(db.Integer, autoincrement=False, primary_key=True)
    naics_code_description = db.Column(db.String(255), nullable=False)
    
    
    def __repr__(self):
        """Provide helpful representation when printed to console rather
        than just saying it's an object"""

        return "<Violation code=%s description=%s>" % (
            self.naic_cd, self.naics_code_description)


class GoogleReview(db.Model):
    """Google Review of a business."""

    __tablename__ = "googlereviews"

    review_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('businesses.bus_id'), nullable=False)
    reviewer_username = db.Column(db.String(64), nullable=False)
    reviewer_rating = db.Column(db.Integer, nullable=False)
    reviewer_comments = db.Column(db.String(255), nullable=True)
    reviewer_photo = db.Column(db.String(255), nullable=True)
    
    
    def __repr__(self):
        """Provide helpful representation when printed to console rather
        than just saying it's an object"""

        return "<Google Review reviewer username=%s reviewer rating=%s>" % (
            self.reviewer_username, self.reviewer_rating)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    # the name of this "name" will be whatever I name it when I do createdb name
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///dol_project'
#    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
