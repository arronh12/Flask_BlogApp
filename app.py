from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db = SQLAlchemy(app)

app.secret_key = "45Q@3DS*wo64Uzae%98hmargh"
app.permanent_session_lifetime = timedelta(minutes=5)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

    def __init__(self, name, email):
        self.name = name
        self.email = email


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        current_usr = request.form['nm']
        session['user'] = current_usr

        found_usr = db.session.query(User).filter_by(name=current_usr).first()

        if found_usr:
            session['email'] = found_usr.email
        else:
            usr = User(current_usr, "")
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


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
