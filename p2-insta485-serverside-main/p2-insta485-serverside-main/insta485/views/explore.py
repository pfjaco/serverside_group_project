"""Insta485 explore view."""
import flask
import insta485


@insta485.app.route("/explore/")
def show_explore():
    """Show explore page."""
    if "logname" not in flask.session:
        return flask.redirect(flask.url_for("login_user"))

    logname = flask.session["logname"]
    connection = insta485.model.get_db()

    users = connection.execute(
        "SELECT username, filename FROM users WHERE username != ?",
        (logname,)).fetchall()
    not_following = []

    for i in range(0, len(users)):
        following = connection.execute(
            "SELECT * FROM following WHERE username1 = ? AND username2 = ?",
            (logname, users[i]["username"])).fetchone()

        if following is None:
            not_following += [{"username": users[i]["username"],
                               "profile_picture": users[i]["filename"]}]

    context = {"not_following": not_following, "logname": logname}
    return flask.render_template("explore.html", **context)
