from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "45Q@3DS*wo64Uzae%98hmargh"
app.permanent_session_lifetime = timedelta(minutes=5)


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        current_usr = request.form['nm']
        session['user'] = current_usr

        return redirect(url_for("user"))
    else:
        return render_template('login.html')


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash('You were logged out...', "info")
    return redirect(url_for("login"))


@app.route("/user")
def user():
    if "user" in session:
        usr = session["user"]
        return f"<h1>{usr}</h1>"
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
