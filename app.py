from flask import Flask, render_template, request, redirect
import json

POSTS_FILE = r"static\posts.json"


def get_posts():
    with open(POSTS_FILE) as f:
        posts = json.load(f)
        posts = posts[::-1]  # reverse the order of the posts so the newest one is at te top
    return posts


def save_posts(posts):
    with open(POSTS_FILE, "w") as f:
        json.dump(posts, f)


app = Flask(__name__, template_folder='templates', static_folder='static')  # create the app


@app.route('/')
def home():
    return render_template('home.html', posts=get_posts())


@app.route('/interest-blog')
def interest_blog():
    return render_template('interest_blog.html')


@app.route('/study-blog')
def study_blog():
    return render_template('study_blog.html')


@app.route('/post/<int:post_id>')
def post(post_id):
    post = get_posts()[-post_id]
    return render_template('post.html', post=post)


@app.route("/edit/<int:index>")
def edit_post(index):
    posts = get_posts()
    post = posts[-index]
    return render_template("edit_post.html", post=post)


@app.route("/save/<int:index>", methods=["POST"])
def save_post(index):
    posts = get_posts()
    post = posts[-index]
    post["title"] = request.form["title"]
    post["date_posted"] = request.form["date_posted"]
    post["content"] = request.form["content"]
    post["paper"] = request.form["paper"]
    save_posts(posts)
    return redirect("/")


@app.route("/new", methods=["GET", "POST"])
def new_post():
    if request.method == "POST":
        title = request.form["title"]
        date_posted = request.form["date_posted"]
        content = request.form["content"]
        paper = request.form["paper"]
        posts = get_posts()
        post = {"id": str(len(posts)+1), "date_posted": date_posted, "title": title, "content": content, "paper": paper}
        posts.append(post)
        # Replace with your database or file storage system
        with open(POSTS_FILE, "w") as f:
            json.dump(posts, f)
        return redirect("/")
    else:
        return render_template("new_post.html")


@app.route("/delete/<int:index>")
def delete_post(index):
    posts = get_posts()
    posts.pop(index-1)
    save_posts(posts)
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)
