# Chat-HMS

## Usage
- First set up a python virtual environment using:
    - `python -m venv venv`
- then switch to the creater virtual environment using:
    - `source venv/bin/activate`
- run the application using:
    - `gunicorn "app.main:createApp(testing=False)"`
- for running in debug mode:
    - `gunicorn --reload "app.main:createApp(testing=False)"`

Make sure to put a `.env` file inside `/app` which contains :
```
api_key=<Your openai API key without quotes>
FINE_TUNED_MODEL=<Name of the model (choose from modelsAvailable.txt) without quotes>
```
