from bs4 import BeautifulSoup
import requests

# Given HTML content
html_content = ""

url = 'https://cs.ccsu.edu/~stan/classes/CS410/Notes16/01-WhatIsSE.html'
response = requests.get(url)

# Ensure the request was successful
if response.status_code == 200:
    html_content = response.text
    # print(html_content)
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

# Parsing the HTML using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Extracting the title of the quiz
def extract_title(soup):
    title_div = soup.find('div', class_='SimpleTitle')
    title = title_div.find_all('p')[1].text
    return title

from bs4 import BeautifulSoup
import requests

# Fetching the HTML content
url = 'https://cs.ccsu.edu/~stan/classes/CS410/Notes16/01-WhatIsSE.html'
response = requests.get(url)
html_content = response.text if response.status_code == 200 else ""

# Parsing the HTML using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

def extract_title(soup):
    title_div = soup.find('div', class_='SimpleTitle')
    title = title_div.find_all('p')[1].text
    return title

def extract_questions(soup):
    """Extract MCQs and fill in the gaps questions from the soup object."""
    mcqs = []
    fill_in_the_gaps = []
    underheads = soup.find_all('div', class_='Underhead')
    
    for i, underhead in enumerate(underheads):
        context = underhead.find('p').text
        dl = underhead.find_next('dl')
        
        if dl:  # If MCQs are present
            options = [dt.text for dt in dl.find_all('dt')]
            for dd in dl.find_all('dd'):
                question = f"{context}: {dd.text}"
                mcqs.append((question, options))
        else:  # If fill in the gaps questions are present
            # Find all subsequent siblings until the next Underhead or end of document
            for sibling in underhead.find_next_siblings():
                if sibling.name and "Underhead" in sibling.get('class', []):  # Stop if next Underhead is found
                    break
                terms = [term.text for term in sibling.find_all(['b', 'u'])]
                if terms:
                    for term in terms:
                        question = sibling.text.replace(term, "___")
                        fill_in_the_gaps.append((question, term))
    
    return {"mcq": mcqs, "fing": fill_in_the_gaps}

# Extract questions using updated logic
questions = extract_questions(soup)

print(questions["fing"] ) # Displaying the fill in the gaps questions for demonstration


quiz_title = extract_title(soup)

print(f"\"{quiz_title}\" Chapter Quiz\n")

questions = extract_questions(soup)

for question in questions["mcq"]:
    print(question[0])
    for index, choice in enumerate(question [1]):
        print(f"\t {index} {choice}")