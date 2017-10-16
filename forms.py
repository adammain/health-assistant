import datetime

from flask_wtf import FlaskForm
from wtforms import validators, StringField, DateField, DateTimeField, \
    SelectField, TextAreaField, BooleanField, RadioField, SubmitField
from wtforms.validators import DataRequired

today = datetime.date.today


class MealForm(FlaskForm):
    date = DateField(u'Date', validators=[validators.Required()],
                     format='%m/%d/%Y',
                     default=datetime.date(today().year, today().month, today().day))
    time = DateTimeField(u'Time', format='%H:%M',
                         default=datetime.time(0, 0))
    health = SelectField(u'Meal Type', choices=[
        ('healthy', 'Healthy'), ('unhealthy', 'Unhealthy')])
    description = TextAreaField(u'Description')
    submit_meal = SubmitField('Add Meal')


class SleepForm(FlaskForm):
    date = DateField(u'Date', validators=[validators.Required()],
                     format='%m/%d/%Y',
                     default=datetime.date(today().year, today().month, today().day))
    time = DateTimeField(u'Time', format='%H:%M',
                         default=datetime.time(0, 0))
    submit_sleep = SubmitField('Add Sleep')


class WorkoutForm(FlaskForm):
    date = DateField(u'Date', validators=[validators.Required()],
                     format='%m/%d/%Y',
                     default=datetime.date(today().year, today().month, today().day))
    workout_type = RadioField('Workout Type', choices=[
        ('interval', 'Interval'),
        ('endurance', 'Endurance'),
    ])
    intensity = RadioField('Intensity', choices=[
        ('intense', 'Intense'),
        ('light', 'Light'),
    ])
    time = DateTimeField(u'Time', format='%H:%M',
                         default=datetime.time(0, 0))
    submit_workout = SubmitField('Add Workout')


class WeightForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    submit_weight = SubmitField('Add Weight')


class BloodPressureForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    submit_bloodpressure = SubmitField('Add Blood Pressure')


class BloodSugarForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    submit_bloodsugar = SubmitField('Add Blood Sugar')


class HeartRateForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    submit_heartrate = SubmitField('Add Heart Rate')
