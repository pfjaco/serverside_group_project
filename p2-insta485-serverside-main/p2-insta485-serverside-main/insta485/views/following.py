"""Insta485 following view."""

import flask
import insta485


@insta485.app.route("/users/<username>/following/")
def show_following(username):
    """Display a user's following."""
    if "logname" not in flask.session:
        return flask.redirect(flask.url_for("login_user"))

    logname = flask.session["logname"]
    connection = insta485.model.get_db()

    username_exists = connection.execute(
        "SELECT username FROM users WHERE username = ?",
        (username,)).fetchone()

    if username_exists is None:
        flask.abort(404)

    following = connection.execute(
        "SELECT username2 FROM following WHERE username1 = ?",
        (username,)).fetchall()

    """
    if following is None:
        flask.abort(404)
    """

    # check if each user is following the logged in user
    for i in range(0, len(following)):
        is_following = -1
        follow = connection.execute(
            "SELECT username1, username2 FROM following"
            " WHERE username1 = ? AND username2 = ?",
            (logname, following[i]["username2"])).fetchone()

        if logname != following[i]["username2"] and follow is not None:
            is_following = 1
        elif logname != following[i]["username2"] and follow is None:
            is_following = 0

        following[i]["is_following"] = is_following

    # get the profile picture of each following
    for i in range(0, len(following)):
        profile_picture = connection.execute(
            "SELECT filename FROM users WHERE username = ?",
            (following[i]["username2"],)).fetchone()
        following[i]["profile_picture"] = profile_picture

    context = {"following": following,
               "logname": logname, "username": username}
    return flask.render_template("following.html", **context)
