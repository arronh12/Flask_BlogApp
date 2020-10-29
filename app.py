from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from datetime import date, datetime
from passlib.hash import sha256_crypt


app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = '45Q@3DS*wo64Uzae%98hmargh'

db = SQLAlchemy(app)

app.secret_key = "45Q@3DS*wo64Uzae%98hmargh"
app.permanent_session_lifetime = timedelta(minutes=5)


#-----------------------------------------------------------------------------------------
# db models
#-----------------------------------------------------------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(300))
    posts = db.relationship('Post', backref='user', lazy='dynamic')

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    def __repr__(self):
        return self.name


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now())
    post_title = db.Column(db.String(100))
    post_content = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


#------------------------------------------------------------------------------------------


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        current_usr = request.form['login_name']
        current_pw = request.form['login_pw']

        hashed_pw = sha256_crypt.encrypt(current_pw)

        session['user'] = current_usr
        print("User:" + current_usr + ", Password:" + current_pw)

        found_usr = db.session.query(User).filter_by(name=current_usr).first()

        if found_usr:
            session['email'] = found_usr.email
        else:
            usr = User(current_usr, "", hashed_pw)
            db.session.add(usr)
            db.session.commit()

        flash("Login successful!...")
        return redirect(url_for("user"))
    else:
        if "user" in session:
            flash("Already logged in!...")
            return redirect(url_for("user"))

        return render_template('login.html')


@app.route("/logout")
def logout():
    if 'user' in session:
        usr = session['user']
        flash(f"You were logged out, {usr}", "info")
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))


@app.route("/reg_user", methods=["POST", "GET"])
def reg_user():
    if request.method == "POST":
        usr_name = request.form['reg_name']
        usr_email = request.form['reg_email']
        pw_1 = request.form['reg_pw_1']
        pw_2 = request.form['reg_pw_2']

        if pw_1 == pw_2:
            hashed_pw = sha256_crypt.encrypt(pw_1)
            make_usr = User(name=usr_name, email=usr_email, password=hashed_pw)
            db.session.add(make_usr)
            db.session.commit()
            session['user'] = usr_name
            session['email'] = usr_email
            flash("You are registered successfully....")
            return redirect(url_for("user"))
        else:
            flash("Your passwords do not match!....")
            return redirect(url_for("reg_user"))
    else:
        if "user" in session:
            flash("Already logged in!....")
            return redirect(url_for("user"))

        return render_template("reg_user.html")


@app.route("/friends")
def friends():
    return render_template("friends.html", values=User.query.all())


@app.route("/view_friend/<selected_id>")
def view_friend(selected_id):
    i = db.session.query(User).filter_by(id=selected_id).first()
    return render_template("selectedfriend.html", value=i)


@app.route("/user", methods=["POST", "GET"])
def user():
    email = None
    if "user" in session:
        current_usr = session["user"]

        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            found_usr = db.session.query(User).filter_by(name=current_usr).first()
            found_usr.email = email
            db.session.commit()
            flash("Email was saved!...")
        else:
            if "email" in session:
                email = session["email"]

        return render_template('user.html', email=email)
    else:
        flash("You are not logged in!...")
        return redirect(url_for('login'))


@app.route("/posts")
def posts():
    if "user" in session:
        current_usr = session["user"]
        found_usr = db.session.query(User).filter_by(name=current_usr).first()
        all_posts = db.session.query(Post).filter_by(user_id=found_usr.id)
        return render_template("posts.html", values=all_posts)
    else:
        flash("you are not logged in...")
        return render_template("posts.html")


@app.route("/make_post", methods=["POST", "GET"])
def make_post():
    if request.method == "POST":
        p_title = request.form['postTitleInput']
        p_content = request.form['postContentInput']
        usr = db.session.query(User).filter_by(name=session['user']).first()
        made_post = Post(post_title=p_title, post_content=p_content, user_id=usr.id)
        db.session.add(made_post)
        db.session.commit()
        return redirect(url_for("posts"))
    else:
        return render_template('make_post.html')


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
