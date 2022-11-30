import datetime
from datetime import date, time, datetime
from flask import render_template, flash, redirect, url_for
from app import app, db
from app.models import User, Location, Space, meetingHistory, upcomingMeeting, reviews, Tech, TechToSpace
from app.forms import LoginForm, RegistrationForm, FullSearch, Booking, ReviewForm
from flask_login import current_user, login_user, logout_user, login_required
from apscheduler.schedulers.background import BackgroundScheduler

def updateMeetings():
    with app.app_context():
        print('updating db')
        upcoming = upcomingMeeting.query.all()
        updated = []
        changes = False
        for meeting in upcoming:
            if meeting.date <= datetime.today().date():
                if meeting.startTime < datetime.now().time():
                    changes = True
                    prev = meetingHistory(uid=meeting.uid,
                                          spid=meeting.spid,
                                          date=meeting.date,
                                          startTime=meeting.startTime,
                                          endTime=meeting.endTime,
                                          review=False)
                    db.session.delete(meeting)
                    updated.append(prev)
        if changes:
            db.session.add_all(updated)
            db.session.commit()
            print("db changed")
        else:
            print("no changes")


@app.route('/')
@app.route('/home')
def home():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(updateMeetings, 'interval', minutes=1)
    sched.start()
    return render_template('home.html', title="Home")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('home'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    form.guest.choices = [(True, 'User'), (False, 'Host')]
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, name=form.fullName.data, guest=form.guest.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        login_user(user)
        return redirect(url_for('user', username=user.username))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    upcoming = upcomingMeeting.query.filter_by(uid=user.id)
    history = meetingHistory.query.filter_by(uid=user.id)
    uMeetings = []
    pMeetings = []
    for meet in upcoming:
        curr = {
            "space": Space.query.filter_by(id=meet.spid).first(),
            "location": Location.query.filter_by(id=Space.location).first(),
            "date": meet.date,
            "start": meet.startTime,
            "end": meet.endTime
        }
        uMeetings.append(curr)

    for meet in history:
        curr = {
            "space": Space.query.filter_by(id=meet.spid).first(),
            "location": Location.query.filter_by(id=Space.location).first(),
            "date": meet.date,
            "start": meet.startTime,
            "end": meet.endTime
        }
        pMeetings.append(curr)

    return render_template('user.html', user=user, meetings=uMeetings, history=pMeetings)


@app.route('/booking/<space>', methods=['GET', 'POST'])
@login_required
def book(space):
    space = Space.query.filter_by(name=space).first()
    tech = TechToSpace.query.filter_by(spid=space.id).all()
    techInSpace = []
    for t in tech:
        curr = {
            "tech": Tech.query.filter_by(id=t.tid).all(),
            "count": TechToSpace.query.filter_by(tid=t.tid, spid=space.id).all()
        }
        techInSpace.append(curr)
    form = Booking()
    form.space.data = space.name
    if form.validate_on_submit():
        flash("You've booked: {}".format(space.name))
        confirm = upcomingMeeting(uid=current_user.id, spid=space.id, date=form.date.data, startTime=form.startTime.data, endTime=form.endTime.data)
        db.session.add(confirm)
        db.session.commit()
        return redirect(url_for('user', username=current_user.username))
    return render_template('booking.html', title='Search', form=form, space=space, tech=techInSpace)


@app.route('/confirm', methods=['GET', 'POST'])
@login_required
def confirm():
    form = Booking()
    if form.validate_on_submit():

        confirmed = Booking(date=form.date.data,
                            space=form.space.data,
                            tech=form.tech.data,
                            groupSize=form.groupSize.data)
        db.session.add(confirmed)
        db.session.commit()
        return redirect(url_for('confirm', date=form.date.data,
                                space=form.space.data,
                                tech=form.tech.data,
                                groupSize=form.groupSize.data))
    return render_template('booking.html', form=form)


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = FullSearch()
    form.price.choices = [(True, 'Free'), (False, '$$$')]
    form.groupSize.data = 1
    technology = []
    for t in Tech.query.all():
        technology.append((t.id, t.name))
    form.tech.choices = technology

    if form.validate_on_submit():
        zip = form.zipcode.data
        date = form.date.data
        #sT = form.startTime.data
        eT = form.endTime.data
        tech = form.tech.data
        gSize = form.groupSize.data
        free = form.price.data

        if free == "True":
            if tech is None:
                s = db.session.query(Space).filter(Space.hourlyRate == 0, Space.sizeCap >= gSize) \
                    .join(Location).filter(Location.zip == zip) \
                    .join(upcomingMeeting).filter(eT <= upcomingMeeting.startTime, date == upcomingMeeting.date)
                s2 = db.session.query(Space).filter(Space.hourlyRate == 0, Space.sizeCap >= gSize) \
                    .join(Location).filter(Location.zip == zip) \
                    .join(upcomingMeeting).filter(date != upcomingMeeting.date)
                spaces = s.union(s2)
            else:
                s = db.session.query(Space).filter(Space.hourlyRate == 0, Space.sizeCap >= gSize) \
                .join(Location).filter(Location.zip == zip) \
                .join(TechToSpace).filter(Space.id == TechToSpace.spid, TechToSpace.tid.in_(tech))\
                .join(upcomingMeeting).filter(eT <= upcomingMeeting.startTime, date == upcomingMeeting.date)
                s2 = db.session.query(Space).filter(Space.hourlyRate == 0, Space.sizeCap >= gSize) \
                    .join(Location).filter(Location.zip == zip) \
                    .join(TechToSpace).filter(Space.id == TechToSpace.spid, TechToSpace.tid.in_(tech)) \
                    .join(upcomingMeeting).filter(date != upcomingMeeting.date)
                spaces = s.union(s2)
            return results(spaces)
        else:
            if tech is None:
                s = db.session.query(Space).filter(Space.hourlyRate >= 1, Space.sizeCap >= gSize) \
                    .join(Location).filter(Location.zip == zip) \
                    .join(upcomingMeeting).filter(eT <= upcomingMeeting.startTime, date == upcomingMeeting.date)
                s2 = db.session.query(Space).filter(Space.hourlyRate >= 1, Space.sizeCap >= gSize) \
                    .join(Location).filter(Location.zip == zip) \
                    .join(upcomingMeeting).filter(date != upcomingMeeting.date)
                spaces = s.union(s2)
            else:
                s = db.session.query(Space).filter(Space.hourlyRate >= 1, Space.sizeCap >= gSize) \
                    .join(Location).filter(Location.zip == zip) \
                    .join(TechToSpace).filter(Space.id == TechToSpace.spid, TechToSpace.tid.in_(tech))\
                    .join(upcomingMeeting).filter(eT <= upcomingMeeting.startTime, date == upcomingMeeting.date)
                s2 = db.session.query(Space).filter(Space.hourlyRate >= 1, Space.sizeCap >= gSize) \
                    .join(Location).filter(Location.zip == zip) \
                    .join(TechToSpace).filter(Space.id == TechToSpace.spid, TechToSpace.tid.in_(tech)) \
                    .join(upcomingMeeting).filter(date != upcomingMeeting.date)
                spaces = s.union(s2)
        return results(spaces)
    return render_template('search.html', title='Search', form=form)


@app.route("/search_results")
def results(spaces):
    return render_template("searchResults.html", title="Results", spaces=spaces)


@app.route('/space/<space>')
def space(space):
    space = Space.query.filter_by(name=space).first_or_404()
    location = Location.query.filter_by(id=space.location).first_or_404()
    r = reviews.query.filter_by(spid=space.id).all()
    tech = TechToSpace.query.filter_by(spid=space.id).all()
    techInSpace = []
    for t in tech:
        curr = {
            "tech": Tech.query.filter_by(id=t.tid).all(),
            "count": TechToSpace.query.filter_by(tid=t.tid, spid=space.id).all()
        }
        techInSpace.append(curr)

    return render_template('space.html', space=space, location=location, reviews=r, tech=techInSpace)


@app.route('/spaces')
def spaces():
    spaces = Space.query.all()
    locations = []
    for space in spaces:
        l = Location.query.filter_by(id=space.location).first_or_404()
        locations.append(l)
    return render_template('listings.html', spaces=spaces)

@app.route('/review/<space>/<date>/<time>', methods=['GET', 'POST'])
def review(space, date, time):
    form = ReviewForm()
    day = datetime.strptime(date, '%Y-%m-%d').date()
    st = datetime.strptime(time, '%H:%M:%S').time()
    meetSpace = Space.query.filter_by(name=space).first()
    meet = meetingHistory.query.filter_by(uid=current_user.id, spid=meetSpace.id, date=day, startTime=st, review=0).first()
    if form.validate_on_submit():
        flash("Thanks for your review!")
        r = reviews(uid=current_user.id, spid=meetSpace.id, score=form.score.data, desc=form.desc.data)
        meetingHistory.__setattr__(meet, 'review', 1)
        db.session.add(r)
        db.session.commit()
        return redirect(url_for('user', username=current_user.username))
    return render_template('review.html', title="Review", form=form, space=space, date=date, time=time)


def reset_db():
    flash("Resetting database: deleting old data and repopulating with dummy data")
    # clear all data from all tables
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        # print('Clear table {}'.format(table))
        db.session.execute(table.delete())
    db.session.commit()
    return render_template('home.html', title="Home")


@app.route('/populate_db')
def populate_db():
    reset_db()

    L1 = Location(name="Williams Hall",
                  city="Ithaca",
                  state="NY",
                  zip=14850,
                  lat=42.422758,
                  long=-76.495839
                  )
    L2 = Location(name="Friends Hall",
                  city="Ithaca",
                  state="NY",
                  zip=14850,
                  lat=42.422030,
                  long=-76.497014
                  )
    L3 = Location(name="CNS",
                  city="Ithaca",
                  state="NY",
                  zip=14850,
                  lat=42.423299,
                  long=-76.495559
                  )
    db.session.add_all([L1, L2, L3])
    db.session.commit()

    S1 = Space(name="Williams 320",
               sizeCap=25,
               hourlyRate=10,
               location=L1.id,
               description="Wonderful home of CS205! Here you can find"
                           "Doug Turnbull and many great devices."
               )
    S2 = Space(name="Williams 310",
               sizeCap=40,
               hourlyRate=15,
               location=L1.id,
               description="Classroom that features several computers."
               )
    S3 = Space(name="Friends 207",
               sizeCap=20,
               hourlyRate=8,
               location=L2.id,
               description="We're all friends here!"
               )
    S4 = Space(name="CNS 112",
               sizeCap=100,
               hourlyRate=0,
               location=L3.id,
               description="I LOVE SCIENCE. STEM!"
               )
    S5 = Space(name="CNS 200",
               sizeCap=15,
               hourlyRate=0,
               location=L3.id,
               description="Science Lab... why are you meeting here Mr. White?"
               )
    S6 = Space(name="CNS 321",
               sizeCap=8,
               hourlyRate=5,
               location=L3.id,
               description="A nice well, lit classroom."
               )
    db.session.add_all([S1, S2, S3, S4, S5, S6])
    db.session.commit()

    mh1date = date(2020, 10, 10)
    mh1STime = time(10, 30)
    mh1SEime = time(11, 30)

    mh2date = date(2021, 10, 10)
    mh2STime = time(10, 30)
    mh2SEime = time(11, 30)

    mh3date = date(2020, 9, 10)
    mh3STime = time(8, 00)
    mh3SEime = time(10, 00)

    mh4date = date(2019, 4, 8)
    mh4STime = time(12, 00)
    mh4SEime = time(13, 00)

    MH1 = meetingHistory(uid=1,
                         spid=S3.id,
                         date=mh1date,
                         startTime=mh1STime,
                         endTime=mh1SEime,
                         review=False)

    MH2 = meetingHistory(uid=1,
                         spid=S4.id,
                         date=mh2date,
                         startTime=mh2STime,
                         endTime=mh2SEime,
                         review=False)

    MH3 = meetingHistory(uid=2,
                         spid=S3.id,
                         date=mh3date,
                         startTime=mh3STime,
                         endTime=mh3SEime,
                         review=False)

    MH4 = meetingHistory(uid=3,
                         spid=S3.id,
                         date=mh4date,
                         startTime=mh4STime,
                         endTime=mh4SEime,
                         review=False)

    db.session.add_all([MH1, MH2, MH3, MH4])
    db.session.commit()

    um1date = date(2023, 10, 10)
    um1STime = time(10, 30)
    um1SEime = time(11, 30)

    um2date = date(2023, 11, 12)
    um2STime = time(10, 30)
    um2SEime = time(11, 30)

    um3date = date(2025, 4, 8)
    um3STime = time(9, 00)
    um3SEime = time(11, 00)

    um4date = date(2024, 9, 9)
    um4STime = time(12, 45)
    um4SEime = time(13, 45)

    UM1 = upcomingMeeting(uid=1,
                          spid=S3.id,
                          date=um1date,
                          startTime=um1STime,
                          endTime=um1SEime)

    UM2 = upcomingMeeting(uid=2,
                          spid=S4.id,
                          date=um2date,
                          startTime=um2STime,
                          endTime=um2SEime)

    UM3 = upcomingMeeting(uid=2,
                          spid=S3.id,
                          date=um3date,
                          startTime=um3STime,
                          endTime=um3SEime)

    UM4 = upcomingMeeting(uid=3,
                          spid=S3.id,
                          date=um4date,
                          startTime=um4STime,
                          endTime=um4SEime)

    db.session.add_all([UM1, UM2, UM3, UM4])
    db.session.commit()

    r1 = reviews(uid=1,
                 spid=S3.id,
                 score=4,
                 desc="Lovely, but smelled a little funny.")
    r2 = reviews(uid=1,
                 spid=S4.id,
                 score=5,
                 desc="Perfect! Just what I needed for my clown convention.")
    r3 = reviews(uid=2,
                 spid=S6.id,
                 score=4,
                 desc="Good")
    r4 = reviews(uid=2,
                 spid=S4.id,
                 score=2,
                 desc="There was a leak in the middle of the room.")

    db.session.add_all([r1, r2, r3, r4])
    db.session.commit()

    t1 = Tech(id=1, name="Projector")
    t2 = Tech(id=2, name="Wall Computers")
    t3 = Tech(id=3, name="Desks")
    t4 = Tech(id=4, name="Chairs")

    db.session.add_all([t1, t2, t3, t4])
    db.session.commit()

    TS1 = TechToSpace(tid=t1.id,
                      spid=S2.id,
                      count=1)

    TS2 = TechToSpace(tid=t2.id,
                      spid=S2.id,
                      count=8)

    TS3 = TechToSpace(tid=t3.id,
                      spid=S2.id,
                      count=10)

    TS4 = TechToSpace(tid=t4.id,
                      spid=S2.id,
                      count=20)

    TS5 = TechToSpace(tid=t3.id,
                      spid=S4.id,
                      count=25)

    TS6 = TechToSpace(tid=t4.id,
                      spid=S4.id,
                      count=50)

    TS7 = TechToSpace(tid=t1.id,
                      spid=S2.id,
                      count=1)

    TS8 = TechToSpace(tid=t4.id,
                      spid=S1.id,
                      count=20)

    TS9 = TechToSpace(tid=t1.id,
                      spid=S3.id,
                      count=1)

    TS10 = TechToSpace(tid=t2.id,
                       spid=S3.id,
                       count=5)

    TS11 = TechToSpace(tid=t4.id,
                       spid=S3.id,
                       count=10)

    TS12 = TechToSpace(tid=t1.id,
                       spid=S5.id,
                       count=2)

    TS13 = TechToSpace(tid=t3.id,
                       spid=S5.id,
                       count=3)

    TS14 = TechToSpace(tid=t4.id,
                       spid=S5.id,
                       count=6)

    TS15 = TechToSpace(tid=t1.id,
                       spid=S6.id,
                       count=1)

    TS16 = TechToSpace(tid=t4.id,
                       spid=S6.id,
                       count=8)

    db.session.add_all([TS1, TS2, TS3, TS4, TS5, TS6, TS7, TS8, TS9, TS10, TS11, TS12, TS13, TS14, TS15, TS16])
    db.session.commit()

    flash("Database populated")
    return render_template('home.html', title="Home")
