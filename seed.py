"""Utility file to seed DOL Google database from DOL data in seed_data/"""

import datetime
import csv

from sqlalchemy import func

from model import Business, Case, Violation, GoogleReview, connect_to_db, db
from server import app

def load_cases():
    """Load cases from DOL data dol_data_subset.csv into database."""
    # i think this should be cases

    # print to console
    print "Cases"

    # Delete all rows in table, so if we need to run this a second time, we wont be trying to add duplicate items
    # Q: this line fails so temporarily deleting it for debugging help
    Case.query.delete()

    # use this way to parse csv file rather than rstrip and split on ","
    # because some of the addresses have commas inside their street address
    # designating suite
    # removed header from file
    with open('test_data/dol_data_subset.csv') as csvfile:
        dol_file = csv.reader(csvfile)
        for row in dol_file:
            case_id, trade_nm, legal_name, street_addr_1_txt, cty_nm, \
            st_cd, zip_cd, naic_cd, naics_code_description, case_violtn_cnt, \
            cmp_assd_ee_violtd_cnt, ee_violtd_cnt, bw_atp_amt, ee_atp_cnt, \
            findings_start_date, findings_end_date = row[:16]


    # look at how to do this with a header line or remove it from my data
    # for i, row in enumerate(open("test_data/dol_data_subset.csv")):


    #     row = row.rstrip()
    #     # print row
    #     #row.split returns a list then it will unpack
    #     # note: split into multiple lines using the backslash escape
    #     case_id, trade_nm, legal_name, street_addr_1_txt, cty_nm, \
    #     st_cd, zip_cd, naic_cd, naics_code_description, case_violtn_cnt, \
    #     cmp_assd_ee_violtd_cnt, ee_violtd_cnt, bw_atp_amt, ee_atp_cnt, \
    #     findings_start_date, findings_end_date = row.split(",")[:16]

        #put in python csv reader so that it can catch commas within a column

        # Strip out the date information from the findings_start_date
        # and findings_end_date and get years for relevancy.
        # Will use end-year as relevancy information, and display start year
        # and end year as data on webpage

        # pseudocode:
        #   If start date exists, then extract year and month (don't care about day)
        #   If end date exists, then extract year and month (don't care about day)


        # The date is in the file as daynum-month_abbreviation-year;
        # it needs to be converted to an actual datetime object.

        # date comes in as M/DD/YY (%m/%d/%y)
            start_date = datetime.datetime.strptime(findings_start_date, "%m/%d/%y")
            end_date = datetime.datetime.strptime(findings_end_date, "%m/%d/%y")


        # ***** add google seed info in here.

        # making an instance of Case (orange model.py=white seed.py)
        # SEED THE CASE TABLE THIS AFTER I GET THE PLACE_ID
            case = Case(case_id=case_id,
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
                        ee_atp_cnt=ee_atp_cnt,
                        # TBD: place_id=place_id
                        )

            #making an instance of Violation
            # pseudocode: if naic_cd exists in violation table, don't add

            if (Violation.query.filter_by(naic_cd=naic_cd).first() == None):
                violation = Violation(naic_cd=naic_cd,
                            naics_code_description=naics_code_description)
                db.session.add_all([case,violation])
            else:
                db.session.add_all([case])





            # # Add to the session so it will be stored after commitment
            # #db.session.add(case)
            # #db.session.add(violation)
            # # can commit all using a list
            # db.session.add_all([case,violation])

            # REMOVE_FINAL
            # Show progress for debugging (print every 100 rows)
            # if i % 100 == 0:
            #     print i

    # Commit the update to the database. Only do this once.
    db.session.commit()



# def load_ratings():
#     """Load ratings from google into database??"""

#     print "Ratings"

#     #create a google_ratings.csv file with all the ratings data
#     for i, row in enumerate(open("seed_data/google_ratings.csv")):
#         row = row.rstrip()

#         user_id, movie_id, score, timestamp = row.split("\t")

#         user_id = int(user_id)
#         movie_id = int(movie_id)
#         score = int(score)

#         # We don't care about the timestamp, so we'll ignore this

#         rating = Rating(user_id=user_id,
#                         movie_id=movie_id,
#                         score=score)

#         # We need to add to the session or it won't ever be stored
#         db.session.add(rating)

#         # provide some sense of progress
#         if i % 1000 == 0:
#             print i

#             # An optimization: if we commit after every add, the database
#             # will do a lot of work committing each record. However, if we
#             # wait until the end, on computers with smaller amounts of
#             # memory, it might thrash around. By committing every 1,000th
#             # add, we'll strike a good balance.

#             db.session.commit()

#     # Once we're done, we should commit our work
#     db.session.commit()


# def set_val_user_id():
#     """Set value for the next user_id after seeding database"""

#     # Get the Max user_id in the database
#     result = db.session.query(func.max(User.user_id)).one()
#     max_id = int(result[0])

#     # Set the value for the next user_id to be max_id + 1
#     query = "SELECT setval('users_user_id_seq', :new_id)"
#     db.session.execute(query, {'new_id': max_id + 1})
#     db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)
    #db.droptable # ??? --- or command line(> dropdb dol_project) or in each table
    db.create_all()

    #change these to my functions
    load_cases()
    # load_movies()
    # load_ratings()
    # set_val_user_id()

    
