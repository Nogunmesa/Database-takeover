import csv
import requests
from pypdf import PdfReader
from io import BytesIO
import re
from bs4 import BeautifulSoup as bs
import pandas as pd

faculty_url = "https://www.grinnell.edu/profiles/history/faculty"
page = requests.get(faculty_url)
text = page.text
soup = bs(text, "html.parser")

base_url="https://www.grinnell.edu/user/"    
rows = soup.find_all("div", class_="views-row")
users = []



#for each member on the faculty page, collect their position and name, and then open their personal page.

for row in rows:
    name_tag = row.find("div", class_="user__name").find("a")
    position_tag = row.find("div", class_="user__position")
    if name_tag and 'href' in name_tag.attrs:
        faculty_id = name_tag["href"].split("/")[-1]
        profile_link = base_url + faculty_id
        name = " ".join(name_tag.text.split())
        name=name.replace(".","")
        
        
        # avoid whitespace in professor emeritus position. Yes, this looks redundant but it seems to be neccessary
        position=""
        for s in position_tag.stripped_strings:
            position+=" ".join(s.strip().split())
            
        
        faculty_response = requests.get(profile_link)        
        faculty_soup = bs(faculty_response.text, "html.parser")
        contact_info = faculty_soup.find("div", class_="user__contact-info")
        
        #collect relevant data from their personal page
        email_tag = contact_info.find("div", class_="user__email").find("a") if contact_info and contact_info.find("div", class_="user__email") else None
        phone_tag = contact_info.find("div", class_="user__phone").find("a") if contact_info and contact_info.find("div", class_="user__phone") else None
        cv_tag = contact_info.find("div", class_="user__cv").find("a") if contact_info and contact_info.find("div", class_="user__cv") else None
        address_tag = contact_info.find("p", class_="address") if contact_info else None
        
        
        
        email = email_tag.text.strip() if email_tag else ""
        phone = phone_tag.text.strip() if phone_tag else ""
        phone = phone.replace("(", "").replace(")", "")
        
        cv_link = cv_tag["href"] if cv_tag else ""
        if len(cv_link)>0:
            cv_link="https://www.grinnell.edu/"+cv_link
        address = " ".join(address_tag.stripped_strings).strip() if address_tag else ""
        
        #remove redundant info from address
        pattern = r"\s*(Grinnell(?:\s*College)?|,\s*IA\s*\d{5}(?:\s*United States)?)\b"
        
        cleaned_address = re.sub(pattern, "", address)
        
        
        users.append([name, position, cleaned_address, phone, email, cv_link])
        

with open("history_classes/data/personal_page.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["instructor", "title", "address", "phone", "email", "CV"])
    writer.writerows(users)
    
    

