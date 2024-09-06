"""Display user posts."""
import flask
import arrow
import insta485


@insta485.app.route("/posts/<postid>/")
def show_post(postid):
    """Display posts of a given user."""
    if "logname" not in flask.session:
        return flask.redirect(flask.url_for("login_user"))

    logname = flask.session["logname"]

    connection = insta485.model.get_db()
    post = connection.execute(
        "SELECT owner, filename, postid, created"
        " FROM posts WHERE postid = ?", (postid,)).fetchone()
    profile_picture = connection.execute(
        "SELECT filename FROM users where username =?",
        (post["owner"],)).fetchone()
    likes = connection.execute(
        "SELECT COUNT(*) FROM likes WHERE postid = ?", (postid,)).fetchone()
    post['created'] = arrow.get(post['created']).humanize()
    comments = connection.execute(
        "SELECT owner, text, commentid FROM comments WHERE postid = ?",
        (postid,)).fetchall()

    get_liked = connection.execute(
        "SELECT owner FROM likes WHERE owner = ? AND postid = ?",
        (logname, postid)).fetchone()
    liked = 0

    if get_liked is not None:
        liked = 1

    context = {"liked": liked, "logname": logname,
               "profile_picture": profile_picture,
               "post": post, "likes": likes["COUNT(*)"],
               "comments": comments}
    return flask.render_template("post.html", **context)
