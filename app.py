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

def extract_questions(soup):
    """Extract MCQs from the soup object."""
    mcqs = []
    fill_in_the_gaps = []
    underheads = soup.find_all('div', class_='Underhead')
    
    for underhead in underheads:
        context = underhead.find('p').text
        dl = underhead.find_next('dl')
        if dl:
            options = [dt.text for dt in dl.find_all('dt')]
            for dd in dl.find_all('dd'):
                question = f"{context}: {dd.text}"
                mcqs.append((question, options))
        else: 
            p = underhead.find_next(['p', 'ul'])
            terms = [term.text for term in p.find_all(['b', 'u'])]
            if terms:
                for term in terms:
                    question = p.text.replace(term, "___")
                    fill_in_the_gaps.append((question, term))
    
    return {"mcq": mcqs, "fing": fill_in_the_gaps}

quiz_title = extract_title(soup)

print(f"\"{quiz_title}\" Chapter Quiz\n")

questions = extract_questions(soup)

for question in questions["mcq"]:
    print(question[0])
    for index, choice in enumerate(question [1]):
        print(f"\t {index} {choice}")