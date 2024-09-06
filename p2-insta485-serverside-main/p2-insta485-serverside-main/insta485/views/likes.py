"""Handle like and unlike functionality."""
import flask
import insta485


@insta485.app.route("/likes/", methods=["POST"])
def post_like_unlike():
    """Handle operations involving liking and unliking posts."""
    connection = insta485.model.get_db()
    logname = flask.session['logname']
    postid = flask.request.form.get("postid")
    log_like = connection.execute(
        "SELECT * from likes WHERE postid = ? and owner = ?",
        (postid, logname)).fetchone()
    target = flask.request.args.get("target")
    if flask.request.form.get("operation") == "like":
        if log_like is not None:
            return flask.abort(409)
        else:
            connection.execute(
                "INSERT INTO likes(owner, postid) VALUES (?,?)",
                (logname, postid))
            if target == "" or target is None:
                return flask.redirect(
                    flask.url_for("show_index"))
            else:
                return flask.redirect(target)
    else:
        if log_like is not None:
            connection.execute(
                "DELETE FROM likes WHERE postid = ? AND owner = ?",
                (postid, logname))
            if target == "" or target is None:
                return flask.redirect(flask.url_for("show_index"))
            else:
                return flask.redirect(target)
        else:
            return flask.abort(409)
