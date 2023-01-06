# Chat-HMS
First set up a python virtual environment using:
`python -m venv venv`
then switch to the creater virtual environment using:
`source venv/bin/activate`
run the application using:
`gunicorn "app.main:createApp(testing=False)"`
for running in debug mode:
`gunicorn --reload "app.main:createApp(testing=False)"`