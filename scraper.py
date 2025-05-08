from bs4 import BeautifulSoup
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        url = request.form['url']
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.content, 'lxml')  # use lxml parser (faster)

            questions = soup.find_all('div', class_='question-pnl')
            total = 0
            correct = 0

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
            result = {
                'total': 0,
                'correct': 0,
                'score': f"Error: {str(e)}"
            }

    return render_template('index.html', result=result)
