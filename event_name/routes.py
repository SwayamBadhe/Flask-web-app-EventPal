import secrets
import os
from PIL import Image
from flask import redirect, render_template, flash, url_for, request, abort
from event_name import app, db, bcrypt, mail
from event_name.forms import RegistrationForm_User, LoginForm_User, UpdateAccountForm_User, EventForm, SearchBarForm
from event_name.models import User, Event, Enrollment
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from sqlalchemy import or_
# from event_name.utils import login_required

@app.route("/")
def base():
    return render_template('base.html')

@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    events = Event.query.order_by(Event.date_posted.desc()).paginate(page=page, per_page=5)
    if current_user:
        user = current_user
    
    return render_template('home.html', events=events, user=user)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


# User Forms

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm_User()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('You have been logged in!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
            
    return render_template('login.html', title='Login', form=form)

# check role and assign
def roleCheck(form):
    if form.is_organizer.data == 'user':
        role = 'user'
    else:  
        role = 'organizer'
    return role
    

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm_User()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        role = roleCheck(form)
        user = User(username=form.username.data, email=form.email.data
                    ,password=hashed_password, is_organizer=form.is_organizer.data
                    ,role=role)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm_User()

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email 

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form, user=current_user)



# -----------------------------------------------------------------------------------------------------------
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))



def save_event_picture(form_picture):
    if not form_picture:
        return None
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/event_pics', picture_fn)

    output_size = (600, 400)  # adjust the size to fit col-md-6
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn
    
@app.route("/event/new", methods=['GET', 'POST'])
@login_required
def new_event():
    if (not current_user.is_authenticated) or (current_user.is_organizer == 'user') :
        abort(403)
    form = EventForm()

    if form.validate_on_submit():
        picture_file = save_event_picture(form.picture.data)
        event = Event(title=form.title.data, description=form.description.data,
                       image_file=picture_file, organizer_id=current_user.id,
                       date_of_event=form.date_of_event.data)
        db.session.add(event)
        db.session.commit()
        flash('Your event has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_event.html', title='New Event', form=form, legend='New Event')

@app.route("/event/<int:event_id>")
def event(event_id):
    event = Event.query.get_or_404(event_id)
    if current_user:
        user = current_user
    return render_template('event.html', title=event.title, event=event, user=user)


@app.route("/event/<int:event_id>/update", methods=['GET', 'POST'])
@login_required
def update_event(event_id):
    if (not current_user.is_authenticated) or (current_user.is_organizer == 'user') :
        abort(403)
    event = Event.query.get_or_404(event_id)
    if event.author != current_user:
        abort(403)
    form = EventForm()
    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        db.session.commit()
        flash('Your event has been updated!', 'success')
        return redirect(url_for('event', event_id=event.id))
    elif request.method == 'GET':
        form.title.data = event.title
        form.description.data = event.description
    return render_template('create_event.html', title='Update event', form=form, legend='Update event')

@app.route("/event/<int:event_id>/delete", methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.author != current_user:
        abort(403)
    db.session.delete(event)
    db.session.commit()
    flash('Your event has been deleted!', 'success')
    return redirect(url_for('home'))

# Enroll --------------------------------------------------------------------------------

@app.route("/enrollment/<int:user_id>/<int:event_id>")
@login_required
def enroll(user_id, event_id):
    event = Event.query.get(event_id)
    user = User.query.get(user_id)
  
    if (Enrollment.query.filter_by(user_id=user_id, event_id=event_id).count() == 1):
        flash("You have already enrolled in this event!", "info")
        return redirect(url_for('home'))

    enrollment = Enrollment(user_id=user.id, event_id=event.id) 
    db.session.add(enrollment)
    db.session.commit()
    flash("You have successfully enrolled in this event!", "success")

    msg = Message(f'You are enrolled in { event.title }', sender="swayambadhe252@gmail.com", recipients=[user.email])
    
    msg.html = render_template("email.html", user=user, event=event, category='enroll')

    mail.send(msg)
    return render_template('enrollment.html', title='Enroll', user=user, event=event)

@app.route("/user/<string:username>")
def org_events(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    events = Event.query.filter_by(author=user).order_by(Event.date_posted.desc()).paginate(page=page, per_page=3)
    event_O = Event.query.filter_by(author=user).first()

    if current_user:
        user = current_user
    
    return render_template('org_events.html', events=events, user=user, event_O=event_O)

@app.route("/event_status")
@login_required
def event_status():
    if (not current_user.is_authenticated) or (current_user.is_organizer == 'user') :
        abort(403)

    cid = current_user.id
    events = Event.query.filter_by(organizer_id=cid).all()

    return render_template('event_status.html', title='Event Status', events=events)

@app.route("/event_info/<int:event_id>")
@login_required
def event_info(event_id):
    if (not current_user.is_authenticated) or (current_user.is_organizer == 'user') :
        abort(403)
    event = Event.query.get_or_404(event_id)
    if event.author != current_user:
        abort(403)

    all_enrolled = Enrollment.query.filter_by(event_id=event_id).all()    

    return render_template('event_info.html', title='Event Information', event=event, all_enrolled=all_enrolled)

@app.route("/enrolled_events/<int:user_id>")
@login_required
def enrolled_events(user_id):
    if (not current_user.is_authenticated) or (current_user.is_organizer == 'organizer') :
        abort(403)
    user = User.query.get_or_404(user_id)
    if user != current_user:
        abort(403)

    my_enrolled = Enrollment.query.filter_by(user_id=user_id).all()  

    return render_template('enrolled_events.html', title='Enrolled Events', my_enrolled=my_enrolled)

@app.route("/enrolled_events/<int:user_id>/delete", methods=['POST'])
@login_required
def unenroll(user_id):
    if (not current_user.is_authenticated) or (current_user.is_organizer == 'organizer') :
        abort(403)
    user = User.query.get_or_404(user_id)
    if user != current_user:
        abort(403)

    enrolled = Enrollment.query.filter_by(user_id=user_id).first()

    msg = Message(f'You are unenrolled from { enrolled.event.title }', sender="swayambadhe252@gmail.com", recipients=[user.email])    
    msg.html = render_template("email.html", user=user, event=enrolled.event, category='unenroll')
    mail.send(msg)
    
    db.session.delete(enrolled)
    db.session.commit()
    flash('You have been enenrolled from the event', 'info')
    return redirect(url_for('home'))


@app.route("/search", methods=['GET', 'POST'])
@login_required
def search():
    form = SearchBarForm()
    events = None
    if form.validate_on_submit():
        keyword = form.content.data
        events = Event.query.filter(or_(Event.title.like(f'%{keyword}%'), Event.description.like(f'%{keyword}%')))\
                  .order_by(Event.date_posted.desc())
    return render_template('search.html', events=events, user=current_user, form=form) if events else render_template('search.html', user=current_user, form=form)

@app.route("/customer_care")
def customer_care():
    return render_template('customer_care.html')

