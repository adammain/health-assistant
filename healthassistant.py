from flask import Flask, Response, render_template, request, redirect, \
    jsonify, Markup, url_for, flash, session
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
import babel
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

# save sessions on server with flask_sessions ext. (Redis)
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

# Models Object for looping (API primarily)
Models = {'meal': Meal, 'sleep': Sleep, 'workout': Workout, 'weight': Weight,
          'bloodpressure': BloodPressure, 'bloodsugar': BloodSugar,
          'heartrate': HeartRate}


# # User Helper Functions
def createUser(session):
    newUser = User(name=session.get('username'), email=session.get(
                   'email'), picture=session.get('picture'))
    db_session.add(newUser)
    db_session.commit()
    user = db_session.query(User).filter_by(email=session.get('email')).one()
    return user.id


# Helper function: Return current user data
def getUserInfo(user_id):
    user = db_session.query(User).filter_by(id=user_id).one()
    return user


# Helper function: Return current user id
def getUserID(email):
    try:
        user = db_session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Helper function: Return all DB entries for user
def getAllDB(user_id, date):
    meals = db_session.query(Meal) \
        .filter(func.DATE(Meal.created) == date) \
        .filter_by(user_id=user_id) \
        .all()

    sleep = db_session.query(Sleep) \
        .filter(func.DATE(Sleep.created) == date) \
        .filter_by(user_id=user_id) \
        .all()

    workouts = db_session.query(Workout) \
        .filter(func.DATE(Workout.created) == date) \
        .filter_by(user_id=user_id) \
        .all()

    weights = db_session.query(Weight) \
        .filter(func.DATE(Weight.created) == date) \
        .filter_by(user_id=user_id) \
        .all()

    bloodpressure = db_session.query(BloodPressure) \
        .filter(func.DATE(BloodPressure.created) == date) \
        .filter_by(user_id=user_id) \
        .all()

    bloodsugar = db_session.query(BloodSugar) \
        .filter(func.DATE(BloodSugar.created) == date) \
        .filter_by(user_id=user_id) \
        .all()

    heartrate = db_session.query(HeartRate) \
        .filter(func.DATE(HeartRate.created) == date) \
        .filter_by(user_id=user_id) \
        .all()

    entries = {'meals': meals, 'sleep': sleep, 'workouts': workouts,
               'weights': weights, 'bloodpressure': bloodpressure,
               'bloodsugar': bloodsugar, 'heartrate': heartrate}

    return entries


# Helper function: Return all entry forms
def getForms(date=None):
    meal_form = MealForm(date=date)
    sleep_form = SleepForm(date=date)
    workout_form = WorkoutForm(date=date)
    weight_form = WeightForm(date=date)
    bloodpressure_form = BloodPressureForm(date=date)
    bloodsugar_form = BloodSugarForm(date=date)
    heartrate_form = HeartRateForm(date=date)

    forms = {'meal': meal_form, 'sleep': sleep_form, 'workout': workout_form,
             'weight': weight_form, 'blood_pressure': bloodpressure_form,
             'blood_sugar': bloodsugar_form, 'heart_rate': heartrate_form}

    forms_submit_checks = {'meal': meal_form.submit_meal,
                           'sleep': sleep_form.submit_sleep,
                           'workout': workout_form.submit_workout,
                           'weight': weight_form.submit_weight,
                           'blood_pressure':
                           bloodpressure_form.submit_bloodpressure,
                           'blood_sugar': bloodsugar_form.submit_bloodsugar,
                           'heart_rate': heartrate_form.submit_heartrate}

    return forms, forms_submit_checks


# Helper function: Remove microseconds from time
def chop_microseconds(delta):
    return delta - datetime.timedelta(microseconds=delta.microseconds)


# Helper function: Format time display piping filter
@app.template_filter('hour_min')
def _jinja2_filter_datetime(time_delta):
    minutes = "%02d" % ((time_delta.seconds // 60) % 60,)
    hours = time_delta.seconds // 3600
    return str(hours) + ":" + str(minutes)


# Helper function: Send login data to all tempates
@app.context_processor
def utility_processor():
    if 'username' in session:
        return dict(logged_in=True, provider=session['provider'])
    else:
        return dict(logged_in=False)


# # OAuth/Login/User Functions
@app.route('/login')
def showLogin():
    print("LOGIN SESSION: {}".format(session))
    access_token = session.get('access_token')
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    session['state'] = state

    # Only display login button for provider of previous logins
    if 'provider' not in session:
        return render_template('login.html', STATE=state, provider=None)
    elif session['provider'] == 'google':
        return render_template('login.html', STATE=state, provider='google')
    else:
        return render_template('login.html', STATE=state, provider='facebook')


# FB OAuth connection - Create/Test token and session
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = request.data
    print("ACCESS TOK: {}".format(access_token))
    if len(access_token) <= 5:
        print("BROKEN ACCESS TOKEN")
        if 'access_token' not in session:
            flash(
                "Error logging in with provider.  \
                Please clear broswer cache and reattempt.")
            return render_template('login.html')
        else:
            print("USING SAVED ACCESS TOKEN")
            access_token = session['access_token']
    else:
        access_token = access_token.decode("utf-8")

    print("access token received %s " % access_token)

    # exchange client token for long-lived server-side token with GET
    app_id = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/v2.9/oauth/access_token?'
           'grant_type=fb_exchange_token&client_id=%s&client_secret=%s'
           '&fb_exchange_token=%s') % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1].decode('utf-8')
    data = json.loads(result)
    token = 'access_token=' + data['access_token']
    # see: https://discussions.udacity.com/t/
    #   issues-with-facebook-oauth-access-token/233840?source_topic_id=174342

    # Use token to get user info from API
    # make API call with new token
    url = \
        'https://graph.facebook.com/v2.9/me?%s&fields=name,id,email,picture' \
        % token

    h = httplib2.Http()
    result = h.request(url, 'GET')[1].decode('utf-8')
    data = json.loads(result)
    session['provider'] = 'facebook'
    session['username'] = data['name']
    session['email'] = data['email']
    session['facebook_id'] = data['id']
    session['picture'] = data['picture']["data"]["url"]
    session['access_token'] = access_token

    # see if user exists
    try:
        user = db_session.query(User).filter_by(email=session['email']).one()
        user_id = user.id
    except:
        user_id = createUser(session)

    if not user_id:
        user_id = createUser(session)
    session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += session['username']
    output += '!</h1><img src="'
    output += session['picture']
    output += ' ">'

    flash("Now logged in as %s" % session['username'])
    return output


# FB OAuth disconnect
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = session['facebook_id']
    # The access token must me included to successfully logout
    access_token = session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1].decode('utf-8')
    flash('You have been successfully logged out.')
    return redirect(url_for('showLogin'))


# Google OAuth connection - Create token and session
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
        response = make_response(
            json.dumps('Current user is already connected.'),
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
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px; \
    -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % session.get('username'))
    print("done!")
    return output


# Google disconnect - Revoke current token and reset session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = session.get('access_token')
    print("ACCESS TOKEN: {}".format(access_token))
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print("Result:".format(result))
    if result['status'] == '200':
        del session['access_token']
        del session['gplus_id']
        del session['username']
        del session['email']
        del session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash(response)
        return redirect(url_for('showLogin'))
        # return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# # General routing functions
@app.route('/', methods=('GET', 'POST'))
@app.route('/home/', methods=('GET', 'POST'))
def showHome():
    if 'username' not in session:
        return redirect(url_for('showLogin'))
    else:
        days = {0: "M", 1: "T", 2: "W", 3: "Th", 4: "F", 5: "S", 6: "Su"}
        now = datetime.datetime.now()
        year, month, day = now.year, now.month, now.day
        if 'year' in request.args:
            year = int(request.args['year'])
            month = int(request.args['month'])
            day = int(request.args['day'])
        display_date = datetime.date(year, month, day)
        current_date = datetime.date(now.year, now.month, now.day)
        user_id = session['user_id']
        forms, forms_submit_checks = getForms()
        entries = getAllDB(user_id, display_date)

        return render_template('home.html',
                               forms=forms,
                               entries=entries,
                               days=days,
                               display_date=display_date,
                               display_year=display_date.year,
                               display_month=display_date.month,
                               display_day=display_date.day,
                               current_date=current_date,
                               current_year=now.year,
                               current_month=now.month,
                               current_day=now.day)


# Add new DB Entry
@app.route('/new-entry/', methods=('GET', 'POST'))
@app.route('/new-entry/<int:year>/<int:month>/<int:day>',
           methods=('GET', 'POST'))
def newEntry(year=datetime.datetime.now().year,
             month=datetime.datetime.now().month,
             day=datetime.datetime.now().day):
    if 'username' not in session:
        return redirect('/login')

    date = datetime.date(year, month, day)
    entry_name = None
    user_id = session.get('user_id')

    forms, forms_submit_checks = getForms(date=date)

    # Runs after forms are submitted, checks validity, submits form to helper
    for key, form in forms.items():
        if forms_submit_checks[key].data and form.validate_on_submit():
            helpers.NewEntry(form)
            table, entry_name = forms[key], key.title()

    # If form entry successfully added, flash message and redirect home
    if entry_name is not None:
        flash('New %s entry added successfully' % entry_name)
        db_session.commit()
        # TODO: Add redirect to display date as year/month/day
        return redirect(url_for('showHome', year=year, month=month, day=day))

    # return "This page will show all my activities"
    return render_template('newEntry.html',
                           meal_form=forms['meal'],
                           sleep_form=forms['sleep'],
                           workout_form=forms['workout'],
                           weight_form=forms['weight'],
                           bloodpressure_form=forms['blood_pressure'],
                           bloodsugar_form=forms['blood_sugar'],
                           heartrate_form=forms['heart_rate'])


# Edit existing DB entry
@app.route('/edit-entry/', methods=('GET', 'POST'))
@app.route('/edit-entry/<int:year>/<int:month>/<int:day>',
           methods=('GET', 'POST'))
def editEntry(year=datetime.datetime.now().year,
              month=datetime.datetime.now().month,
              day=datetime.datetime.now().day):
    if 'username' not in session:
        return redirect('/login')

    current_date = datetime.date(year, month, day)
    entry_name = None
    user_id = session.get('user_id')

    if 'year' in request.args:
        year = request.args['year']
        month = request.args['month']
        day = request.args['day']
    if 'id' in request.args and request.method == 'POST':
        id = request.args['id']

    forms, forms_submit_checks = getForms()

    # Runs after Modal forms are submitted, checks validity, submits form
    for key, form in forms.items():
        if forms_submit_checks[key].data and form.validate_on_submit():
            helpers.EditEntry(form, id)
            table, entry_name = forms[key], key.title()

        # If edit entry failed display error message
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print("ERROR MESSAGE: {}".format(err))
            return jsonify({'Error saving data': request.form})

    if entry_name is not None:
        flash('%s entry updated successfully' % entry_name)
        db_session.commit()
        return redirect(url_for('showHome', year=year, month=month, day=day))

    # If edit entry failed redirect to home page with error message
    flash('Failed to update with %s. Please attempt again.' %
          (jsonify({'test': request.form})))
    return redirect(url_for('showHome', year=year, month=month, day=day))


# Delete existing DB entry
@app.route('/delete-entry/', methods=('GET', 'POST'))
@app.route('/delete-entry/<int:year>/<int:month>/<int:day>',
           methods=('GET', 'POST'))
def deleteEntry(id=None):
    if 'username' not in session:
        return redirect('/login')

    print("METHOD TYPE: {}".format(request.method))
    print("ID: {}".format(request.args))

    if 'id' in request.args and request.method == 'POST':
        id = int(request.args['id'])
        type = request.args['type']

        if type == 'meal':
            meal = db_session.query(Meal).filter_by(id=id).one()
            db_session.delete(meal)
            db_session.commit()
        elif type == 'sleep':
            sleep = db_session.query(Sleep).filter_by(id=id).one()
            db_session.delete(sleep)
            db_session.commit()
        elif type == 'workout':
            workout = db_session.query(Workout).filter_by(id=id).one()
            db_session.delete(workout)
            db_session.commit()
        elif type == 'weight':
            print("DELETE WEIGHT")
            weight = db_session.query(Weight).filter_by(id=id).one()
            db_session.delete(weight)
            db_session.commit()
        elif type == 'bloodpressure':
            bloodpressure = db_session.query(
                BloodPressure).filter_by(id=id).one()
            db_session.delete(bloodpressure)
            db_session.commit()
        elif type == 'bloodsugar':
            bloodsugar = db_session.query(
                BloodSugar).filter_by(id=id).one()
            db_session.delete(bloodsugar)
            db_session.commit()
        elif type == 'heartrate':
            heartrate = db_session.query(
                HeartRate).filter_by(id=id).one()
            db_session.delete(heartrate)
            db_session.commit()

        flash('%s entry successfully deleted.' % type.title())
        return redirect(url_for('showHome', year=int(request.args['year']),
                                month=int(request.args['month']),
                                day=int(request.args['day'])))

    flash('Failed to delete entry. Please attempt again.')
    return redirect(url_for('showHome', year=int(request.args['year']),
                            month=int(request.args['month']),
                            day=int(request.args['day'])))


# # START of SocketIO implimentation
# Timer thread. Manages running timer.
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
        socketio.sleep(1)

        if session['active_timer'] is not None and \
                timers[session['active_timer']].running:
            timer = timers[session['active_timer']]

        timer_btn_text = ''
        if timer and timer.running:
            seconds = timer.runningElapsed
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            time = "%d:%02d" % (h, m)
            socketio.emit('timer_response',
                          {'data': 'Server generated event',
                              'count': time,
                              'active_timer': session['active_timer']},
                          namespace='/timer')
        else:
            thread_live = False
            global thread
            with thread_lock:
                print("Thread set: None")
                thread = None


# Start timer
@socketio.on('activate_timer', namespace='/timer')
def activate(message):
    # create room for this activities timer
    join_room(message['room'])

    # save active timer info to current session
    session['active_timer'] = message['type'] + message['room']
    # session['active_timer_type'] =
    print("PREPARING TO ACTIVATE TIMER: {}".format(session['active_timer']))
    print("TIME DETAILS: {}".format(message))

    models = {'meal': Meal, 'sleep': Sleep, 'workout':
              Workout, 'weight': Weight, 'bloodpressure': BloodPressure,
              'bloodsugar': BloodSugar, 'heartrate': HeartRate}

    for key, model in models.items():
        if key == message['type']:
            # get activities current saved time from DB
            print("ACTIVATE %s TIMER" % key)
            activity = db_session.query(model).filter(
                model.id == message['room']).one()
            start_with_time = activity.duration.total_seconds()

    # elif message['type'] == 'sleep':
    #     print("ACTIVATE SLEEP TIMER")
    #     sleep = db_session.query(Sleep).filter(
    #         Sleep.id == message['room']).one()
    #     start_with_time = sleep.duration.total_seconds()

    print("START WITH TIME: {}".format(start_with_time))
    # start timer for activity
    print("Starting Timer...")
    global timerKey
    timerID = message['type'] + message['room']
    global timers
    timers = {timerID: Timer()}
    timers[timerID].start(start_with_time)

    print("Timer STARTED")
    print("activated TIMER: " + str(session['active_timer']))

    # start background websocket thread for active timer
    global thread
    with thread_lock:
        if thread is None:
            print("Background thread fire request...")
            thread = socketio.start_background_task(
                background_thread, session._get_current_object())

    # send response for log update
    emit('my_response',
         {'data': 'TIMER STARTED',
          'active_timer': session['active_timer']})


# Stop timer and update DB
@socketio.on('deactivate_timer', namespace='/timer')
def deactivate(message):
    timerID = message['type'] + message['room']
    print("Deactivate TimerID: {}".format(timerID))
    timer = timers[timerID]
    if timer.running:
        print("Stopping Timer...")
        timer.stop()
        print("Timer STOPPED")
    leave_room(message['room'])
    # Save timer info to db
    print("Activity: {}".format(message['type']))

    models = {'meal': Meal, 'sleep': Sleep,
              'workout': Workout, 'weight': Weight,
              'bloodpressure': BloodPressure,
              'bloodsugar': BloodSugar, 'heartrate': HeartRate}

    for key, model in models.items():
        if key == message['type']:
            print("SAVE SAVE SAVE SAVE")
            activity = db_session.query(model).filter(
                model.id == message['room']).one()
            elapsed_time = datetime.timedelta(seconds=timer.elapsed)
            print("Duration Before: " + str(activity.duration))
            print("Change To: " + str(elapsed_time))
            activity.duration = elapsed_time
            db_session.add(activity)
            db_session.commit()
            activity = db_session.query(model).filter(
                model.id == message['room']).one()
            print("Duration After: " + str(activity.duration))

            # Reset background thread and send log deactivate message
            global thread
            thread = None
            print("Thread setting: None")
            emit('my_response',
                 {'data': 'TIMER STOPPED',
                  'active_timer': session['active_timer']})
            session['active_timer'] = None
            print("Active Timer: {}".format(session['active_timer']))


# Background thread initiation test:
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


# Background thread disconnect test:
@socketio.on('disconnect', namespace='/timer')
def test_disconnect():
    print('Client disconnected', request.sid)

# # End of SocketIO test implimentation


# # API Implementation
@app.route("/")
@app.route("/activities", methods=['GET', 'POST'])
def activitiesFunction():
    if request.method == 'GET':
        # Call the method to Get all of the activities
        user_id = request.args.get('user_id', '')
        return getAllActivities(user_id)
    elif request.method == 'POST':
        # Call the method to make a new activity
        print("Making a New activity")
        activity_type = request.args.get('type', '')

        if activity_type == 'meal':
            user_id = request.args.get('user_id', '')
            description = request.args.get('description', '')
            duration = request.args.get('duration', '')
            healthy = request.args.get('healthy', '')
            unhealthy = request.args.get('unhealthy', '')
            starch_rich = request.args.get('starch_rich', '')
            sucrose_rich = request.args.get('sucrose_rich', '')
            return makeANewMeal(user_id, description, duration, healthy,
                                unhealthy, starch_rich, sucrose_rich)
        elif activity_type == 'sleep':
            description = request.args.get('description', '')
            return makeANewSleep(activity_type, description)
        elif activity_type == 'workout':
            description = request.args.get('description', '')
            return makeANewSleep(activity_type, description)


@app.route("/activities/<int:user_id>/<activity_type>/<int:activity_id>",
           methods=['GET', 'PUT', 'DELETE'])
# Call the method to view a specific activity
def activitiesFunctionId(user_id, activity_type, activity_id):
    if request.method == 'GET':
        return getActivity(user_id, activity_type, activity_id)

    # Call the method to edit a specific activity
    elif request.method == 'PUT':
        if activity_type == 'meal':
            meal_id = activity_id
            description = request.args.get('description', '')
            duration = request.args.get('duration', '')
            healthy = request.args.get('healthy', '')
            unhealthy = request.args.get('unhealthy', '')
            starch_rich = request.args.get('starch_rich', '')
            sucrose_rich = request.args.get('sucrose_rich', '')
            return updateMeal(user_id, meal_id, description, duration, healthy,
                              unhealthy, starch_rich, sucrose_rich)

    # Call the method to remove a activity
    elif request.method == 'DELETE':
        return deleteActivity(user_id, activity_type, activity_id)


def getAllActivities(user_id):
    db_session.close()
    try:
        meals = db_session.query(Meal) \
            .filter_by(user_id=user_id).all()
        sleep_sessions = db_session.query(Sleep) \
            .filter_by(user_id=user_id).all()
        workouts = db_session.query(Workout) \
            .filter_by(user_id=user_id).all()
    except:
        db_session.rollback()
        raise
    finally:
        db_session.close()

    for meal in meals:
        meal.created = str(meal.created)
        meal.duration = str(meal.duration)
    for sleep in sleep_sessions:
        sleep.created = str(sleep.created)
        sleep.duration = str(sleep.duration)
    for workout in workouts:
        workout.created = str(workout.created)
        workout.duration = str(workout.duration)

    return jsonify(Meals=[i.serialize for i in meals],
                   Sleep_sessions=[i.serialize for i in sleep_sessions],
                   Workouts=[i.serialize for i in workouts])


def getActivity(user_id, activity_type, activity_id):
    for key, Model in Models.items():
        if key == activity_type:
            try:
                activity = db_session.query(Model).filter_by(
                    user_id=user_id).filter_by(id=activity_id).one()
            except:
                db_session.rollback()
                raise
            finally:
                db_session.close()
            activity.created = str(activity.created)
            activity.duration = str(activity.duration)
            return jsonify(activity_found=activity.serialize)


def makeANewMeal(user_id, description, duration, healthy, unhealthy,
                 starch_rich, sucrose_rich):
    now = datetime.datetime.now()
    created = datetime.date(now.year, now.month, now.day)
    hours, minutes = duration.split(':')
    duration = datetime.timedelta(hours=int(hours), minutes=int(minutes))

    newMeal = Meal(
        created=created,
        description=description,
        duration=duration,
        healthy=0,
        unhealthy=1,
        starch_rich=0,
        sucrose_rich=1,
        user_id=user_id
    )
    db_session.add(newMeal)
    try:
        db_session.commit()
    except:
        db_session.rollback()
        raise
    newMeal.created = str(newMeal.created)
    newMeal.duration = str(newMeal.duration)
    return jsonify(Meal=newMeal.serialize)


def updateMeal(user_id, meal_id, description, duration, healthy,
               unhealthy, starch_rich, sucrose_rich):
    try:
        meal = db_session.query(Meal).filter_by(
            user_id=user_id).filter_by(id=meal_id).one()
    except:
        db_session.rollback()
        raise
    finally:
        db_session.close()

    if description:
        meal.description = description
    if duration:
        meal.duration = duration
    if healthy:
        meal.healthy = healthy
    if unhealthy:
        meal.unhealthy = unhealthy
    if starch_rich:
        meal.starch_rich = starch_rich
    if sucrose_rich:
        meal.sucrose_rich = sucrose_rich

    db_session.add(meal)
    try:
        db_session.commit()
    except:
        db_session.rollback()
        raise

    return "Updated a Meal with id %s" % meal_id


def deleteActivity(user_id, activity_type, activity_id):
    for key, Model in Models.items():
        if key == activity_type:
            try:
                activity = db_session.query(Model) \
                    .filter_by(user_id=user_id) \
                    .filter_by(id=activity_id).one()
            except:
                db_session.rollback()
                raise
            finally:
                db_session.close()

    db_session.delete(activity)
    try:
        db_session.commit()
    except:
        db_session.rollback()
        raise
    finally:
        db_session.close()

    return "Removed Activity with id %s" % activity_id

# TODO: UPDATE SUPER SECRET KEY TO app.config
if __name__ == '__main__':
    socketio.run(app, debug=True)
