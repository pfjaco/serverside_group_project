"""Insta485 post handling functionality."""

import pathlib
import uuid
import insta485
import flask


@insta485.app.route("/posts/", methods=["POST"])
def handle_posts_operations():
    """Handle posts operation functionality."""
    connection = insta485.model.get_db()
    operation = flask.request.form.get("operation")
    postid = flask.request.form.get("postid")
    logname = flask.session["logname"]
    target = flask.request.args.get("target")

    if operation == "create":

        fileobj = flask.request.files["file"]
        filename = fileobj.filename

        if fileobj is None:
            return flask.abort(400)

        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"

        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)

        connection.execute(
            "INSERT INTO posts(postid, filename, owner) VALUES (?, ?, ?)",
            (postid, filename, logname))

    elif operation == "delete":

        userPosted = connection.execute(
            "SELECT * FROM posts WHERE postid = ? AND owner = ?",
            (postid, logname)).fetchone()
        if userPosted is None:
            return flask.abort(403)

        connection.execute("DELETE FROM posts WHERE postid = ? AND owner = ?",
                           (postid, logname))

        # TODO: delete a file from the disc

    # TODO?
    if target == "" or target == "/" or target is None:
        return flask.redirect(flask.url_for("show_user", username=logname))
    else:
        return flask.redirect(flask.url_for(target))
