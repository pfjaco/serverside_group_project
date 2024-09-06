"""
Insta485 user view.

URLS include:
/users/<user_url_slug>/
"""

import flask
import insta485


@insta485.app.route("/users/<username>/")
def show_user(username):
    """Display the user's profile."""
    if "logname" not in flask.session:
        return flask.redirect(flask.url_for("login_user"))

    logname = flask.session["logname"]
    connection = insta485.model.get_db()

    # Abort if slug does not exist in the database
    user = connection.execute(
        "SELECT username FROM users WHERE username = ?",
        (username,)).fetchone()
    if user is None:
        flask.abort(404)

    posts = connection.execute(
        "SELECT postid, filename FROM posts WHERE owner = ?",
        (username,)).fetchall()
    num_posts = connection.execute(
        "SELECT COUNT(*) FROM posts WHERE owner = ?",
        (username,)).fetchone()
    num_followers = connection.execute(
        "SELECT COUNT(*) FROM following WHERE username2 = ?",
        (username,)).fetchone()
    num_following = connection.execute(
        "SELECT COUNT(*) FROM following WHERE username1 = ?",
        (username,)).fetchone()
    fullname = connection.execute(
        "SELECT fullname FROM users WHERE username = ?",
        (username,)).fetchone()
    following = connection.execute(
        "SELECT username1, username2 FROM following"
        " WHERE username1 = ? AND username2 = ?",
        (logname, username)).fetchall()
    is_following = -1

    if logname != username and len(following) > 0:
        is_following = 1

    elif logname != username and len(following) == 0:
        is_following = 0

    context = {"is_following": is_following, "fullname": fullname["fullname"],
               "username": username, "logname": logname, "posts": posts,
               "num_posts": num_posts["COUNT(*)"],
               "num_followers": num_followers["COUNT(*)"],
               "num_following": num_following["COUNT(*)"]}
    return flask.render_template("user.html", **context)
