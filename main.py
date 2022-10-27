import json
import os
import pikepdf
import requests
from datetime import datetime
from dotenv import load_dotenv

FILENAME = 'edt.pdf'
JSON_FILE = 'last.json'

def convert_obj_to_dt(obj) -> datetime:
    # convert to str and remove zone
    dt_str = str(obj).replace("'", '').split('+')[0]
    return datetime.strptime(dt_str, 'D:%Y%m%d%H%M%S')

def get_last_update_dt() -> datetime:
    with open(JSON_FILE, 'r+') as file:
        content = json.load(file)
        return datetime.strptime(content['last']['mod_date'], '%Y-%m-%d %H:%M:%S')

def insert_json(author: str, mod_date: str) -> None:
    dictionary = {
        'author': author,
        'mod_date': mod_date
    }
    with open(JSON_FILE, 'r+') as file:
        content = json.load(file)
        content['last'].update(dictionary)
        file.seek(0)
        json.dump(content, file, indent=4)

def send_telegram_msg(text: str) -> None:
    token = os.getenv('TOKEN')
    chat_id = os.getenv('CHAT_ID')
    telegram_url = f'https://api.telegram.org/bot{token}/sendMessage'

    payload = {
        'text': text,
        'chat_id': chat_id
    }
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json'
    }
    requests.post(telegram_url, json=payload, headers=headers)

def download_pdf(url: str) -> pikepdf.Pdf:
    response = requests.get(url, cookies={ 'MoodleSession': os.getenv('SESSION') })

    if response.status_code == 200:
        open(FILENAME, 'wb').write(response.content)
        return pikepdf.Pdf.open(FILENAME)

    return None

def main():
    url = os.getenv('URL')
    now_hour = datetime.now().time()
    
    try:
        if now_hour.hour == 6 and now_hour.minute == 0:
            send_telegram_msg("Hello, I'm ready to detect a new schedule")

        pdf = download_pdf(url)
               
        # get metadata
        info = pdf.docinfo

        # get modification date of current pdf
        curr_mod_dt = convert_obj_to_dt(info.ModDate)

        # get last modification date from json
        last_mod_dt = get_last_update_dt()

        if curr_mod_dt > last_mod_dt:
            insert_json(str(info.Author), str(curr_mod_dt)) 
            send_telegram_msg(f'{str(info.Author)} has updated the university schedule. {url}')

    except Exception as e:
        send_telegram_msg(f'@MiageScheduleBot encountered an error : {str(e)} !')

if __name__ == '__main__':
    load_dotenv()
    main()