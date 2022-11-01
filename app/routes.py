from _curses import flash
from datetime import date

from flask import render_template

from app import app, db
from app.models import User, Location, Space, meetingHistory, upcomingMeeting, reviews, Tech, TechToSpace


@app.route('/')
@app.route('/home')
def home():
    return 'Hello world!'


@app.route('/reset_db')
def reset_db():
    flash("Resetting database: deleting old data and repopulating with dummy data")
    # clear all data from all tables
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        # print('Clear table {}'.format(table))
        db.session.execute(table.delete())
    db.session.commit()
    return render_template('index.html', title="Home")


@app.route('/populate_db')
def populate_db():
    reset_db()

    L1 = Location(name="Williams Hall",
                  city="Ithaca",
                  state="NY",
                  zip=14850
                  )
    L2 = Location(name="Friends Hall",
                  city="Ithaca",
                  state="NY",
                  zip=14850
                  )
    L3 = Location(name="CNS",
                  city="Ithaca",
                  state="NY",
                  zip=14850
                  )
    db.session.add_all([L1, L2, L3])
    db.session.commit()

    S1 = Space(name="Williams 320",
               sizeCap=25,
               hourlyRate=10,
               location=L1.id
               )
    S2 = Space(name="Williams 310",
               sizeCap=40,
               hourlyRate=15,
               location=L1.id
               )
    S3 = Space(name="Friends 207",
               sizeCap=20,
               hourlyRate=8,
               location=L2.id
               )
    S4 = Space(name="CNS 112",
               sizeCap=100,
               hourlyRate=20,
               location=L3.id
               )
    S5 = Space(name="CNS 200",
               sizeCap=15,
               hourlyRate=0,
               location=L3.id
               )
    S6 = Space(name="CNS 321",
               sizeCap=8,
               hourlyRate=5,
               location=L3.id
               )
    db.session.add_all([S1, S2, S3, S4, S5, S6])
    db.session.commit()

    MH1 = meetingHistory(uid=1,
                         spid=S3.id,
                         date=date(2020, 10, 10),
                         startTime="10:30",
                         endTime="11:30")

    MH2 = meetingHistory(uid=1,
                         spid=S4.id,
                         date=date(2021, 10, 10),
                         startTime="10:30",
                         endTime="11:30")

    MH3 = meetingHistory(uid=2,
                         spid=S3.id,
                         date=date(2020, 9, 10),
                         startTime="8:00",
                         endTime="10:00")

    MH4 = meetingHistory(uid=3,
                         spid=S3.id,
                         date=date(2019, 4, 8),
                         startTime="12:00",
                         endTime="1:00")

    db.session.add_all([MH1, MH2, MH3, MH4])
    db.session.commit()

    UM1 = upcomingMeeting(uid=1,
                         spid=S3.id,
                         date=date(2023, 10, 10),
                         startTime="10:30",
                         endTime="11:30")

    UM2 = upcomingMeeting(uid=2,
                         spid=S4.id,
                         date=date(2023, 11, 12),
                         startTime="10:30",
                         endTime="11:30")

    UM3 = upcomingMeeting(uid=2,
                         spid=S3.id,
                         date=date(2025, 4, 8),
                         startTime="9:00",
                         endTime="11:00")

    UM4 = upcomingMeeting(uid=3,
                         spid=S3.id,
                         date=date(2014, 9, 9),
                         startTime="12:45",
                         endTime="1:45")

    db.session.add_all([UM1, UM2, UM3, UM4])
    db.session.commit()

    return render_template('index.html', title="Home")
