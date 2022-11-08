from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


# IMPLEMENT LOGIN, PASSWORD_HASHING
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    password_hash = db.Column(db.String(64))
    name = db.Column(db.String(64))
    guest = db.Column(db.Boolean)

    def __repr__(self):
        return '<User> {}'.format(self.name)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    city = db.Column(db.String(64), index=True)
    state = db.Column(db.String(64), index=True)
    zip = db.Column(db.Integer)

    def __repr__(self):
        return '<Location> {}'.format(self.name)


# CONSTRAINTS:
# HOURLYRATE >= 0
class Space(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    sizeCap = db.Column(db.Integer, index=True)
    hourlyRate = db.Column(db.Integer, index=True)
    location = db.Column(db.Integer, db.ForeignKey('location.id'), index=True)

    def __repr__(self):
        return '<Location> {}'.format(self.name)


# CONSTRAINTS:
# START_TIME > END_TIME
class meetingHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    spid = db.Column(db.Integer, db.ForeignKey('space.id'), index=True)
    date = db.Column(db.Date())
    startTime = db.Column(db.Time())
    endTime = db.Column(db.Time())

    def __repr__(self):
        return '<meeting> {}'.format(self.spid + " on "
                                     + self.date + " starting at"
                                     + self.startTime)


# CONSTRAINTS:
# START_TIME > END_TIME
class upcomingMeeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    spid = db.Column(db.Integer, db.ForeignKey('space.id'), index=True)
    date = db.Column(db.Date())
    startTime = db.Column(db.Time())
    endTime = db.Column(db.Time())

    def __repr__(self):
        return '<meeting> {}'.format(self.spid + " on "
                                     + self.date + " starting at"
                                     + self.startTime)


# CONSTRAINTS:
# SCORE >= 1
class reviews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'))
    spid = db.Column(db.Integer, db.ForeignKey('space.id'))
    score = db.Column(db.Integer)

    def __repr__(self):
        return '<review> {}'.format(self.uid + " rated "
                                    + self.spid + " "
                                    + self.score)


class Tech(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(64), index=True)

    def __repr__(self):
        return '<tech> {}'.format(self.name)


# CONSTRAINTS:
# count >= 1
class TechToSpace(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    tid = db.Column(db.Integer, db.ForeignKey('tech.id'))
    spid = db.Column(db.Integer, db.ForeignKey('space.id'))
    count = db.Column(db.Integer)
