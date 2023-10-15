from bs4 import BeautifulSoup
import requests
import random
import string
import datetime

# Given HTML content
html_content = ""

note_urls = [
    'https://cs.ccsu.edu/~stan/classes/CS410/Notes16/01-WhatIsSE.html',
    'https://cs.ccsu.edu/~stan/classes/CS410/Notes16/02-SoftwareProcesses.html',
    'https://cs.ccsu.edu/~stan/classes/CS410/Notes16/03-Agile.html',
    'https://cs.ccsu.edu/~stan/classes/CS410/notes16/04-Requirements.html',
    'https://cs.ccsu.edu/~stan/classes/CS410/Notes16/05-SystemModeling.html',
    'https://cs.ccsu.edu/~stan/classes/CS410/Notes16/06-ArchitecturalDesign.html',
    'https://cs.ccsu.edu/~stan/classes/CS410/Notes16/07-DesignAndImplementation.html',
    'https://cs.ccsu.edu/~stan/classes/CS410/Notes16/08-SoftwareTesting.html',
    'https://cs.ccsu.edu/~stan/classes/CS410/Notes16/09-SoftwareEvolution.html',
    'https://cs.ccsu.edu/~stan/classes/CS410/Notes16/10-SystemDependability.html',
    'https://cs.ccsu.edu/~stan/classes/CS410/Notes16/11-ReliabilityEngineering.html',
    'https://cs.ccsu.edu/~stan/classes/CS410/Notes16/12-SafetyEngineering.html',
]

# Prompt user for input
while True:
    try:
        chapter_number_input = int(input("What chapter you want to be quizzed on? (1-12): "))
        if 1 <= chapter_number_input <= 12:
            break
        else:
            print("Number is out of range. Please enter a number between 1 and 12.")
    except ValueError:
        print("Invalid input. Please enter a number between 1 and 12.")

# Get the URL based on user input
url = note_urls[chapter_number_input - 1]

# Get the HTML Content
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
    
    # Check if the next .Underhead comes before the next <dl>
    next_underhead = chunk.find_next(class_='Underhead')
    dl_elements = chunk.find_next('dl')

    # If next Underhead is found before next DL, set dl_elements to None
    if next_underhead and (not dl_elements or next_underhead.find_previous('dl') != dl_elements):
        dl_elements = None
    
    if dl_elements:
        # MCQ extraction logic remains unchanged
        for dd in dl_elements.find_all("dd"):
            choices = [strip_choice_custom(dt.text.strip()) for dt in dl_elements.find_all("dt")]
            question = dd.text.strip()
            correct_answer = dd.find_previous_sibling("dt").text.strip()
            correct_answer = strip_choice_custom(correct_answer)

            if len(choices) > 4:
                correct_choice_index = choices.index(correct_answer)
                
                choices = choices

                # Remove the correct choice temporarily
                del choices[correct_choice_index]
                
                # Randomly select 3 other choices
                random_choices = random.sample(choices, 3)
                
                # Add back the correct choice
                random_choices.append(correct_answer)
                
                # Shuffle the 4 choices
                random.shuffle(random_choices)
                
                choices = random_choices

            quiz_questions.append({
                "type": "mcq",
                "question": question,
                "choices": choices,
                "correct_answer": correct_answer
            })
    else:
        bold_elements = []
        for tag in chunk.find_all_next():
            # If we hit the next underhead, stop looking for bold tags
            if tag == next_chunk:
                break
            bold_elements.extend(tag.find_all("b"))
        

        for b_element in bold_elements:
            parent = b_element.parent

            if parent:
                sentence = parent.text.strip()
                answer = b_element.text.strip()
                question = sentence.replace(answer, "___")
                quiz_questions.append({
                    "type": "fill",
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
        if q["type"] == "mcq":
            print(f"{idx}. {q['question']}")
            for choice_idx, choice in enumerate(q['choices'], 1):
                prefix = '*' if choice == q['correct_answer'] else ''
                print(f"   {choice_idx}. {prefix}{choice}")
            print("\n")

        if q["type"] == "fill":
            print(f'{idx}. {q["question"]}')
            print(f'Answer: {q["answer"]}')
            print("\n")

# random.shuffle(quiz_questions)

def administer_quiz(quiz_questions, chapter_number):
    title = extract_title(soup)
    ref = extract_ref(soup)


    print(f"\"{title}\" Chapter Quiz")
    print(ref)
    print(f"# of questions: {len(quiz_questions)}")
    print(f"Study here: {url}")
    print()

    # Variables to keep track of user's answers and score
    user_answers = []
    score = 0

    choice_labels = string.ascii_lowercase  # Gets 'abcdefghijklmnopqrstuvwxyz'
    
    for idx, q in enumerate(quiz_questions, 1):
        if q["type"] == "mcq":
            print(f"{idx}. Choose the most suitable answer for this definition:\n{q['question']}")
            current_choices = choice_labels[:len(q['choices'])]
            for choice_idx, choice in enumerate(q['choices']):
                print(f"   {current_choices[choice_idx]}. {choice}")
            while True:
                user_choice = input(f"Your answer ({'/'.join(current_choices)}): ").lower()
                if user_choice in current_choices:
                    user_answers.append(user_choice)
                    if q['choices'][current_choices.index(user_choice)] == q['correct_answer']:
                        score += 1
                    break
                else:
                    print(f"Invalid input. Please enter a valid choice ({'/'.join(current_choices)}).")
            print("\n")

        if q["type"] == "fill":
            print(f'{idx}. Fill in the gap:\n{q["question"]}')
            user_answer = input("Your answer: ").strip()
            user_answers.append(user_answer)
            if user_answer.lower() == q["answer"].lower():
                score += 1
            print("\n")

    percentage = (score/len(quiz_questions)) * 100
    print(f"Your Score: {score}/{len(quiz_questions)}")
    print(f"Percentage: {percentage:.2f}%")

    # After collecting all answers and calculating the score, save to a file
    timestamp = datetime.datetime.now().strftime("%d.%m.%Y-%H:%M")
    filename = f"Ch{chapter_number}-{timestamp}.txt"

    # Save results to final.txt
    with open(filename, "w") as f:
        f.write(f"Your Score: {score}/{len(quiz_questions)}\n")
        f.write(f"Percentage: {percentage:.2f}%\n\n")
        for idx, q in enumerate(quiz_questions, 1):
            f.write(f"{idx}. {q['question']}\n")
            if q["type"] == "mcq":
                correct_choice = 'abcd'[q['choices'].index(q['correct_answer'])]
                f.write(f"Your Answer: {user_answers[idx-1]}\nCorrect Answer: {correct_choice}\n\n")
            else:
                f.write(f"Your Answer: {user_answers[idx-1]}\nCorrect Answer: {q['answer']}\n\n")
    
    print(f"Results saved to {filename}")

administer_quiz(quiz_questions, chapter_number_input)
