from flask import session
import datetime
import time
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker

from models import Base, User, Meal, Sleep, \
    Workout, Weight, BloodPressure, BloodSugar, HeartRate


# Connect to Database and create database session
engine = create_engine('sqlite:///healthdata.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
db_session = DBSession()


class NewEntry:

    # def __init__(form=form):
    #     _form = form

    #     if _form == 'meal_form':
    #         meal(_form)

    def meal(meal_data):
        d = datetime.timedelta(hours=meal_data.time.data.hour,
                               minutes=meal_data.time.data.minute)
        healthy_val = 1
        unhealthy_val = 0
        if meal_data.health.data == 'unhealthy':
            healthy_val = 0
            unhealthy_val = 1
        newMeal = Meal(
            created=meal_data.date.data,
            description=meal_data.description.data,
            duration=d,
            healthy=healthy_val,
            unhealthy=unhealthy_val,
            user_id=session['user_id']
        )
        db_session.add(newMeal)
        db_session.commit()

    def sleep(sleep_data):
        t = datetime.time(sleep_data.time.data.hour,
                          sleep_data.time.data.minute, 0)

        newSleep = Sleep(
            duration=t,
            user_id=session['user_id']
        )
        db_session.add(newSleep)
        db_session.commit()

    def workout(workout_form):
        t = datetime.time(workout_form.time.data.hour,
                          workout_form.time.data.minute, 0)
        intense_val = 1
        light_val = 0
        interval_val = 1
        endurance_val = 0
        if workout_form.intensity.data == 'light':
            intense_val = 0
            light_val = 1
        if workout_form.workout_type.data == 'endurance':
            interval_val = 0
            endurance_val = 1
        newWorkout = Workout(
            duration=t,
            intense=intense_val,
            light=light_val,
            interval=interval_val,
            endurance=endurance_val,
            user_id=session['user_id']
        )
        db_session.add(newWorkout)
        db_session.commit()
