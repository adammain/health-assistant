import datetime

from flask_wtf import FlaskForm
from wtforms import validators, StringField, DateField, DateTimeField, \
    SelectField, TextAreaField, BooleanField, RadioField, SubmitField, \
    HiddenField, IntegerField
from wtforms.validators import DataRequired

today = datetime.date.today


class MealForm(FlaskForm):
    date = DateField(u'Date', validators=[validators.Required()],
                     format='%m/%d/%Y',
                     default=datetime.date(today().year,
                                           today().month,
                                           today().day))
    time = DateTimeField(u'Time', format='%H:%M',
                         default=datetime.time(0, 0))
    health = SelectField(u'Meal Type', choices=[
        ('healthy', 'Healthy'), ('unhealthy', 'Unhealthy')])
    starch_rich = BooleanField(u'Starchy', default=False)
    sucrose_rich = BooleanField(u'Sucrose Rich', default=False)
    description = TextAreaField(u'Description')
    submit_meal = SubmitField('Submit')


class SleepForm(FlaskForm):
    date = DateField(u'Date', validators=[validators.Required()],
                     format='%m/%d/%Y',
                     default=datetime.date(today().year,
                                           today().month,
                                           today().day))
    time = DateTimeField(u'Time', format='%H:%M',
                         default=datetime.time(0, 0))
    submit_sleep = SubmitField('Submit Sleep')


class WorkoutForm(FlaskForm):
    date = DateField(u'Date', validators=[validators.Required()],
                     format='%m/%d/%Y',
                     default=datetime.date(today().year,
                                           today().month,
                                           today().day))
    duration = DateTimeField(u'Time', format='%H:%M',
                             default=datetime.time(0, 0))
    workout_type = RadioField('Workout Type', choices=[
        ('interval', 'Interval'),
        ('endurance', 'Endurance'),
    ])
    intensity = RadioField('Intensity', choices=[
        ('intense', 'Intense'),
        ('light', 'Light'),
    ])
    submit_workout = SubmitField('Submit Workout')


class WeightForm(FlaskForm):
    date = DateField(u'Date', validators=[validators.Required()],
                     format='%m/%d/%Y',
                     default=datetime.date(today().year,
                                           today().month,
                                           today().day))
    weight = IntegerField(u'Weight', validators=[validators.Required()])
    submit_weight = SubmitField('Submit Weight')


class BloodPressureForm(FlaskForm):
    date = DateField(u'Date', validators=[validators.Required()],
                     format='%m/%d/%Y',
                     default=datetime.date(today().year,
                                           ftoday().month,
                                           ftoday().day))
    systolic = IntegerField(u'Systolic', validators=[validators.Required()])
    diastolic = IntegerField(u'Diastolic', validators=[validators.Required()])
    submit_bloodpressure = SubmitField('Submit Measurement')


class BloodSugarForm(FlaskForm):
    date = DateField(u'Date', validators=[validators.Required()],
                     format='%m/%d/%Y',
                     default=datetime.date(today().year,
                                           today().month,
                                           today().day))
    glucose_level = IntegerField(u'Glucose Level', validators=[
                                 validators.Required()])
    insulin_level = IntegerField(u'Insulin Level', validators=[
                                 validators.Required()])
    submit_bloodsugar = SubmitField('Submit Measurement')


class HeartRateForm(FlaskForm):
    date = DateField(u'Date', validators=[validators.Required()],
                     format='%m/%d/%Y',
                     default=datetime.date(today().year,
                                           today().month,
                                           today().day))
    bpm = IntegerField(u'BPM', validators=[
        validators.Required()])
    measurement_type = RadioField('HR Measurement Type', choices=[
        ('resting', 'Resting'),
        ('active', 'Active'),
    ])
    submit_heartrate = SubmitField('Submit Measurement')
