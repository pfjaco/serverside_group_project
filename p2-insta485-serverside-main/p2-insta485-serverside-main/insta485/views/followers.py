"""Insta485 followers view."""
import flask
import insta485


@insta485.app.route("/users/<username>/followers/")
def show_followers(username):
    """Display a user's followers."""
    if "logname" not in flask.session:
        return flask.redirect(flask.url_for("login_user"))

    logname = flask.session["logname"]
    connection = insta485.model.get_db()

    usernameExists = connection.execute(
        "SELECT username FROM users WHERE username = ?",
        (username,)).fetchone()

    if usernameExists is None:
        flask.abort(404)

    followers = connection.execute(
        "SELECT username1 FROM following WHERE username2 = ?",
        (username,)).fetchall()

    '''
    if followers is None:
        flask.abort(404)
    '''

    # check if each user is following the logged in user
    for i in range(0, len(followers)):
        is_following = -1
        follower = connection.execute(
            "SELECT username1, username2 FROM following"
            " WHERE username1 = ? AND username2 = ?",
            (logname, followers[i]["username1"])).fetchone()

        if logname != followers[i]["username1"] and follower is not None:
            is_following = 1
        elif logname != followers[i]["username1"] and follower is None:
            is_following = 0

        followers[i]["is_following"] = is_following

    # get the profile picture of each follower
    for i in range(0, len(followers)):
        profile_picture = connection.execute(
            "SELECT filename FROM users WHERE username = ?",
            (followers[i]["username1"],)).fetchone()
        followers[i]["profile_picture"] = profile_picture

    context = {"followers": followers,
               "logname": logname, "username": username}
    return flask.render_template("followers.html", **context)
