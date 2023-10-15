from bs4 import BeautifulSoup
import requests, random, string, datetime, re

ascii_art_welcome = '''                                 _ _____  __   _ 
  __ _  ___ ___     ___ ___  ___(_)___ / / /_ / |
 / _` |/ __/ _ \\   / __/ __|/ __| | |_ \\| '_ \\| |
| (_| | (_|  __/  | (__\\__ \\ (__| |___) | (_) | |
 \\__,_|\\___\\___|___\\___|___/\\___|_|____/ \\___/|_|\n'''

print(ascii_art_welcome)

# Constants
NOTE_URLS = [
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
CHOICE_LABELS = string.ascii_lowercase  # 'abcdefghijklmnopqrstuvwxyz'


def get_user_input():
    while True:
        try:
            chapter_number = int(input(f"What chapter you want to be quizzed on? (1-{len(NOTE_URLS)}): "))
            if 1 <= chapter_number <= len(NOTE_URLS):
                return chapter_number
            else:
                print(f"Number is out of range. Please enter a number between 1 and {len(NOTE_URLS)}.")
        except ValueError:
            print(f"Invalid input. Please enter a number between 1 and {len(NOTE_URLS)}.")


def fetch_html_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
    return ""


def strip_choice_custom(choice):
    for prefix in ["What is the", "What are the", "What is", "What"]:
        if choice.startswith(prefix):
            choice = choice.replace(prefix, "").rstrip("?")
            break
    choice = re.sub(r'\(.*?\)', '', choice)  # Remove anything inside parentheses
    return choice.strip()


def extract_ul_questions(chunk, next_chunk):
    ul_questions = []
    ul_element = chunk.find_next('ul')
    
    if not ul_element or (next_chunk and next_chunk.find_previous('ul') == ul_element):
        return []

    # Extract the header from the preceding <p> element
    header = ul_element.find_previous('p').text.strip()
    
    for li in ul_element.find_all("li"):
        b_element = li.find("b")
        if b_element:
            surrounding_text = li.text.strip()
            answer = b_element.text.strip()
            question = surrounding_text.replace(answer, "___")
            
            # Combine the header with the question
            combined_question = f"{header} {question}"
            
            ul_questions.append({
                "type": "fill",
                "question": combined_question,
                "answer": answer
            })

    return ul_questions


def extract_fill_questions(chunk, next_chunk):
    fill_questions = []
    bold_elements = []

    for tag in chunk.find_all_next():
        # If we hit the next underhead, stop looking for bold tags
        if tag == next_chunk:
            break
        bold_elements.extend(tag.find_all("b"))
    for b_element in bold_elements:
        # Get the entire text surrounding the bold text
        surrounding_text = b_element.parent.text.strip()

        # Split the surrounding text into sentences
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', surrounding_text)

        # Find the specific sentence that contains the bold text (answer)
        for sentence in sentences:
            if b_element.text.strip() in sentence:
                sentence = re.sub(r'\(.*?\)', '', sentence)
                answer = b_element.text.strip()
                answer = re.sub(r'\(.*?\)', '', answer).strip()
                question = sentence.replace(answer, "___")
                # Check if fill in the gap question ends with ":"
                if not question.endswith(":"):
                    fill_questions.append({
                        "type": "fill",
                        "question": question,
                        "answer": answer
                    })
    
    return fill_questions


def extract_quiz_questions(soup):
    underheads = soup.select(".Underhead")
    quiz_questions = []

    for idx, chunk in enumerate(underheads):
        next_chunk = underheads[idx + 1] if idx + 1 < len(underheads) else None
        # next_underhead = chunk.find_next(class_='Underhead')
        dl_elements = chunk.find_next('dl')

        # if next_underhead and (not dl_elements or next_underhead.find_previous('dl') != dl_elements):
        #     dl_elements = None

        if dl_elements:
            for dd in dl_elements.find_all("dd"):
                choices = [strip_choice_custom(dt.text.strip()) for dt in dl_elements.find_all("dt")]
                question = dd.text.strip()
                correct_answer = strip_choice_custom(dd.find_previous_sibling("dt").text.strip())

                if len(choices) > 4:
                    correct_choice_index = choices.index(correct_answer)
                    del choices[correct_choice_index]
                    random_choices = random.sample(choices, 3)
                    random_choices.append(correct_answer)
                    choices = random_choices

                random.shuffle(choices)

                quiz_questions.append({
                    "type": "mcq",
                    "question": question,
                    "choices": choices,
                    "correct_answer": correct_answer
                })
        else: 
            # TODO: Fix bullet point questions
            # ul_questions = extract_ul_questions(chunk, next_chunk)
            # quiz_questions.extend(ul_questions)
            fill_questions = extract_fill_questions(chunk, next_chunk)
            quiz_questions.extend(fill_questions)

    return quiz_questions


def question_wizard(quiz_questions, score, user_answers):
    for idx, q in enumerate(quiz_questions, 1):
        if q["type"] == "mcq":
            print(f"{idx}. Choose the most suitable/close term for this definition:\n\n{q['question']}\n")
            current_choices = CHOICE_LABELS[:len(q['choices'])]
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
            print(f'{idx}. Fill in the gap:\n\n{q["question"]}\n')
            user_answer = input("Your answer: ").strip()
            user_answers.append(user_answer)
            if user_answer.lower() == q["answer"].lower():
                score += 1
            print("\n")
    return score


def administer_quiz(quiz_questions, chapter_number, soup):
    title = soup.find('div', class_='SimpleTitle').find_all('p')[1].text
    ref = soup.find("div", class_="Content").find_next('p').text
    url = NOTE_URLS[chapter_number - 1]

    print()
    print(f"\"{title}\" Chapter Quiz")
    print(ref)
    print(f"# of questions: {len(quiz_questions)}")
    print(f"Study here: {url}")
    print()

    user_answers = []
    score = 0

    score = question_wizard(quiz_questions, score, user_answers)

    percentage = (score / len(quiz_questions)) * 100
    print(f"Your Score: {score}/{len(quiz_questions)}")
    print(f"Percentage: {percentage:.2f}%")

    timestamp = datetime.datetime.now().strftime("%d.%m.%Y-%H:%M")
    filename = f"Ch{chapter_number}-{timestamp}.txt"

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


def main():
    chapter_number = get_user_input()
    html_content = fetch_html_content(NOTE_URLS[chapter_number - 1])
    soup = BeautifulSoup(html_content, 'html.parser')
    quiz_questions = extract_quiz_questions(soup)
    # random.shuffle(quiz_questions)
    administer_quiz(quiz_questions, chapter_number, soup)


# Execute the main function
main()
