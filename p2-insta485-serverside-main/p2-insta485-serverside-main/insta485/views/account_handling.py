"""Insta485 account login view."""
import insta485
import flask
import hashlib
import uuid
import os
import pathlib

insta485.app.secret_key = b"\xbe\xfa\xaf\xd1\xbc[&\\\x03?' \xc2\x82a\x0e"


def save_file(fileobj, filename):
    """Save files to system."""
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix.lower()
    uuid_basename = f"{stem}{suffix}"
    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    fileobj.save(path)

    return uuid_basename


@insta485.app.route("/accounts/auth/", methods=["GET"])
def is_logged_in():
    """Check if a given user is logged in."""
    if "logname" in flask.session:
        return flask.Response(status=200)
    else:
        return flask.abort(403)


@insta485.app.route("/accounts/login/", methods=["GET"])
def login_user():
    """Display login page."""
    if "logname" in flask.session:
        return flask.redirect(flask.url_for("show_index"))

    context = {}
    return flask.render_template("account_login.html", **context)


@insta485.app.route("/accounts/logout/", methods=["POST"])
def logout_user():
    """Log out a given user."""
    flask.session.clear()
    return flask.redirect(flask.url_for("login_user"))


@insta485.app.route("/accounts/create/", methods=["GET"])
def display_create_account_page():
    """Displayaccount creation page."""
    if "logname" in flask.session:
        return flask.redirect(flask.url_for("display_edit_account_form"))

    context = {}
    return flask.render_template("account_creation.html", **context)


@insta485.app.route("/accounts/delete/", methods=["GET"])
def display_delete_account_form():
    """Display account deletion page."""
    if "logname" not in flask.session:
        return flask.redirect(flask.url_for("login_user"))

    logname = flask.session["logname"]
    context = {"logname": logname}
    return flask.render_template("delete_account.html", **context)


@insta485.app.route("/accounts/edit/", methods=["GET"])
def display_edit_account_form():
    """Display account edit page."""
    if "logname" not in flask.session:
        return flask.redirect(flask.url_for("login_user"))

    connection = insta485.model.get_db()
    user_data = connection.execute(
        "SELECT fullname, email, filename FROM users WHERE username = ?",
        (flask.session["logname"],)).fetchone()
    context = {"logname": flask.session["logname"],
               "fullname": user_data["fullname"], "email": user_data["email"],
               "filename": user_data["filename"]}
    return flask.render_template("account_edit.html", **context)


@insta485.app.route("/accounts/password/", methods=["GET"])
def display_change_password():
    """Display change password page."""
    if "logname" not in flask.session:
        return flask.redirect(flask.url_for("login_user"))

    context = {"logname": flask.session["logname"]}
    return flask.render_template("change_password.html", **context)


@insta485.app.route("/accounts/", methods=["POST"])
def handle_account_operations():
    """Handle account operations."""
    connection = insta485.model.get_db()
    operation = flask.request.form.get("operation")
    target = flask.request.args.get("target")

    if operation == "login":
        if "logname" in flask.session:
            return flask.redirect(flask.url_for("show_index"))

        username = flask.request.form.get("username")
        password = flask.request.form.get("password")
        password_data = connection.execute(
            "SELECT password from users WHERE username = ?",
            (username,)).fetchone()

        if username == "" or password == "":
            return flask.abort(400)

        if password_data is not None:
            data = []
            for key, value in password_data.items():
                data.append(value)

            data = data[0].split("$")
            algorithm = data[0]
            salt = data[1]
            hash_object = hashlib.new(algorithm)
            salted_password = salt + password
            hash_object.update(salted_password.encode('utf-8'))
            password_hash = hash_object.hexdigest()
            password_db_string = "$".join([algorithm, salt, password_hash])

            match = connection.execute(
                "SELECT username, password FROM users"
                " WHERE username = ? AND password = ?",
                (username, password_db_string)).fetchone()

            if match is None:
                return flask.abort(403)
            else:
                flask.session["logname"] = username

                if target is None or target == "":
                    return flask.redirect(flask.url_for("show_index"))

                else:
                    # return flask.redirect(flask.url_for("show_index"))
                    return flask.redirect(target)

        else:
            return flask.abort(403)

    elif operation == "create":
        if "logname" in flask.session:
            return flask.redirect(flask.url_for("display_edit_account_form"))

        username = flask.request.form.get("username")
        password = flask.request.form.get("password")
        email = flask.request.form.get("email")
        fullname = flask.request.form.get("fullname")
        # fileobj = flask.request.files["file"]
        fileobj = flask.request.files.get("file")
        filename = ""

        if fileobj is not None:
            filename = fileobj.filename

        if (username == "" or password == "" or fullname == ""
                or email == "" or filename == ""):
            return flask.abort(400)

        check_user = connection.execute(
            "SELECT username FROM users WHERE username = ?",
            (username,)).fetchone()

        if check_user is not None:
            return flask.abort(409)

        algorithm = 'sha512'
        salt = uuid.uuid4().hex
        hash_object = hashlib.new(algorithm)
        salted_password = salt + password
        hash_object.update(salted_password.encode('utf-8'))
        password_hash = hash_object.hexdigest()
        password_db_string = "$".join([algorithm, salt, password_hash])

        new_filename = save_file(fileobj, filename)
        connection.execute(
            "INSERT INTO users(username, fullname, email, filename, password)"
            " VALUES (?, ?, ?, ?, ?)",
            (username, fullname, email, new_filename, password_db_string))
        flask.session["logname"] = username
        # return flask.redirect(flask.url_for("show_index"))

        if target == "" or target is None:
            return flask.redirect(flask.url_for("show_index"))

        else:
            return flask.redirect(target)

    elif operation == "delete":
        if "logname" not in flask.session:
            return flask.abort(403)

        logname = flask.session["logname"]
        flask.session.clear()
        profile_picture = connection.execute(
            "SELECT filename FROM users WHERE username = ?",
            (logname,)).fetchone()
        post_pictures = connection.execute(
            "SELECT filename FROM posts WHERE owner = ?",
            (logname,)).fetchall()

        os.remove(
            insta485.app.config["UPLOAD_FOLDER"]/profile_picture["filename"])
        for picture in post_pictures:
            os.remove(insta485.app.config["UPLOAD_FOLDER"]/picture["filename"])

        connection.execute(
            "DELETE FROM users WHERE username = ?", (logname,))
        connection.execute(
            "DELETE FROM posts WHERE owner = ?", (logname,))
        connection.execute(
            "DELETE FROM following WHERE username1 = ?", (logname,))
        connection.execute(
            "DELETE FROM following WHERE username2 = ?", (logname,))
        connection.execute(
            "DELETE FROM comments WHERE owner = ?", (logname,))
        connection.execute(
            "DELETE FROM likes WHERE owner = ?", (logname,))

        if target is None or target == "":
            return flask.redirect(flask.url_for("show_index"))

        else:
            # return flask.redirect(flask.url_for(
            # "display_create_account_page"))
            return flask.redirect(target)

    elif operation == "edit_account":
        if "logname" not in flask.session:
            return flask.abort(403)

        fullname = flask.request.form.get("fullname")
        email = flask.request.form.get("email")
        logname = flask.session["logname"]

        if fullname == "" or email == "":
            return flask.abort(400)

        # fileobj = flask.request.files["file"]
        fileobj = flask.request.files.get("file")
        filename = ""

        if fileobj is not None:
            filename = fileobj.filename

        if filename == "":
            connection.execute(
                "UPDATE users SET fullname = ?, email = ? WHERE username = ?",
                (fullname, email, flask.session["logname"]))

        else:
            old_profile_photo = connection.execute(
                "SELECT filename FROM users WHERE username = ?",
                (logname,)).fetchone()
            new_dir = insta485.app.config["UPLOAD_FOLDER"]
            os.remove(
                new_dir/old_profile_photo["filename"])
            new_filename = save_file(fileobj, filename)
            connection.execute(
                "UPDATE users SET fullname = ?, email = ?,"
                " filename = ? WHERE username = ?",
                (fullname, email, new_filename, flask.session["logname"]))

        if target is None or target == "":
            return flask.redirect(flask.url_for("show_index"))

        else:
            # return flask.redirect(flask.url_for
            # ("display_edit_account_form"))
            return flask.redirect(target)

    elif operation == "update_password":
        if "logname" not in flask.session:
            return flask.abort(403)

        old_password = flask.request.form.get("password")
        new_password = flask.request.form.get("new_password1")
        repeat_password = flask.request.form.get("new_password2")
        correct_password = connection.execute(
            "SELECT password FROM users WHERE username = ?",
            (flask.session["logname"],)).fetchone()

        if old_password == "" or new_password == "" or repeat_password == "":
            return flask.abort(400)

        if correct_password is not None:
            data = []
            for key, value in correct_password.items():
                data.append(value)

            data = data[0].split("$")
            algorithm = data[0]
            salt = data[1]
            hash_object = hashlib.new(algorithm)
            salted_password = salt + old_password
            hash_object.update(salted_password.encode('utf-8'))
            password_hash = hash_object.hexdigest()
            password_db_string = "$".join([algorithm, salt, password_hash])
            context = {"logname": flask.session["logname"]}

            if (password_db_string == correct_password["password"] and
                    new_password == repeat_password):
                algorithm = 'sha512'
                salt = uuid.uuid4().hex
                hash_object = hashlib.new(algorithm)
                salted_password = salt + new_password
                hash_object.update(salted_password.encode('utf-8'))
                password_hash = hash_object.hexdigest()
                password_db_string = "$".join([algorithm, salt, password_hash])
                connection.execute(
                    "UPDATE users SET password = ? WHERE username = ?",
                    (password_db_string, flask.session["logname"]))

                if target is None or target == "":
                    return flask.redirect(flask.url_for("show_index"))

                else:
                    return flask.redirect(target)

            elif password_db_string != correct_password["password"]:
                return flask.abort(403)

            elif new_password != repeat_password:
                return flask.abort(401)

        else:
            return flask.abort(403)
