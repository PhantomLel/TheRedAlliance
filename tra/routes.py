from re import L
from tra import db, app
from tra.models import ScoutResponse, Scout, Admin
from flask import redirect, request, session, render_template, flash, escape, url_for, abort


@app.route("/")
@app.route("/home")
def home():
    if "name" not in session:
        return redirect(url_for("login"))
    # if the user is not logged in, then redirect back to login
    scout = Scout.query.filter_by(name=session["name"]).first()
    if scout is None:
        return redirect(url_for("login"))
    return render_template("home.html", scout=scout)

# this route handles login for scouts
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if "name" not in request.form or "code" not in request.form:
            abort(400)
        # Add the user's name to the session
        scout = Scout.query.filter_by(name=request.form["name"]).first()
        # make sure a user exists with that name
        if scout is not None:
            # check code
            if request.form["code"] == scout.code:
                # add username to session
                session["name"] = escape(request.form["name"])
                return redirect(url_for("home"))

        flash("Invalid Scout Credentials", "is-danger")
        if len(request.form["name"].split()) < 2:   
            flash("Maybe you forgot to put your last name?", category="is-warning")

    return render_template("login.html")

# handle admin login and setup
@app.route("/login/admin", methods=["GET", "POST"])
def admin_login():
    admin = Admin.query.all()
    if request.method == "POST":
        if "username" not in request.form or "password" not in request.form:
            abort(400)

        # dont allow usernames longer than 20 characters
        if len("username") > 20:
            flash(f"Username cannot be more than 20 characters. Your username is {len(request.form['username'])} characters long")
            return redirect(url_for('admin_login'))

        # admin account still needs to be set
        if len(admin) == 0:
            new_admin = Admin(escape(request.form["username"]), request.form["password"])
            db.session.add(new_admin)
            db.session.commit()
            flash(f"Admin account {new_admin.username} created")
            return redirect(url_for("admin"))

        # admin has already been created
       # select the admin account 
        admin = admin[0]
        # admin account has already been created. check creds
        if request.form["username"] == admin.username \
            and request.form["password"] == admin.password:
            session["admin"] = admin.key
            return redirect(url_for("admin"))

    if len(admin) == 0:
        # if no admin exists, then show the admin setup page
        flash("Looks like a scouting admin needs to be setup. Please set up an account here to begin managing scouts", category="is-primary")
        return render_template("admin_setup.html")

    # otherwise show normal login page
    return render_template("admin_login.html")

# main admin page and panel
@app.route("/admin")
def admin():
    admin = Admin.query.all()
    # admin hasnt been set yet
    if len(admin) == 0:
        return redirect(url_for("admin_login"))
    
    admin = admin[0]
    if "admin" in session:
        if session["admin"] != admin.key:
            abort(403)
    return render_template("admin.html", admin=admin)


# This route is for testing writing to sql database
@app.route("/test", methods=["POST", "GET"])  # specify methods and route
def test():
    if request.method == "POST":
        session.permanent = True  # set permanent session
        form_data = request.form["scout_data"]

        # found_user = users.query.filter_by(name=user).first() #what_to_access.perform_a_query.find_all_that_meet_criteria.grab_first_result    This is how to find a user
        usr_data = ScoutResponse(form_data)
        db.session.add(usr_data)
        db.session.commit()
        for i in UserData.query.all(): 
            print(i.data)

        flash("Data recieved!", "info")

    return render_template("scouting.html")
