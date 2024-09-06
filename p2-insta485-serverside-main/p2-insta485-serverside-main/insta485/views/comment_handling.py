"""Insta485 comment handler."""
import insta485
import flask


@insta485.app.route("/comments/", methods=["POST"])
def handle_comments():
    """Handle creation and deletion of comments."""
    if "logname" not in flask.session:
        return flask.abort(403)

    connection = insta485.model.get_db()
    operation = flask.request.form.get("operation")
    postid = flask.request.form.get("postid")
    logname = flask.session["logname"]
    target = flask.request.args.get("target")

    if operation == "create":
        text = flask.request.form.get("text")

        if text == "":
            return flask.abort(400)

        connection.execute(
            "INSERT INTO comments(owner, postid, text) VALUES(?, ?, ?)",
            (logname, postid, text))

        if target == "" or target is None:
            return flask.redirect(flask.url_for("show_index"))
        else:
            # return flask.redirect(flask.url_for("show_post",
            #  postid = postid))
            return flask.redirect(target)

    elif operation == "delete":
        commentid = flask.request.form.get("commentid")
        is_owner = connection.execute(
            "SELECT owner, commentid FROM comments"
            " WHERE owner = ? AND commentid = ?",
            (logname, commentid)).fetchone()

        if is_owner is None:
            return flask.abort(403)

        connection.execute("DELETE FROM comments WHERE commentid = ?",
                           (commentid,))
        if target == "" or target is None:
            return flask.redirect(flask.url_for("show_index"))

        else:
            # post = target.split("/")[2]
            # could say flask.redirect(target)
            # return flask.redirect(flask.url_for("show_post", postid = post))
            return flask.redirect(target)
