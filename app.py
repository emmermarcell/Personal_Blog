from flask import Flask, render_template, request, redirect, session
import json
from bs4 import BeautifulSoup
import re
from pathlib import Path

# Define the path to the json file containing the posts
THIS_FOLDER = Path(__file__).parent.resolve()
POSTS_FILE = THIS_FOLDER / 'static/posts.json'
# Define your user ID here
USER_ID = "AdventureTimeFan2000"
PASSWORD = "LetsGoInTheGarden"


def regex_find(value, pattern):
    """Find the first match of a regex pattern in a string and return it as a Match object."""
    regex = re.compile(pattern)
    match = regex.search(value)
    if match:
        return match


def get_posts():
    """Get the posts from the json file and sort them by date of posting."""
    with open(POSTS_FILE) as f:
        posts = json.load(f)
    posts = sorted(posts, key=lambda p: int(p['id']))
    return posts


def get_posts_for_page(page, posts_per_page):
    # Load posts from JSON
    with open(POSTS_FILE) as f:
        all_posts = json.load(f)

    # Sort the posts by their 'id' in descending order to ensure latest posts come first
    sorted_posts = sorted(all_posts, key=lambda x: int(x['id']), reverse=True)

    # Calculate the indices for slicing the posts for the current page
    start_index = (page - 1) * posts_per_page
    end_index = start_index + posts_per_page
    page_posts = sorted_posts[start_index:end_index]

    # Return the posts for the current page and the total number of posts
    return page_posts, len(all_posts)


def save_posts(posts):
    """Save the posts to the json file."""
    with open(POSTS_FILE, "w") as f:
        json.dump(posts, f)


app = Flask(__name__, template_folder='templates', static_folder='static')  # create the app
app.secret_key = 'secret_key'  # set a secret key for the app
app.add_template_filter(regex_find, 'regex_find')  # add the regex filter to the app


@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)  # Default to page 1 if not specified
    posts_per_page = 5
    # Assuming get_posts() is modified to return a subset of posts and the total count
    posts, total_posts = get_posts_for_page(page, posts_per_page)

    # Calculate if there's a next page
    has_more = page * posts_per_page < total_posts

    # Now include 'page' and 'has_more' in the context passed to the template
    return render_template('home.html', posts=posts, page=page, has_more=has_more)



@app.route('/interest-blog')
def interest_blog():
    return render_template('interest_blog.html')


@app.route('/study-blog')
def study_blog():
    return render_template('study_blog.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/post/<int:index>')
def post(index):
    """Get the post with the given id and render the post template."""
    post = get_posts()[index]
    try:
        soup = BeautifulSoup(post['content'], 'html.parser')
    except Exception as e:
        print(f'Error creating soup for post {index}: {e}')
        soup = None
    text = soup.get_text()
    return render_template('post.html', post=post, soup=soup, text=text)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login page and authentication."""
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        if user_id == USER_ID and password == PASSWORD:
            session['logged_in'] = True
            session['user_id'] = USER_ID
            return redirect('/')
        else:
            return render_template('login.html', error='Invalid login credentials')
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    """Handle logout."""
    session.pop('logged_in', None)
    session.pop('user_id', None)
    return redirect('/login')


@app.route("/edit/<int:index>")
def edit_post(index):
    if 'user_id' not in session or session['user_id'] != USER_ID:
        # User is not logged in or not authorized to edit posts
        return redirect('/login')
    posts = get_posts()
    post = posts[index]
    return render_template("edit_post.html", post=post)


@app.route("/save/<int:index>", methods=["POST"])
def save_post(index):
    if 'user_id' not in session or session['user_id'] != USER_ID:
        # User is not logged in or not authorized to edit posts
        return redirect('/login')
    posts = get_posts()
    post = posts[index]
    post["title"] = request.form["title"]
    post["tags"] = request.form["tags"]
    post["date_posted"] = request.form["date_posted"]
    post["content"] = request.form["content"]
    post["paper"] = request.form["paper"]
    save_posts(posts)
    return redirect("/")


@app.route("/new", methods=["GET", "POST"])
def new_post():
    # Check if the user is logged in
    if not session.get('logged_in'):
        return render_template('login.html')

    if request.method == "POST":
        title = request.form["title"]
        date_posted = request.form["date_posted"]
        tags = request.form["tags"]
        content = request.form["content"]
        paper = request.form["paper"]
        posts = get_posts()
        post = {"id": str(len(posts)), "date_posted": date_posted, "title": title, "tags": tags, "content": content,
                "paper": paper}
        posts.append(post)
        # Replace with your database or file storage system
        with open(POSTS_FILE, "w") as f:
            json.dump(posts, f)
        return redirect("/")
    else:
        return render_template("new_post.html")


@app.route("/delete/<int:index>", methods=["GET", "POST"])
def delete_post(index):
    if 'user_id' not in session or session['user_id'] != USER_ID:
        # User is not logged in or not authorized to edit posts
        return redirect('/login')
    posts = get_posts()
    posts.pop(index)
    # update ids of posts that come after the deleted post
    for i in range(index, len(posts)):
        posts[i]['id'] = str(i)
    save_posts(posts)
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)
