from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, User, Activity, ActivityItem, Meal, Sleep, Workout, Measurement, Weight, BloodPressure, BloodSugar, HeartRate

engine = create_engine('sqlite:///healthdata.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create dummy user
User1 = User(name="Camila Main", email="mcamilaparradiaz@gmail.com",
             picture='https://cdn-images-1.medium.com/fit/c/200/200/1*neY8KnUgTLFgRYO2flt4sg.jpeg')
session.add(User1)
session.commit()

# Measurement1 for User Camila Main
measurement1 = Measurement(user_id=1, morning=True, pre_meal=True)

session.add(measurement1)
session.commit()

# Weight1 in Measurement1 for User Camila Main
weight1 = Weight(user_id=1, measurement=measurement1, weight=115)

session.add(weight1)
session.commit()

# Activity2 for User Camila Main
activity1 = Activity(user_id=1)

session.add(activity1)
session.commit()

# Workout2 in Activity2 for User Camila Main
workout1 = Workout(user_id=1, activity=activity1, duration=35, intense=True,
                   light=False, interval=True, endurance=False, type="Youtube HIIT")

session.add(workout1)
session.commit()

# Measurement2 for User Camila Main
measurement2 = Measurement(user_id=1, morning=True, pre_meal=True)

session.add(measurement2)
session.commit()

# BloodPressure2 in Measurement2 for User Camila Main
bloodpressure1 = BloodPressure(
    user_id=1, measurement=measurement2, systolic=120, diastolic=80)

session.add(bloodpressure1)
session.commit()

# Activity1 for User Camila Main
activity2 = Activity(user_id=1)

session.add(activity2)
session.commit()

# Sleep1 in Activity1 for User Camila Main
sleep1 = Sleep(user_id=1, activity=activity2, duration=30)

session.add(sleep1)
session.commit()


print("added menu items!")
