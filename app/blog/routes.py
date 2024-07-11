from blog import app, db, bcrypt, fake
from flask import render_template, redirect, url_for, flash, request, abort
from blog.forms import RegistrationForm, LoginForm, UpdateProfileForm, PostForm
from blog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
import random


@app.route("/")
def home():
    page = request.args.get("page", 1, type=int)  # Default to page 1 if not specified
    posts = Post.query.paginate(page=page, per_page=10, error_out=False)
    return render_template("home.html", posts=posts)


@app.route("/post/<int:post_id>")
def detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("detail.html", post=post)


@app.route("/register", methods=["post", "get"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(
            username=form.username.data, email=form.email.data, password=hashed_pass
        )
        db.session.add(user)
        db.session.commit()
        flash("you registered successfully", "success")
        return redirect(url_for("home"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["post", "get"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next", None)

            flash("you logged in seccessfully", "success")
            return redirect(next_page if next_page else url_for("home"))
        else:
            flash("Email or Password is wrong", "danger")
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("you logged out seccessfully", "success")
    return redirect(url_for("home"))


@app.route("/profile", methods=["post", "get"])
@login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("account updated", "info")
        return redirect(url_for("profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template("profile.html", form=form)


@app.route("/post/new", methods=["post", "get"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data, content=form.content.data, author=current_user
        )
        db.session.add(post)
        db.session.commit()
        flash("post created", "success")
        return redirect(url_for("home"))
    return render_template("create_post.html", form=form)


@app.route("/post/<int:post_id>/delete", methods=["post", "get"])
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("post deleted", "info")
    return redirect(url_for("home"))


@app.route("/post/<int:post_id>/update", methods=["post", "get"])
@login_required
def update(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("post updated", "info")
        return redirect(url_for("detail", post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template("update.html", form=form)


def create_fake_data():

    with app.app_context():
        users = User.query.all()
        if not Post.query.first():
            for _ in range(40):  # Adjust the number of posts as you wish
                post = Post(
                    title=fake.sentence(),
                    content=fake.text(),
                    author=random.choice(users),
                )
                db.session.add(post)
            db.session.commit()
            print("Added 100 fake posts.")


create_fake_data()
