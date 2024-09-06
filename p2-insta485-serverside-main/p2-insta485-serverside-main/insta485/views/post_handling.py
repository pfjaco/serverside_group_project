"""Insta485 post handling functionality."""
import insta485
import flask
import uuid
import pathlib
import os


def save_file(fileobj, filename):
    """Save files to system."""
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix.lower()
    uuid_basename = f"{stem}{suffix}"
    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    fileobj.save(path)

    return uuid_basename


@insta485.app.route("/posts/", methods=["POST"])
def handle_post():
    """Handle posts operation functionality."""
    if "logname" not in flask.session:
        return flask.abort(403)

    connection = insta485.model.get_db()
    operation = flask.request.form.get("operation")
    target = flask.request.args.get("target")
    logname = flask.session["logname"]

    if operation == "create":
        # fileobj = flask.request.files["file"]
        fileobj = flask.request.files.get("file")
        filename = ""

        if fileobj is not None:
            filename = fileobj.filename

        if filename == "":
            return flask.abort(400)

        new_filename = save_file(fileobj, filename)
        connection.execute(
            "INSERT INTO posts(filename, owner) VALUES(?, ?)",
            (new_filename, logname))

        if target == "" or target is None:
            return flask.redirect(flask.url_for("show_user", username=logname))

        else:
            return flask.redirect(target)

        # return flask.redirect(flask.url_for("show_user", username = logname))

    elif operation == "delete":
        postid = flask.request.form.get("postid")
        file_to_delete = connection.execute(
            "SELECT filename FROM posts WHERE postid = ? AND owner = ?",
            (postid, logname)).fetchone()

        if file_to_delete is None:
            return flask.abort(403)

        os.remove(
            insta485.app.config["UPLOAD_FOLDER"]/file_to_delete["filename"])
        connection.execute("DELETE FROM posts WHERE postid = ?", (postid,))
        connection.execute("DELETE FROM comments WHERE postid = ?", (postid,))
        connection.execute("DELETE FROM likes WHERE postid = ?", (postid,))

        if target == "" or target is None:
            return flask.redirect(flask.url_for("show_user", username=logname))

        else:
            return flask.redirect(target)

        # return flask.redirect(flask.url_for("show_user", username = logname))
