from bs4 import BeautifulSoup as bs
import pandas as pd
from email_from_syllabus import find_email

instructor_dict = {}
df = pd.read_csv('history_classes/merged/classes.csv')    

# goes through every row in classes.csv, accessing the syllabus and scraping it for emails.
# outputs a csv containg the instructor, syllabus, and email.

for index, row in df.iterrows():
    instructor_name = row['instructor'] 
    syllabus = row['syllabus'] if pd.notna(row['syllabus']) else ""
    
    if syllabus:
        email = find_email(syllabus, row['instructor'].split()[1]) # if there are multiple instructors teaching the course, arbitrarily select first one.
        if not ( len(email)==0 and instructor_name in instructor_dict.keys()): #add if there is an email associated with this instructor, or the instructor wasn't in the dict already
            instructor_dict[instructor_name] = {
                'syllabus': syllabus,
                'email': email
            }

instructor_data = []
for instructor, data in instructor_dict.items():
    instructor_data.append({
        'instructor': instructor,
        'syllabus': data['syllabus'],
        'email': data['email']
    })
result_df = pd.DataFrame(instructor_data)

result_df.to_csv('history_classes/data/instructor_emails.csv', index=False)
