from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from models import Base, User, Meal, Sleep, \
    Workout, Weight, BloodPressure, BloodSugar, HeartRate


engine = create_engine('sqlite:///healthdata.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)


Models = {'meal': Meal, 'sleep': Sleep, 'workout': Workout, 'weight': Weight,
          'bloodpressure': BloodPressure, 'bloodsugar': BloodSugar, 'heartrate': HeartRate}


@app.route("/")
@app.route("/activities", methods=['GET', 'POST'])
def activitiesFunction():
    if request.method == 'GET':
        # Call the method to Get all of the activities
        user_id = request.args.get('user_id', '')
        print("USER ID: {}".format(user_id))
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
            print(user_id)
            print(activity_type)
            print(description)
            print(duration)
            print(healthy)
            print(unhealthy)
            print(starch_rich)
            print(sucrose_rich)
            return makeANewMeal(user_id, description, duration, healthy, unhealthy, starch_rich, sucrose_rich)
        elif activity_type == 'sleep':
            description = request.args.get('description', '')
            print(activity_type)
            print(description)
            return makeANewSleep(activity_type, description)
        elif activity_type == 'workout':
            description = request.args.get('description', '')
            print(activity_type)
            print(description)
            return makeANewSleep(activity_type, description)


@app.route("/activities/<int:user_id>/<activity_type>/<int:activity_id>", methods=['GET', 'PUT', 'DELETE'])
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
            return updateMeal(user_id, meal_id, description, duration, healthy, unhealthy, starch_rich, sucrose_rich)

     # Call the method to remove a activity
    elif request.method == 'DELETE':
        return deleteActivity(user_id, activity_type, activity_id)


def getAllActivities(user_id):
    session.close()
    try:
        meals = session.query(Meal).filter_by(user_id=user_id).all()
        sleep_sessions = session.query(Sleep).filter_by(user_id=user_id).all()
        workouts = session.query(Workout).filter_by(user_id=user_id).all()
    except:
        session.rollback()
        raise
    finally:
        session.close()

    for meal in meals:
        meal.created = str(meal.created)
        meal.duration = str(meal.duration)
    for sleep in sleep_sessions:
        sleep.created = str(sleep.created)
        sleep.duration = str(sleep.duration)
    for workout in workouts:
        workout.created = str(workout.created)
        workout.duration = str(workout.duration)

    return jsonify(Meals=[i.serialize for i in meals], Sleep_sessions=[i.serialize for i in sleep_sessions], Workouts=[i.serialize for i in workouts])


def getActivity(user_id, activity_type, activity_id):
    for key, Model in Models.items():
        if key == activity_type:
            try:
                activity = session.query(Model).filter_by(
                    user_id=user_id).filter_by(id=activity_id).one()
            except:
                session.rollback()
                raise
            finally:
                session.close()
            activity.created = str(activity.created)
            activity.duration = str(activity.duration)
            return jsonify(activity_found=activity.serialize)


def makeANewMeal(user_id, description, duration, healthy, unhealthy, starch_rich, sucrose_rich):
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
    session.add(newMeal)
    try:
        session.commit()
    except:
        session.rollback()
        raise
    newMeal.created = str(newMeal.created)
    newMeal.duration = str(newMeal.duration)
    return jsonify(Meal=newMeal.serialize)


def updateMeal(user_id, meal_id, description, duration, healthy, unhealthy, starch_rich, sucrose_rich):
    try:
        meal = session.query(Meal).filter_by(
            user_id=user_id).filter_by(id=meal_id).one()
        print("FOUND MEAL TO UPDATE: {}".format(meal.id))
    except:
        session.rollback()
        raise
    finally:
        session.close()

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

    session.add(meal)
    try:
        session.commit()
    except:
        session.rollback()
        raise

    return "Updated a Meal with id %s" % meal_id


def deleteActivity(user_id, activity_type, activity_id):
    for key, Model in Models.items():
        if key == activity_type:
            try:
                activity = session.query(Model).filter_by(
                    user_id=user_id).filter_by(id=activity_id).one()
                print("FOUND ACTIVITY TO DELETE: {}".format(activity.id))
            except:
                session.rollback()
                raise
            finally:
                session.close()

    session.delete(activity)
    try:
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

    return "Removed Activity with id %s" % activity_id


if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0', port=5001)
