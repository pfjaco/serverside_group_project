"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import arrow
import insta485


@insta485.app.route("/uploads/<path:filename>")
def get_file(filename):
    """Display files."""
    if "logname" not in flask.session:
        return flask.abort(403)

    try:
        return flask.send_from_directory(
            insta485.app.config["UPLOAD_FOLDER"], filename)
    except FileNotFoundError:
        return flask.abort(404)


@insta485.app.route('/', methods=["GET"])
def show_index():
    """Display / route."""
    # Connect to database
    connection = insta485.model.get_db()

    if "logname" not in flask.session:
        return flask.redirect(flask.url_for("login_user"))

    logname = flask.session["logname"]

    # fetch relevant usernames for the posts on page / (index.html)
    query = connection.execute(
        "SELECT username1, username2 FROM following WHERE username1 = ?",
        (logname,))

    following = query.fetchall()
    profile_pictures = []
    posts = []
    likes = {}

    # fetch the posts from those relevant usernames

    post = connection.execute(
        "SELECT * FROM posts WHERE owner = ? ORDER BY postid DESC",
        (logname,)).fetchall()

    if len(post) > 0:
        posts += post

    for row in following:
        post = connection.execute(
            "SELECT * FROM posts WHERE owner = ? ORDER BY postid DESC",
            (row["username2"],)).fetchall()

        if len(post) > 0:
            posts += post

    posts = list(reversed(sorted(posts, key=lambda x: x['postid'])))

    for i in range(0, len(posts)):
        time = arrow.get(posts[i]["created"])
        posts[i]["created"] = time.humanize()

    # retrieve the profile pictures of the users making the posts
    for i in range(0, len(posts)):
        filename = connection.execute(
            "SELECT username, filename FROM users WHERE username = ?",
            (posts[i]["owner"],)).fetchone()
        filename["postid"] = posts[i]["postid"]
        # flask.send_from_directory(insta485.app.config["UPLOAD_FOLDER"],
        #  filename["filename"])
        profile_pictures.append(filename)

    # compute the number of likes for each post
    for i in range(0, len(posts)):
        like = connection.execute(
            "SELECT COUNT(*) FROM likes WHERE postid = ?",
            (posts[i]["postid"],)).fetchone()
        likes[posts[i]["postid"]] = like["COUNT(*)"]

    # retrieve comments for each post
    for i in range(0, len(posts)):
        add_comment = connection.execute(
            "SELECT owner, text FROM comments WHERE postid = ?",
            (posts[i]["postid"],)).fetchall()
        posts[i]["comments"] = add_comment

    # add profile pictures to posts
    for i in range(0, len(posts)):
        posts[i]["profile_pictures"] = profile_pictures[i]

    for i in range(0, len(posts)):
        like = connection.execute(
            "SELECT owner FROM likes WHERE owner = ? and postid = ?",
            (logname, posts[i]["postid"])).fetchone()

        if like is None:
            posts[i]["liked"] = 0

        else:
            posts[i]["liked"] = 1

    context = {"logname": logname, "profile_pictures": profile_pictures,
               "posts": posts, "likes": likes}
    return flask.render_template("index.html", **context)
