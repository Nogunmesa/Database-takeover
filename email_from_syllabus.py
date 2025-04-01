from bs4 import BeautifulSoup
import requests
from pypdf import PdfReader
from io import BytesIO
import re
#if we have multiple emails, run this to find the email most similar to the instructor. 
def common_prefix_length(instr, email):
    if not instr or not email:
        return 0
    
    min_length = min(len(instr), len(email))
    #print(instr+", "+email)
    count = 0
    for i in range(min_length):
        if instr[i] == email[i]:
            count += 1
        else:
            break
    
    return count
# processes the emails found, selects the one most similar to the instructor name to return
def select_output(emails,instructor,url):
    email_list=[]
    if (len(emails)>1):
        print("more than one email: " +str(emails)+" at "+str(url))  
        
        email_list.extend(emails)
        pattern = r'(.+?)@'
        shared_len=0
        
        for e in email_list:
            match = re.search(pattern, e)
            #print(e)
            if match:
                
                new_shared_len=common_prefix_length(instructor.lower(),match.group(1).lower())
                if shared_len<new_shared_len:
                    output_email=e
                    
                    shared_len=new_shared_len   
        print("selected: " + str(output_email))   
        
    elif not emails:
        print("no emails found")
        print("email read")
        print("")
        return ""
    else:      
        output_email=emails.pop()
    print("email read")
    print("")
    return output_email.lower()


def find_email(url, instructor):

    response = requests.get(url)
    url = response.url
    email_list=[]
    shared_len=0
    
    if url.endswith("pdf"):
        if response.status_code == 200:
            print("Pdf")
            # Read the PDF from the downloaded content
            reader = PdfReader(BytesIO(response.content))
            
            first_page = reader.pages[0]
            text = first_page.extract_text()
            text = text.split("\n")
            second_page = reader.pages[1]
            text = text + second_page.extract_text().split("\n")
                        
            email_pattern = r"[a-zA-Z0-9._%+-]+@grinnell\.edu"
            emails = re.findall(email_pattern, "".join(text))
            return select_output(emails,instructor,url)
                
        else:
            print("Failed to download PDF.")

    else:
        if url.endswith("html")!=True: # seems to always be either pdf or html document 
            print("Warning: the url does not end with pdf/html: "+url)
        print("html")
        soup = BeautifulSoup(response.text, 'html.parser')
    
        email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@grinnell\.edu")
        emails = set(re.findall(email_pattern, soup.get_text()))
        
        return select_output(emails,instructor,url)
    

    