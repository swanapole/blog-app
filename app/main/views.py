from flask import render_template,request,redirect,url_for,abort
from . import main
from ..models import User,Blog,Comment, Subscriber
from .. import db,photos
from .forms import UpdateProfile,BlogForm,CommentForm, SubscriberForm
from flask_login import login_required,current_user
import datetime
from ..email import mail_message


@main.route('/')
def index():
    cuisine = Blog.get_blogs('cuisine')
    voyage = Blog.get_blogs('voyage')
    health = Blog.get_blogs('health')
    empower = Blog.get_blogs('empower')

    return render_template('index.html', title = 'BumbleBee - Home', cuisine = cuisine, voyage = voyage, health = health, empower = empower)

@main.route('/blogs/cuisine')
def cuisine():
    blogs = Blog.get_blogs('cuisine')

    return render_template('cuisine.html',blogs = blogs)


@main.route('/blogs/voyage')
def voyage():
    blogs = Blog.get_blogs('voyage')

    return render_template('voyage.html',blogs = blogs)


@main.route('/blogs/health')
def health():
    blogs = Blog.get_blogs('health')

    return render_template('health.html',blogs = blogs)


@main.route('/blogs/empower')
def empower():
    blogs = Blog.get_blogs('empower')

    return render_template('empower.html',blogs = blogs)


@main.route('/user/<uname>')
def profile(uname):
    user = User.query.filter_by(username = uname).first()

    if user is None:
        abort(404)

    return render_template('profile/profile.html',user = user)


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


@main.route('/blog/new', methods = ['GET','POST'])
@login_required
def new_blog():
    legend = 'New Blog'
    form = BlogForm()
    if form.validate_on_submit():
        title = form.title.data
        blog = form.text.data
        category = form.category.data

        new_blog = Blog(blog_title = title,blog_content = blog, category = category,user = current_user)
        new_blog.save_blog()

        subscriber = Subscriber.query.all()
        for email in subscriber:
            mail_message("New Blog Post from BumbleBee! ","email/postnotification",email.email,subscriber=subscriber)
        return redirect(url_for('main.index'))

    title = 'New Blog'
    return render_template('new_blog.html', legend = legend, title = title, blog_form = form)

@main.route('/blog/delete/<int:id>', methods = ['GET', 'POST'])
@login_required
def delete_blog(id):
    blog = Blog.get_blog(id)
    db.session.delete(blog)
    db.session.commit()

    return render_template('blogs.html', id=id, blog = blog)

@main.route('/blog/<int:id>', methods = ["GET","POST"])
def blog(id):
    blog = Blog.get_blog(id)
    posted_date = blog.posted.strftime('%b %d, %Y')

    form = CommentForm()
    if form.validate_on_submit():
        comment = form.text.data
        name = form.name.data

        new_comment = Comment(comment = comment, name = name, blog_id = blog)

        new_comment.save_comment()

    comments = Comment.get_comments(blog)

    return render_template('blog.html', blog = blog, comment_form = form,comments = comments, date = posted_date)

@main.route('/user/<uname>/blogs', methods = ['GET','POST'])
def user_blogs(uname):
    user = User.query.filter_by(username = uname).first()
    blogs = Blog.query.filter_by(user_id = user.id).all()

    return render_template('profile/blogs.html', user = user, blogs = blogs)

@main.route('/blogs/recent', methods = ['GET','POST'])
def blogs():
    blogs = Blog.query.order_by(Blog.id.desc()).limit(5)

    return render_template('blogs.html',blogs = blogs)


@main.route('/subscribe', methods=['GET','POST'])
def subscriber():
    subscriber_form=SubscriberForm()
    blogs = Blog.query.order_by(Blog.posted.desc()).all()

    if subscriber_form.validate_on_submit():
        subscriber= Subscriber(email=subscriber_form.email.data,name = subscriber_form.name.data)

        db.session.add(subscriber)
        db.session.commit()

        mail_message("Welcome to BumbleBee","email/welcome_subscriber",subscriber.email,subscriber=subscriber)

        title= "BumbleBee"
        return render_template('index.html',title=title, blogs=blogs)

    subscriber = Blog.query.all()

    blogs = Blog.query.all()


    return render_template('subscribe.html',subscriber=subscriber,subscriber_form=subscriber_form,blog=blog)


@main.route('/comment/delete/<int:blog>', methods=['GET', 'POST'])
@login_required
def delete_comment(blog):
    blog = Blog.query.filter_by(id=blog).first()
    comment = Comment.query.filter_by(blog = blog).first()

    db.session.delete(comment)
    db.session.commit()

    return redirect(url_for('main.blog', comment=comment, blog=blog))

@main.route('/blog/<int:id>/update', methods = ['GET','POST'])
@login_required
def update_blog(id):
    legend = 'Update Blog'
    blog = Blog.get_blog(id)
    form = BlogForm()
    if form.validate_on_submit():
        blog.blog_title = form.title.data
        blog.blog_content = form.text.data
        blog.category = form.category.data
        db.session.commit()
        return redirect(url_for('main.blog', id = id))
    elif request.method == 'GET':
        form.title.data = blog.blog_title
        form.text.data = blog.blog_content
    form.category.data = blog.category
    return render_template('new_blog.html', legend = legend, blog_form = form, id=id)
