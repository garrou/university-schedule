import json
import os
import pikepdf
import requests
from datetime import datetime
from dotenv import load_dotenv

FILENAME = 'edt.pdf'
JSON_FILE = 'last.json'

def convert_obj_to_datetime(obj) -> datetime:
    # convert to str and remove +0200
    dt_str = str(obj).replace("'", '').split('+')[0]
    # convert pikepdf date to datetime
    return datetime.strptime(dt_str, 'D:%Y%m%d%H%M%S')

def get_last_update_dt() -> datetime:
    with open(JSON_FILE, 'r+') as file:
        content = json.load(file)
        return datetime.strptime(content['last']['mod_date'], '%Y-%m-%d %H:%M:%S')

def insert_json(info) -> None:
    dictionary = {
        'author': str(info.Author),
        'mod_date': str(convert_obj_to_datetime(info.ModDate))
    }
    with open(JSON_FILE, 'r+') as file:
        content = json.load(file)
        content['last'].update(dictionary)
        file.seek(0)
        json.dump(content, file, indent=4)

def send_telegram_msg(info, schedule_url: str, mod_dt: datetime) -> None:
    token = os.getenv('TOKEN')
    chat_id = os.getenv('CHAT_ID')
    telegram_url = f'https://api.telegram.org/bot{token}/sendMessage'

    payload = {
        'text': f'{str(info.Author)} has updated the university schedule at {mod_dt}. {schedule_url}',
        'chat_id': chat_id
    }
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json'
    }
    requests.post(telegram_url, json=payload, headers=headers)

def main():
    session = os.getenv('SESSION')
    url = os.getenv('URL')
    cookies = {'MoodleSession': session}
    response = requests.get(url, cookies=cookies)
    open(FILENAME, 'wb').write(response.content)
    
    try:
        pdf = pikepdf.Pdf.open(FILENAME)
        info = pdf.docinfo
        curr_mod_dt = convert_obj_to_datetime(info.ModDate)
        last_mod_dt = get_last_update_dt()

        if curr_mod_dt > last_mod_dt:
            insert_json(info) 
            send_telegram_msg(info, url, curr_mod_dt)

    except Exception as e:
        print(e)

if __name__ == '__main__':
    load_dotenv()
    main()