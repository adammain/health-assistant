from flask import Flask, Response, render_template, request, redirect, jsonify, \
    Markup, url_for, flash, session
from sqlalchemy import Date, create_engine, asc, desc, func, cast
from sqlalchemy.orm import sessionmaker
from flask_session import Session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import datetime
import time
from threading import Lock
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from flask_moment import Moment
from flask_util_js import FlaskUtilJs
from stopwatch import Timer
from models import Base, User, Meal, Sleep, \
    Workout, Weight, BloodPressure, BloodSugar, HeartRate
from forms import MealForm, SleepForm, WorkoutForm, WeightForm, \
    BloodPressureForm, BloodSugarForm, HeartRateForm
import helpers

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.secret_key = 'tRSKKNtG0%%q'

# JS flask url_for utility
fujs = FlaskUtilJs(app)

# socketio setup
socketio = SocketIO(app)
thread = None
thread_lock = Lock()

# global timers/date initialization
timerKey = 0
timers = {}
test_timer = Timer()
moment = Moment(app)

# save sessions on server with flask_sessions ext.
SESSION_TYPE = 'redis'
app.config.from_object(__name__)
Session(app)

# oauth2 config
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Health Assistant"

# Connect to Database and create database session
engine = create_engine('sqlite:///healthdata.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

# Create anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    session['state'] = state
    # return "The current session state is %s" % session['state']
    # return "Login session state: %s" % session['state']
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != session.get('state'):
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print("access token received %s " % access_token)

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print("url sent for API access:%s"% url)
    # print("API JSON result: %s" % result)
    data = json.loads(result)
    session['provider'] = 'facebook'
    session['username'] = data["name"]
    session['email'] = data["email"]
    session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(session.get('email'))
    if not user_id:
        user_id = createUser(session)
    session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += session.get('username')

    output += '!</h1>'
    output += '<img src="'
    output += session.get('picture')
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % session.get('username'))
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = session.get('facebook_id')
    # The access token must me included to successfully logout
    access_token = session.get('access_token')
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != session.get('state'):
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = session.get('access_token')
    stored_gplus_id = session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    session['access_token'] = credentials.access_token
    session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    session['username'] = data['name']
    session['picture'] = data['picture']
    session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(session)
    session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += session.get('username')
    output += '!</h1>'
    output += '<img src="'
    output += session.get('picture')
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % session.get('username'))
    print("done!")
    return output


# User Helper Functions
def createUser(session):
    newUser = User(name=session.get('username'), email=session.get(
                   'email'), picture=session.get('picture'))
    db_session.add(newUser)
    db_session.commit()
    user = db_session.query(User).filter_by(email=session.get('email')).one()
    return user.id


def getUserInfo(user_id):
    user = db_session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = db_session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del session['access_token']
        del session['gplus_id']
        del session['username']
        del session['email']
        del session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


def chop_microseconds(delta):
    return delta - datetime.timedelta(microseconds=delta.microseconds)


@app.route('/')
@app.route('/home/')
def showHome():
    days = {0: "M", 1: "T", 2: "W", 3: "Th", 4: "F", 5: "S", 6: "Su"}
    now = datetime.datetime.now()
    year, month, day = now.year, now.month, now.day

    if 'year' in request.args:
        year = int(request.args['year'])
        month = int(request.args['month'])
        day = int(request.args['day'])

    display_date = datetime.date(year, month, day)
    current_date = datetime.date(now.year, now.month, now.day)

    if 'username' not in session:
        return render_template('publicLanding.html')
    else:
        user_id = session['user_id']

        # TODO: Add join query for all activities/measurement tables

        # meals = db_session.query(Meal).filter(
        #     Meal.user_id).order_by(Meal.created.desc()).all()
        # activities = (db_session.query(User, Meal, Sleep, Workout)
        #               .join(Meal)
        #               .join(Sleep)
        #               .join(Workout)
        #               .filter(User.id == user_id)
        #               ).all()

        meals = db_session.query(Meal).filter(
            func.DATE(Meal.created) == display_date).all()

        for meal in meals:
            meal.duration = chop_microseconds(meal.duration)

        # return "This page will show all my activities and measurements"
        return render_template('home.html',
                               meals=meals,
                               days=days,
                               display_date=display_date,
                               display_year=display_date.year,
                               display_month=display_date.month,
                               display_day=display_date.day,
                               current_date=current_date,
                               current_year=now.year,
                               current_month=now.month,
                               current_day=now.day)


# TODO: Add new entry (measurement/activity)
@app.route('/new-entry/', methods=('GET', 'POST'))
@app.route('/new-entry/<int:year>/<int:month>/<int:day>', methods=('GET', 'POST'))
def newEntry(year=datetime.datetime.now().year, month=datetime.datetime.now().month, day=datetime.datetime.now().day):
    if 'username' not in session:
        return redirect('/login')

    date = datetime.date(year, month, day)
    entry_name = None
    user_id = session.get('user_id')

    # Request for passing displayed date to form for default value
    # with app.test_request_context(method='POST'):
    meal_form = MealForm(request.form, date=date)
    sleep_form = SleepForm()
    workout_form = WorkoutForm()
    weight_form = WeightForm()
    bloodpressure_form = BloodPressureForm()
    bloodsugar_form = BloodSugarForm()
    heartrate_form = HeartRateForm()

    if meal_form.submit_meal.data and meal_form.validate_on_submit():
        print("MEAL HELPER CALLED")
        helpers.NewEntry.meal(meal_form)
        table, entry_name = Meal, "Meal"

    if workout_form.submit_workout.data and workout_form.validate_on_submit():
        print("WORKOUT HELPER CALLED")
        helpers.NewEntry.workout(workout_form)
        table, entry_name = Workout, "Workout"

    if sleep_form.submit_sleep.data and sleep_form.validate_on_submit():
        print("SLEEP HELPER CALLED")
        helpers.NewEntry.sleep(sleep_form)
        table, entry_name = Sleep, "Sleep"

    if weight_form.submit_weight.data and weight_form.validate_on_submit():
        print("WEIGHT HELPER CALLED")
        helpers.NewEntry.weight(weight_form)
        table, entry_name = Weight, "Weight"

    if bloodpressure_form.submit_bloodpressure.data and bloodpressure_form.validate_on_submit():
        helpers.NewEntry.bloodPressure(bloodpressure_form)
        table, entry_name = BloodPressure, "Blood Pressure"

    if bloodsugar_form.submit_bloodsugar.data and bloodsugar_form.validate_on_submit():
        helpers.NewEntry.bloodSugar(bloodsugar_form)
        table, entry_name = BloodSugar, "Blood Sugar"

    if heartrate_form.submit_heartrate.data and heartrate_form.validate_on_submit():
        helpers.NewEntry.heartRate(heartrate_form)
        table, entry_name = HeartRate, "Heart Rate"

    if entry_name is not None:
        flash('New %s entry added successfully' % entry_name)
        db_session.commit()
        # TODO: Add redirect to display date as year/month/day
        return redirect(url_for('showHome', year=year, month=month, day=day))

    # return "This page will show all my activities"
    return render_template('newEntry.html',
                           meal_form=meal_form,
                           sleep_form=sleep_form,
                           workout_form=workout_form,
                           weight_form=weight_form,
                           bloodpressure_form=bloodpressure_form,
                           bloodsugar_form=bloodsugar_form,
                           heartrate_form=heartrate_form)


# START of SocketIO implimentation
# Timer thread
def background_thread(session):
    """Send server generated events to client."""
    print("BG THREAD FIRED!")
    # Save timer to db on stop.
    # db.session.remove() <-- clear sessions like this?
    # https://github.com/miguelgrinberg/Flask-SocketIO/issues/410

    thread_live = True
    timer = None
    while thread_live:
        # if active_timer is not None:
        socketio.sleep(0.1)
        if session['active_timer'] is not None:
            timer = timers[session['active_timer']]
            print("active_timer: " + str(session['active_timer']))
            print("Timer Object: {}".format(
                timers[session['active_timer']].runningElapsed))

        timer_btn_text = ''
        if timer and timer.running:
            seconds = timer.runningElapsed
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            time = "%d:%02d:%02d" % (h, m, s)
            print(time)
            socketio.emit('timer_response',
                          {'data': 'Server generated event',
                              'count': time, 'active_timer': session['active_timer']},
                          namespace='/timer')
        else:
            thread_live = False
            global thread
            with thread_lock:
                thread = None


@socketio.on('activate_timer', namespace='/timer')
def activate(message):
    # create room for this activities timer
    join_room(message['room'])

    # save active timer info to current session
    session['active_timer'] = message['room']
    print("CURRENT ACTIVE TIMER: {}".format(session['active_timer']))
    # get activities current saved time from DB
    meal = db_session.query(Meal).filter(
        Meal.id == session['active_timer']).one()
    start_with_time = meal.duration.total_seconds()
    print("START WITH TIME: {}".format(start_with_time))
    # start timer for activity
    print("Starting Timer...")
    global timerKey
    timerKey = message['room']
    global timers
    timers = {timerKey: Timer()}
    timers[timerKey].start(start_with_time)

    print("Timer STARTED")
    print("activated TIMER: " + str(session['active_timer']))

    # start background websocket thread for active timer
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(
                background_thread, session._get_current_object())

    # send response for log update
    emit('my_response',
         {'data': 'Start Timer In room: ' + ', '.join(rooms()),
          'active_timer': session['active_timer']})


@socketio.on('deactivate_timer', namespace='/timer')
def deactivate(message):
    timerID = message['room']
    timer = timers[timerID]
    if timer.running:
        print("Stopping Timer...")
        timer.stop()
        print("Timer STOPPED")
    leave_room(message['room'])
    meal = db_session.query(Meal).filter(
        Meal.id == message['room']).one()
    elapsed_time = datetime.timedelta(seconds=timer.elapsed)
    print("Duration Before: " + str(meal.duration))
    print("Change To: " + str(elapsed_time))
    meal.duration = elapsed_time
    db_session.add(meal)
    db_session.commit()
    meal = db_session.query(Meal).filter(
        Meal.id == timerID).one()
    print("Duration After: " + str(meal.duration))
    global thread
    with thread_lock:
        thread = None
    emit('my_response',
         {'data': 'Stopped Timer In room: ' + ', '.join(rooms()),
          'active_timer': session['active_timer']})
    session['active_timer'] = None


# Background thread initiation example:
@socketio.on('connect', namespace='/timer')
def test_connect():

    # Have to get session object this way to pass to socketio bg thread
    sessionObject = session._get_current_object()

    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(
                background_thread, session._get_current_object())

    if 'active_timer' not in sessionObject:
        session['active_timer'] = None

    print("SessionTimerID: " + str(sessionObject['active_timer']))
    emit('connect_response', {'data': 'Connected',
                              'active_timer': sessionObject['active_timer']})


@socketio.on('disconnect', namespace='/timer')
def test_disconnect():
    print('Client disconnected', request.sid)


# End of SocketIO test implimentation


# TODO: Show all activities sortable by date
@app.route('/activities/')
def showActivities():
    # sleep_activities = db_session.query(Sleep).filter_by(
    #     user_id=user_id).all()

    # workout_activities = db_session.query(Workout).filter_by(
    #     user_id=user_id).all()
    print(activities)
    # return "This page will show all my activities"
    return render_template('activities.html', activities=activities)


# TODO: Show all measurements sortable by date
@app.route('/measurements/')
def showMeasurements():
    # weight_measurements = db_session.query(Weight).filter_by(
    #     user_id=user_id).all()

    # bp_measurements = db_session.query(BloodPressure).filter_by(
    #     user_id=user_id).all()
    print(measurements)
    # return "This page will show all my restaurants"
    return render_template('measurements.html', measurements=measurements)


# TODO: Edit activity

# TODO: Add new measurement

# TODO: Edit measurement


# API routes
# TODO: All users all data
@app.route('/api/activities/<int:user_id>/JSON')
def allDataJSON(user_id):
    date = date
    activity = db_session.query(Activity).filter_by(id=user_id).one()
    sleep = db_session.query(Sleep).filter_by(
        user_id=user_id).order_by(sleep.activity.time_created)
    return jsonify(MenuItems=[i.serialize for i in items])


# TODO: All invividual users data
@app.route('/api/activities/<int:user_id>/JSON')
def userDataJSON(user_id):
    date = date
    activity = db_session.query(Activity).filter_by(id=user_id).one()
    sleep = db_session.query(Sleep).filter_by(
        user_id=user_id).order_by(sleep.activity.time_created)
    return jsonify(MenuItems=[i.serialize for i in items])


# TODO: All invividual user activities by date
@app.route('/api/activities/<int:user_id>/<int:date>JSON')
def userDayDataJSON(user_id):
    date = date
    activity = db_session.query(Activity).filter_by(id=user_id).one()
    sleep = db_session.query(Sleep).filter_by(
        user_id=user_id).order_by(sleep.activity.time_created)
    return jsonify(MenuItems=[i.serialize for i in items])


# TODO: All invividual user measurements by date
@app.route('/api/measurement/<int:user_id>/<int:date>/JSON')
def userDayMeasurementsJSON(user_id, menu_id):
    Menu_Item = db_session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(Menu_Item=Menu_Item.serialize)


# TODO: All invividual user activities by type
@app.route('/api/activities/<int:user_id>/<int:date>/<type>/JSON')
def userActivityType():
    restaurants = db_session.query(Restaurant).all()
    return jsonify(restaurants=[r.serialize for r in restaurants])


# TODO: Invividual user specific activity
@app.route('/api/activity/<int:user_id>/<int:activity_id>JSON')
def userActivityJSON():
    restaurants = db_session.query(Restaurant).all()
    return jsonify(restaurants=[r.serialize for r in restaurants])


# TODO: Individual user specific measurement
@app.route('/api/measurement/<int:user_id>/<int:measurement_id>JSON')
def userMeasurementJSON():
    restaurants = db_session.query(Restaurant).all()
    return jsonify(restaurants=[r.serialize for r in restaurants])


# TODO: UPDATE SUPER SECRET KEY TO app.config
if __name__ == '__main__':
    socketio.run(app, debug=True)
