import re
import pandas as pd
import math
import glob

# reads through everything in don't touch courses, grabs the professor title and


professor_info = {}
csv_files = glob.glob("history_classes/dont_touch_courses/*.csv")




for filename in csv_files:
    
    df = pd.read_csv(filename)
    for _, row in df.iterrows():
        # clean name, removing abbreviations and other fluff.
        professor_full_name = re.sub(r"[.:|,\n\/]", "", row['instructor'].strip())
        
        syllabus = row['syllabus']
        if type(syllabus)==float:
            syllabus=""
        if len(syllabus)>0 and "grinnell.edu" not in syllabus:
            syllabus="https://www.grinnell.edu" + syllabus
        
        titles_list = ["Visiting", "Senior", "Asst", "Assist","Assistant", "Assoc", "Associate", "Professor", "Professors",
                   "Instructor", "Lecturer", "Inst"]

        components = professor_full_name.split()
        

        titles = [word for word in components if word in titles_list]
        names = [word for word in components if word not in titles_list ] 

        professor_title = " ".join(titles)
        professor_full_name = " ".join(names)
        

        # Store or update professor info
        if professor_full_name not in professor_info:
            professor_info[professor_full_name] = (professor_title, syllabus)
        else:
            # If the professor appears again, only update the title, not the syllabus
            current_title = professor_info[professor_full_name][0]
            if professor_title != current_title:  
                professor_info[professor_full_name] = (professor_title, syllabus)
        
professor_df = pd.DataFrame(professor_info.items(), columns=['instructor', 'TitleSyllabus'])

professor_df[['title', 'syllabus']] = pd.DataFrame(professor_df['TitleSyllabus'].tolist(), index=professor_df.index)
professor_df = professor_df.drop(columns=['TitleSyllabus'])

professor_df.to_csv('history_classes/data/prof_info.csv', index=False)



