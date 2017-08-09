from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Activity, ActivityItem, Meal, Sleep, Workout, Measurement, Weight, BloodPressure, BloodSugar, HeartRate

app = Flask(__name__)

engine = create_engine('sqlite:///healthdata.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Show all activities and measurements
@app.route('/')
@app.route('/dashboard/<int:user_id>')
def showDashboard():
    activity_id = 1
    measurement_id = 1
    user_id = 1
    activities = session.query(Activity).all()
    measurements = session.query(Measurement).all()

    sleep_activities = session.query(Sleep).filter_by(
        user_id=user_id).all()

    workout_activities = session.query(Workout).filter_by(
        user_id=user_id).all()

    weight_measurements = session.query(Weight).filter_by(
        user_id=user_id).all()

    bp_measurements = session.query(BloodPressure).filter_by(
        user_id=user_id).all()

    # return "This page will show all my activities and measurements"
    for weight in weight_measurements:
        print("Weight:")
        print(weight.weight)
    for bp in bp_measurements:
        print("BP")
        print(bp.systolic)
    return render_template('dashboard.html', activities=activities,
                           measurements=measurements, sleep_activities=sleep_activities, workout_activities=workout_activities, weight_measurements=weight_measurements, bp_measurements=bp_measurements)


# TODO: Show all activities sortable by date
@app.route('/activities/')
def showActivities():
    activities = session.query(Activity).all()
    print(activities)
    # return "This page will show all my activities"
    return render_template('activities.html', activities=activities)


# TODO: Show all measurements sortable by date
@app.route('/measurements/')
def showMeasurements():
    measurements = session.query(Measurement).all()
    print(measurements)
    # return "This page will show all my restaurants"
    return render_template('measurements.html', measurements=measurements)


# TODO: Add new activity

# TODO: Edit activity

# TODO: Add new measurement

# TODO: Edit measurement


# API routes
# TODO: All users all data
@app.route('/activities/<int:user_id>/JSON')
def restaurantMenuJSON(restaurant_id):
    date = date
    activity = session.query(Activity).filter_by(id=user_id).one()
    sleep = session.query(Sleep).filter_by(
        user_id=user_id).order_by(sleep.activity.time_created)
    return jsonify(MenuItems=[i.serialize for i in items])


# TODO: All invividual users data
@app.route('/activities/<int:user_id>/JSON')
def restaurantMenuJSON(restaurant_id):
    date = date
    activity = session.query(Activity).filter_by(id=user_id).one()
    sleep = session.query(Sleep).filter_by(
        user_id=user_id).order_by(sleep.activity.time_created)
    return jsonify(MenuItems=[i.serialize for i in items])


# TODO: All invividual user activities by date
@app.route('/activities/<int:user_id>/<date:date>JSON')
def restaurantMenuJSON(restaurant_id):
    date = date
    activity = session.query(Activity).filter_by(id=user_id).one()
    sleep = session.query(Sleep).filter_by(
        user_id=user_id).order_by(sleep.activity.time_created)
    return jsonify(MenuItems=[i.serialize for i in items])


# TODO: All invividual user measurements by date
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    Menu_Item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(Menu_Item=Menu_Item.serialize)


# TODO: All invividualuser activities by type
@app.route('/restaurant/JSON')
def restaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(restaurants=[r.serialize for r in restaurants])


# TODO: Invividual user specific activity
@app.route('/restaurant/JSON')
def restaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(restaurants=[r.serialize for r in restaurants])


# TODO: Individual user specific measurement
@app.route('/restaurant/JSON')
def restaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(restaurants=[r.serialize for r in restaurants])


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
