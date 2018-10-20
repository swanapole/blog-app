from flask import render_template,request,redirect,url_for,abort
from . import main
from ..models import User,Pitch,Comment, Subscriber
from .. import db,photos
from .forms import UpdateProfile,PitchForm,CommentForm, SubscriberForm
from flask_login import login_required,current_user
import datetime
from ..email import mail_message


user = [
    {
        'email':'admin@blog.com',
        'password':'admin098'
    }
]

@main.route('/')
def index():
    cuisine = Pitch.get_pitches('cuisine')
    voyage = Pitch.get_pitches('voyage')
    health = Pitch.get_pitches('health')
    empower = Pitch.get_pitches('empower')

    return render_template('index.html', title = 'Pitch App - Home', cuisine = cuisine, voyage = voyage, health = health, empower = empower)

@main.route('/pitches/cuisine')
def cuisine():
    pitches = Pitch.get_pitches('cuisine')

    return render_template('cuisine.html',pitches = pitches)


@main.route('/pitches/voyage')
def voyage():
    pitches = Pitch.get_pitches('voyage')

    return render_template('voyage.html',pitches = pitches)


@main.route('/pitches/health')
def health():
    pitches = Pitch.get_pitches('health')

    return render_template('health.html',pitches = pitches)


@main.route('/pitches/empower')
def empower():
    pitches = Pitch.get_pitches('empower')

    return render_template('empower.html',pitches = pitches)


@main.route('/user/<uname>')
def profile(uname):
    user = User.query.filter_by(username = uname).first()
    pitch_count = Pitch.count_pitches(uname)

    if user is None:
        abort(404)

    return render_template('profile/profile.html',user = user, pitches = pitch_count)


@main.route('/user/<uname>/update', methods = ['GET','POST'])
@login_required
def update_profile(uname):
    user = User.query.filter_by(username = uname).first()
    if user is None:
        abort(404)

    form = UpdateProfile()

    if form.validate_on_submit():
        user.bio = form.bio.data
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('.profile',uname = user.username))

    return render_template('profile/update.html', form = form)


@main.route('/user/<uname>/update/pic', methods = ['POST'])
def update_pic(uname):
    user = User.query.filter_by(username = uname).first()
    if 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        path = f'photos/{filename}'
        user.profile_pic_path = path
        db.session.commit()

    return redirect(url_for('main.profile', uname = uname))


@main.route('/pitch/new', methods = ['GET','POST'])
@login_required
def new_pitch():
    legend = 'New Blog'
    form = PitchForm()
    if form.validate_on_submit():
        title = form.title.data
        pitch = form.text.data
        category = form.category.data

        new_pitch = Pitch(pitch_title = title,pitch_content = pitch, category = category,user = current_user)
        new_pitch.save_pitch()

        subscriber = Subscriber.query.all()
        for email in subscriber:
            mail_message("New Blog Post from BumbleBee! ","email/postnotification",email.email,subscriber=subscriber)
        return redirect(url_for('main.index'))

    title = 'New Pitch'
    return render_template('new_pitch.html', legend = legend, title = title, pitch_form = form)

@main.route('/pitch/delete/<int:id>', methods = ['GET', 'POST'])
@login_required
def delete_pitch(id):
    pitch = Pitch.get_pitch(id)
    db.session.delete(pitch)
    db.session.commit()

    return render_template('pitches.html', id=id, pitch = pitch)

@main.route('/pitch/<int:id>', methods = ["GET","POST"])
def pitch(id):
    pitch = Pitch.get_pitch(id)
    posted_date = pitch.posted.strftime('%b %d, %Y')

    form = CommentForm()
    if form.validate_on_submit():
        comment = form.text.data
        name = form.name.data

        new_comment = Comment(comment = comment, name = name, pitch_id = pitch)

        new_comment.save_comment()

    comments = Comment.get_comments(pitch)

    return render_template('pitch.html', pitch = pitch, comment_form = form,comments = comments, date = posted_date)

@main.route('/user/<uname>/pitches', methods = ['GET','POST'])
def user_pitches(uname):
    user = User.query.filter_by(username = uname).first()
    pitches = Pitch.query.filter_by(user_id = user.id).all()
    pitch_count = Pitch.count_pitches(uname)

    return render_template('profile/pitches.html', user = user, pitches = pitches, pitches_count = pitch_count)

@main.route('/pitches/recent', methods = ['GET','POST'])
def pitches():
    pitches = Pitch.query.order_by(Pitch.id.desc()).limit(5)

    return render_template('pitches.html',pitches = pitches)


@main.route('/subscribe', methods=['GET','POST'])
def subscriber():
    subscriber_form=SubscriberForm()
    pitches = Pitch.query.order_by(Pitch.posted.desc()).all()

    if subscriber_form.validate_on_submit():
        subscriber= Subscriber(email=subscriber_form.email.data,name = subscriber_form.name.data)

        db.session.add(subscriber)
        db.session.commit()

        mail_message("Welcome to BumbleBee","email/welcome_subscriber",subscriber.email,subscriber=subscriber)

        title= "BumbleBee"
        return render_template('index.html',title=title, pitches=pitches)

    subscriber = Pitch.query.all()

    pitches = Pitch.query.all()


    return render_template('subscribe.html',subscriber=subscriber,subscriber_form=subscriber_form,pitch=pitch)


@main.route('/comment/delete/<int:pitch>', methods=['GET', 'POST'])
@login_required
def delete_comment(pitch):
    pitch = Pitch.query.filter_by(id=pitch).first()
    comment = Comment.query.filter_by(pitch = pitch).first()

    db.session.delete(comment)
    db.session.commit()

    return redirect(url_for('main.pitch', comment=comment, pitch=pitch))

@main.route('/pitch/<int:id>/update', methods = ['GET','POST'])
@login_required
def update_blog(id):
    legend = 'Update Blog'
    pitch = Pitch.get_pitch(id)
    form = PitchForm()
    if form.validate_on_submit():
        pitch.pitch_title = form.title.data
        pitch.pitch_content = form.text.data
        pitch.category = form.category.data
        db.session.commit()
        return redirect(url_for('main.pitch', id = id))
    elif request.method == 'GET':
        form.title.data = pitch.pitch_title
        form.text.data = pitch.pitch_content
    form.category.data = pitch.category
    return render_template('new_pitch.html', legend = legend, pitch_form = form, id=id)
