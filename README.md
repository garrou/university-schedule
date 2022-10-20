# university-schedule

Script to be notified when the university's schedule has changed.

## Requirements 

```sh
pip install -r requirements.txt
```

File to keep the last update : **last.json**

```json
{
    "last": {}
}
```

**.env** file with :
- SESSION (moodle session)
- URL (pdf url)
- TOKEN (telegram token)
- CHAT_ID (telegram chat id)