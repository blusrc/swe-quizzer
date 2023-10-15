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

def extract_ref(soup):
    ref_div = soup.find("div", class_="Content")
    title = ref_div.find_next('p').text
    return title

underheads = soup.select(".Underhead")

quiz_questions = []

def strip_choice_custom(choice):
    if choice.startswith("What is the"):
        choice = choice.replace("What is the", "").rstrip("?")
    elif choice.startswith("What are the"):
        choice = choice.replace("What are the", "").rstrip("?")
    elif choice.startswith("What is"):
        choice = choice.replace("What is", "").rstrip("?")
    elif choice.startswith("What"):
        choice = choice.replace("What", "").rstrip("?")
    
    return choice.strip()

for idx, chunk in enumerate(underheads):
    next_chunk = underheads[idx + 1] if idx + 1 < len(underheads) else None

    dl_elements = chunk.find_next("dl")
    if dl_elements:
        print("found mcq")
        choices = [strip_choice_custom(dt.text.strip()) for dt in dl_elements.find_all("dt")]
        for dd in dl_elements.find_all("dd"):
            question = dd.text.strip()

            correct_answer = dd.find_previous_sibling("dt").text.strip()
            correct_answer = strip_choice_custom(correct_answer)

            quiz_questions.append({
                "type": "mcq",
                "question": question,
                "choices": choices,
                "correct_answer": correct_answer
            })
    else:
        print("found fill")
        # Fill-in-the-gaps extraction
        paragraphs = chunk.find_all_next("p", limit=5)  # Let's limit to 5 for safety, adjust if necessary
        for para in paragraphs:
            if not para.find("dl"):  # We don't want to process DL elements within these paragraphs
                b_elements = para.find_all("b")
                for b_element in b_elements:
                    sentence = b_element.find_parent().text.strip()
                    answer = b_element.text.strip()
                    question = sentence.replace(answer, "___")
                    quiz_questions.append({
                        "type": "fill-in-the-gap",
                        "question": question,
                        "answer": answer
                    })

def pretty_print_quiz(quiz_questions):
    title = extract_title(soup)
    ref = extract_ref(soup)

    print(f"\"{title}\" Chapter Quiz")
    print(ref)
    print()
    for idx, q in enumerate(quiz_questions, 1):
        # if q["type"] == "mcq":
        #     print(f"{idx}. {q['question']}")
        #     for choice_idx, choice in enumerate(q['choices'], 1):
        #         prefix = '*' if choice == q['correct_answer'] else ''
        #         print(f"   {choice_idx}. {prefix}{choice}")
        #     print("\n")

        if q["type"] == "fill":
            print(f'{idx} {q["question"]}')
            print(f'Answer: {q["answer"]}')
            print('-' * 50)

pretty_print_quiz(quiz_questions)
