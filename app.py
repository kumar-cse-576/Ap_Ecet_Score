from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

# Path to the file that stores submitted URLs
url_file = 'submitted_urls.txt'


# Function to load submitted URLs
def load_urls():
    try:
        with open(url_file, 'r') as file:
            urls = file.readlines()
            return [url.strip() for url in urls]
    except FileNotFoundError:
        return []


# Function to save a URL to the file
def save_url(url):
    with open(url_file, 'a') as file:
        file.write(url + '\n')


@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    submitted_urls = load_urls()  # Load previously submitted URLs

    if request.method == 'POST':
        url = request.form['url']
        save_url(url)  # Save the new URL

        try:
            # Making the request with a timeout to prevent hanging
            response = requests.get(url, timeout=5)
            # Using lxml parser for faster processing
            soup = BeautifulSoup(response.content, 'lxml')

            # Find all the question divs (optimized selector)
            questions = soup.find_all('div', class_='question-pnl')
            total = 0
            correct = 0

            # Loop through each question to check answers
            for q in questions:
                chosen_option = q.find('td', string='Chosen Option :')
                correct_img = q.find('td', class_='rightAns')

                if chosen_option and correct_img:
                    total += 1
                    chosen_value = chosen_option.find_next_sibling('td').text.strip()
                    correct_option_text = correct_img.get_text(strip=True)
                    correct_number = correct_option_text.split('.')[0].strip()

                    if correct_number == chosen_value:
                        correct += 1

            result = {
                'total': total,
                'correct': correct,
                'score': f"{correct} / {total}"
            }

        except Exception as e:
            # Handle errors in case of a failed request or parsing error
            result = {
                'total': 0,
                'correct': 0,
                'score': f"Error: {str(e)}"
            }

    return render_template('index.html', result=result, submitted_urls=submitted_urls)


if __name__ == '__main__':
    app.run(debug=True)
