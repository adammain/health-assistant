# Health Assistant

## Synopsis

Track key daily health metrics while building a personalized health database.  Timer for tracking how much time is spent eating healthy or unhealthy meals, working out, or sleeping as well details about each activity.  Also, measurements for weight, blood pressure, and blood sugar levels.

## Motivation

When sufficient personal health data has been gathered, a (yet to be built) deep learning network will analayze the fed data and output a personalized predictive health analysis.

## Installation

*** TESTED WITH PYTHON 3

```
$ git clone git@github.com:amtruenorth/health-assistant.git

$ cd health-assistant/
```

## Usage
Install required packages:
```
$ pip install -r requirements.txt
```

To create a database:
```
$ python3 models.py
```

Start redis-server (https://redis.io/topics/quickstart):
```
$ redis-server
```

In a different terminal tab, start python web server:
```
$ npm start
```

In a different terminal tab, start application (tested with Python 3):
```
$ python3 app.py
```
* Navigate to: http://localhost:5000

## API Reference

READ all user activities (meals, sleep records, workouts):
```
# GET request to
/activities?user_id=<Your user id>
```
* Returns a JSON object containing the response data of the POST request

READ specific user meal record:
```
# GET request to
/activities/<your_user_id>/meal/<meal_id>
```
* Returns a JSON object containing the response data of the POST request

CREATE new Meal record:
```
# POST to:
/activities?type=meal&user_id=1&description=Snickers&duration=0:30&healthy=False&unhealthy=True&starch_rich=False&sucrose_rich=True
```

UPDATE Meal record:
```
# PUT to:
/activities/<your_user_id>/meal/<meal_id>/?healthy=False&description=Snickers+candy+bar
```

DELETE Meal record:
```
# DELETE to:
/activities/<your_user_id>/meal/<meal_id>
```

## Tests

Test API:
```
$ python3 api_tester.py
```

## What You're Getting
```bash
├── README.md - This file.
├── requirements.txt # pip package manager file. It's unlikely that you'll need to modify this.
├── templates
│   ├── All html view templates
└── flask_socketio # Socketio library for flask. Real time updates. (https://github.com/miguelgrinberg/Flask-SocketIO)
└── src # flask_util library folder (https://github.com/dantezhu/flask_util_js)
└── static
    ├── styles.css # Styles for app.
    ├── datetime.js # Controls timer and ui functionality
    ├── editActivityModal.js # Controls Bootstrap modal content
    ├── BookShelf.js # BookShelf for displaying books.
    ├── favicon.ico # favicon
    ├── favicon.png # favicon
    ├── ha-logo.png # logo (not used)
├── api.py # Standalone API server (not used)
├── api_tester.py # Tests API functionality.
├── app.py # Primary app server.
├── forms.py # All of the apps forms.
├── helpers.py # Helper functions for forms.
├── models.py # DB Database setup
├── stopwatch.py # Stopwatch helper functions (https://www.safaribooksonline.com/library/view/python-cookbook-3rd/9781449357337/ch13s13.html)
```

## License

MIT © Adam Main
