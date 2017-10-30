from flask import session
import datetime
import time
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker

from models import Base, User, Meal, Sleep, \
    Workout, Weight, BloodPressure, BloodSugar, HeartRate
from forms import MealForm, SleepForm, WorkoutForm, WeightForm, \
    BloodPressureForm, BloodSugarForm, HeartRateForm


# Connect to Database and create database session
engine = create_engine('sqlite:///healthdata.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
db_session = DBSession()


class NewEntry():

    def __init__(self, form):
        self._form = form

        if isinstance(self._form, MealForm):
            self.meal(self._form)
        if isinstance(self._form, SleepForm):
            self.sleep(self._form)
        if isinstance(self._form, WorkoutForm):
            self.workout(self._form)
        if isinstance(self._form, WeightForm):
            self.weight(self._form)
        if isinstance(self._form, BloodPressureForm):
            self.blood_pressure(self._form)
        if isinstance(self._form, BloodSugarForm):
            self.blood_sugar(self._form)
        if isinstance(self._form, HeartRateForm):
            self.heart_rate(self._form)

    def meal(self, meal_data):
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
            starch_rich=meal_data.starch_rich.data,
            sucrose_rich=meal_data.sucrose_rich.data,
            user_id=session['user_id']
        )
        db_session.add(newMeal)
        db_session.commit()

    def sleep(self, sleep_data):
        d = datetime.timedelta(hours=sleep_data.time.data.hour,
                               minutes=sleep_data.time.data.minute)

        newSleep = Sleep(
            created=sleep_data.date.data,
            duration=d,
            user_id=session['user_id']
        )

        db_session.add(newSleep)
        db_session.commit()

    def workout(self, workout_data):
        d = datetime.timedelta(hours=workout_data.duration.data.hour,
                               minutes=workout_data.duration.data.minute)

        intense_val = 1
        light_val = 0
        interval_val = 1
        endurance_val = 0

        if workout_data.intensity.data == 'light':
            intense_val = 0
            light_val = 1
        if workout_data.workout_type.data == 'endurance':
            interval_val = 0
            endurance_val = 1

        newWorkout = Workout(
            created=workout_data.date.data,
            duration=d,
            intense=intense_val,
            light=light_val,
            interval=interval_val,
            endurance=endurance_val,
            user_id=session['user_id']
        )
        db_session.add(newWorkout)
        db_session.commit()

    def weight(self, weight_data):
        newWeight = Weight(
            created=weight_data.date.data,
            weight=weight_data.weight.data,
            user_id=session['user_id']
        )
        db_session.add(newWeight)
        db_session.commit()

    def blood_pressure(self, bp_data):
        newBP = BloodPressure(
            created=bp_data.date.data,
            systolic=bp_data.systolic.data,
            diastolic=bp_data.diastolic.data,
            user_id=session['user_id']
        )
        db_session.add(newBP)
        db_session.commit()

    def blood_sugar(self, bloodsugar_data):
        newBloodSugar = BloodSugar(
            created=bloodsugar_data.date.data,
            glucose_level=bloodsugar_data.glucose_level.data,
            insulin_level=bloodsugar_data.insulin_level.data,
            user_id=session['user_id']
        )
        db_session.add(newBloodSugar)
        db_session.commit()

    def heart_rate(self, heartrate_data):
        resting = 1
        active = 0

        if heartrate_data.measurement_type.data == 'active':
            resting = 0
            active = 1

        newHeartRate = HeartRate(
            created=heartrate_data.date.data,
            bpm=heartrate_data.bpm.data,
            active=active,
            resting=resting,
            user_id=session['user_id']
        )
        db_session.add(newHeartRate)
        db_session.commit()


class EditEntry:

    def __init__(self, form, id):
        self._form = form
        self._id = id

        if isinstance(self._form, MealForm):
            self.meal(self._form, self._id)
        if isinstance(self._form, SleepForm):
            self.sleep(self._form, self._id)
        if isinstance(self._form, WorkoutForm):
            self.workout(self._form, self._id)
        if isinstance(self._form, WeightForm):
            self.weight(self._form, self._id)
        if isinstance(self._form, BloodPressureForm):
            self.blood_pressure(self._form, self._id)
        if isinstance(self._form, BloodSugarForm):
            self.blood_sugar(self._form, self._id)
        if isinstance(self._form, HeartRateForm):
            self.heart_rate(self._form, self._id)

    def meal(self, meal_data, id):
        d = datetime.timedelta(hours=meal_data.time.data.hour,
                               minutes=meal_data.time.data.minute)
        healthy_val = 1
        unhealthy_val = 0
        if meal_data.health.data == 'unhealthy':
            healthy_val = 0
            unhealthy_val = 1

        updatedMeal = db_session.query(Meal).filter_by(id=id).one()
        updatedMeal.created = meal_data.date.data
        updatedMeal.duration = d
        updatedMeal.healthy = healthy_val
        updatedMeal.unhealthy = unhealthy_val
        updatedMeal.description = meal_data.description.data
        updatedMeal.starch_rich = meal_data.starch_rich.data
        updatedMeal.sucrose_rich = meal_data.sucrose_rich.data

        db_session.add(updatedMeal)
        db_session.commit()
        db_session.close()

    def sleep(self, sleep_data, id):
        d = datetime.timedelta(hours=sleep_data.time.data.hour,
                               minutes=sleep_data.time.data.minute)

        updatedSleep = db_session.query(Sleep).filter_by(id=id).one()
        updatedSleep.created = sleep_data.date.data
        updatedSleep.duration = d

        db_session.add(updatedSleep)
        db_session.commit()
        db_session.close()

    def workout(self, workout_data, id):
        d = datetime.timedelta(hours=workout_data.duration.data.hour,
                               minutes=workout_data.duration.data.minute)

        intense_val = 1
        light_val = 0
        interval_val = 1
        endurance_val = 0
        if workout_data.intensity.data == 'light':
            intense_val = 0
            light_val = 1
        if workout_data.workout_type.data == 'endurance':
            interval_val = 0
            endurance_val = 1

        updatedWorkout = db_session.query(Workout).filter_by(id=id).one()
        updatedWorkout.created = workout_data.date.data
        updatedWorkout.duration = d
        updatedWorkout.intense = intense_val
        updatedWorkout.light = light_val
        updatedWorkout.interval = interval_val
        updatedWorkout.endurance = endurance_val

        db_session.add(updatedWorkout)
        db_session.commit()
        db_session.close()

    def weight(self, weight_data, id):
        updatedWeight = db_session.query(Weight).filter_by(id=id).one()
        updatedWeight.created = weight_data.date.data
        updatedWeight.weight = weight_data.weight.data

        db_session.add(updatedWeight)
        db_session.commit()
        db_session.close()

    def blood_pressure(self, bp_data, id):
        updatedBP = db_session.query(BloodPressure).filter_by(id=id).one()
        updatedBP.created = bp_data.date.data
        updatedBP.systolic = bp_data.systolic.data
        updatedBP.diastolic = bp_data.diastolic.data

        db_session.add(updatedBP)
        db_session.commit()
        db_session.close()

    def blood_sugar(self, bloodsugar_data, id):
        updatedBS = db_session.query(BloodSugar).filter_by(id=id).one()
        print("SEARCH FOR BS ENTRY: {}".format(id))
        updatedBS.created = bloodsugar_data.date.data
        updatedBS.glucose_level = bloodsugar_data.glucose_level.data
        updatedBS.insulin_level = bloodsugar_data.insulin_level.data
        print("FOUND BS ENTRY: {}".format(updatedBS.id))
        print("UPDATE BS glucose_level: {}".format(updatedBS.glucose_level))

        db_session.add(updatedBS)
        db_session.commit()
        db_session.close()

    def heart_rate(self, heartrate_data, id):
        updatedHeartRate = db_session.query(HeartRate).filter_by(id=id).one()
        print("SEARCH FOR HeartRate ENTRY: {}".format(id))

        resting = 1
        active = 0
        if heartrate_data.measurement_type.data == 'active':
            resting = 0
            active = 1

        updatedHeartRate.created = heartrate_data.date.data
        updatedHeartRate.bpm = heartrate_data.bpm.data
        updatedHeartRate.resting = resting
        updatedHeartRate.active = active
        print("FOUND HeartRate ENTRY: {}".format(updatedHeartRate.id))
        print("UPDATE HeartRate Resting: {}".format(updatedHeartRate.bpm))

        db_session.add(updatedHeartRate)
        db_session.commit()
        db_session.close()
