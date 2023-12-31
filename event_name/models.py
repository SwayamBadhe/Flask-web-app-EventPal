from datetime import datetime
from event_name import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(200))
    email = db.Column(db.String(256), unique=True)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    role = db.Column(db.String(80))
    is_organizer = db.Column(db.String, default='user')
    events = db.relationship('Event', backref='author', lazy=True)
    enrollments = db.relationship('Enrollment', backref='user', lazy=True)

    def enrolled_events(self, user):
        return Enrollment.query.filter_by(user_id=user.id).count()
    
    def get_role(self):
            return self.role

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.role}', '{self.is_organizer}')"


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_of_event = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    enrollments = db.relationship('Enrollment', backref='event', lazy=True)

    def __repr__(self):
        return f"Event('{self.title}', '{self.date_posted}', '{self.image_file}')"


class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

    def enrollment_count(self, event):
        return Enrollment.query.filter_by(event_id=event.id).count()

    def __repr__(self):
        return f"Enrollment('{self.user_id}', '{self.event_id}')"
    

