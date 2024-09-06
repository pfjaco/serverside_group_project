"""Enable follow and unfollow functionality."""
import insta485
import flask


@insta485.app.route("/following/", methods=["POST"])
def handle_following_operations():
    """Enable users to follow and unfollow other users."""
    if "logname" not in flask.session:
        return flask.abort(403)

    connection = insta485.model.get_db()
    operation = flask.request.form.get("operation")
    username = flask.request.form.get("username")
    logname = flask.session["logname"]
    target = flask.request.args.get("target")
    followAlready = connection.execute(
        "SELECT * FROM following WHERE username1 = ? AND username2 = ?",
        (logname, username)).fetchone()

    if operation == "follow":
        # make sure logname isn't already following username
        if followAlready is not None:
            return flask.abort(409)
        # follow them
        else:
            connection.execute(
                "INSERT INTO following(username1, username2) VALUES (?, ?)",
                (logname, username))

    elif operation == "unfollow":
        # make sure logname isn't already NOT following username
        if followAlready is None:
            return flask.abort(409)
        # unfollow them
        else:
            connection.execute(
                "DELETE FROM following WHERE username1 = ? AND username2 = ?",
                (logname, username))

    if target == "" or target is None:
        return flask.redirect(flask.url_for("show_index"))
    else:
        return flask.redirect(target)
