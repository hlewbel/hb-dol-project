README for DOL Project

Author: Hannah Lewbel
Creation date: 2016_08_08
Last updated: 2016_08_08

Working project name: Wage Wise
Alt title options: Accountable, Wage Justice

Description: Create a consumer-friendly accessible & responsive website that allows a user to search the US Department of Labor wage & hour violations data for a business, takes this DOL data and merges it with business listings data from Google to present both sets of data to the consumer.

US DOL Data: http://ogesdw.dol.gov/views/data_summary.php - this is the key/column listing: whd_data_dictionary  and this is the full database (large): whd_whisard

*** Note alt text for images - re accessibility
** WAS GOING TO USE JAVASCRIPT/JQUERY FOR SENDING FORM TO DOL (BUTTON CLICKS, ETC)

Project Outline:

Tables:

1. Google Review - this is a table of google reviews for a single business
    Table: review_id*, bus_id (FK) [Business table], reviewer_username, reviewer_rating, reviewer_comments, reviewer_photo?
2. Business - this is an individual business that has already been identified as having a DOL violation and a Google business record
    - Table: bus_id*, bus_address, bus_city, bus_state, bus_zip, bus_phone, bus_url, google_img?
3. Violation Categories - this is a list of unique labor violation types
    - Table: violation_code*, violation_description
    - Mapping: violation_code = naic_cd column in DOL data, violation_description = naics_code_description in DOL data 
4. Case - this is an individual case record of a business' violation
    - Table: case_id*, start_date, end_date, violation_code (FK) [Violation Categories], number_violations, employees_violated, bus_id (FK) [Business table]
    - Mapping: All the column data comes from the DOL data aside from bus_id

Calculations:
1. Relevancy (Python) - by time period, # violations
2. dol_rating/severity - ?
3. Average Google rating

Backend Dev:
1. Combine US DOL data with Google business data via name & address then import only matching businesses into database
2. 

User Flow:

1. User pulldowns for business type, business name, and location
2. 

**** TO UPDATE BELOW HERE ****
------

OLD User Flow -- need to update with the new plan to only have DOL businesses:
1. User search entry to search Google for a business type (like restaurant)
    - Business type (pull down to limit options)
    - Search by city name & state, zip code, or nearby
2. Google search results
    - mate user's search to business results using Google Place API
        https://developers.google.com/places/web-service/
    - STEPS: Learn how the URL modifications work
3. Map showing businesses nearby
    - GeoPy? Google Geocoder - are these the same?? 
        https://github.com/geopy/geopy/issues/171
4. Show DOL summary icon/marker on businesses that have DOL data
5. User selects a unique business
6. Unique business page loads
    - Shows Google business info
    - Shows DOL violation data summary & relevancy
    - optional click to see violation details
7. Allow user to report a violation on that business --> fill out form which submits to DOL in intake format (TBD)
    Questions:
        - What format could DOL take in?
        - How is normal violation reported? Web search didn't show obvious soln
        - 

Required functionality:
1. Accessible
2. Static imagees (unless easy way to pull all the image data from Google)
3. Simple page output (no ads/distractions)
4. Responsive webpage
5. Anonymize option for data submission to DOL?

Nice to Have Features:
1. Multiple Languages
2. Provide user with navigation instruction to get to that business
3. Suggest alternative businesses without violations in nearby location
4. Allow user to report a discrepancy (maybe new owner?)
5. Allow business commentary?
6. Show the underlying structure (including schema?) for the website (like inner clockwork)

Challenges:
1. Ethical interpretation of the data & presentation
2. Relevancy of the data

Future possibilities:
1. Description of Google focused search (more open): Create a consumer-friendly accessible & responsive website that allows a consumer to search Google for a business, takes any existing publicly-available wage and hours violation data from the US Department of Labor, and merges this with business listings data from Google to present both sets of data to the consumer. 


----
Python script to populate URLs with my API key and business data
Narrow scope by only searching businesses that have violations (my data) and then add the business data from Google for just those businesses


