import json
import os
import pikepdf
import requests
from datetime import datetime
from dotenv import load_dotenv

FILENAME = 'edt.pdf'
JSON_FILE = 'last.json'

def convert_obj_to_datetime(obj):
    # convert to str and remove +0200
    dt_str = str(obj).replace("'", "").split('+')[0]
    # convert pikepdf date to datetime
    return datetime.strptime(dt_str, 'D:%Y%m%d%H%M%S')

def get_last_update_dt():
    with open(JSON_FILE, "r+") as file:
        content = json.load(file)
        return datetime.strptime(content['last']['mod_date'], '%Y-%m-%d %H:%M:%S')

def insert_json(info):
    dictionary = {
        'author': str(info.Author),
        'mod_date': str(convert_obj_to_datetime(info.ModDate))
    }
    with open(JSON_FILE, "r+") as file:
        content = json.load(file)
        content['last'].update(dictionary)
        file.seek(0)
        json.dump(content, file, indent=4)

def main():
    session = os.getenv('SESSION')
    url = os.getenv('URL')
    cookies = {'MoodleSession': session}
    response = requests.get(URL, cookies=cookies)
    open(FILENAME, 'wb').write(response.content)
    
    try:
        pdf = pikepdf.Pdf.open(FILENAME)
        info = pdf.docinfo
        curr_mod_dt = convert_obj_to_datetime(info.ModDate)
        last_mod_dt = get_last_update_dt()

        if curr_mod_dt > last_mod_dt:
            insert_json(info) 
            print('Diff')

    except Exception as e:
        print(e)

if __name__ == '__main__':
    load_dotenv()
    main()