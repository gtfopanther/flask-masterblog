import json
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
POSTS_FILE = os.path.join(DATA_DIR, "blog_posts.json")


# ----------------------------
# JSON Helpers
# ----------------------------

def load_posts():
    """Load all blog posts from the JSON file."""
    if not os.path.exists(POSTS_FILE):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(POSTS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []

    with open(POSTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Sicherstellen, dass jeder Post Likes hat
    for post in data:
        if "likes" not in post:
            post["likes"] = 0

    return data if isinstance(data, list) else []


def save_posts(posts):
    """Save all blog posts back into the JSON file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)


def generate_new_id(posts):
    """Generate a unique ID based on the highest existing ID."""
    if not posts:
        return 1
    return max(post.get("id", 0) for post in posts) + 1


def fetch_post_by_id(post_id, posts):
    """Return the post dict matching post_id or None."""
    for post in posts:
        if post.get("id") == post_id:
            return post
    return None


# ----------------------------
# Routes
# ----------------------------

@app.route("/")
def index():
    posts = load_posts()
    posts = sorted(posts, key=lambda p: p.get("id", 0), reverse=True)
    save_posts(posts)  # speichert Likes-Feld falls neu hinzugefügt
    return render_template("index.html", posts=posts)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        posts = load_posts()

        author = request.form.get("author", "").strip()
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        new_post = {
            "id": generate_new_id(posts),
            "author": author,
            "title": title,
            "content": content,
            "likes": 0
        }

        posts.append(new_post)
        save_posts(posts)

        return redirect(url_for("index"))

    return render_template("add.html")


@app.route("/delete/<int:post_id>")
def delete(post_id):
    posts = load_posts()
    posts = [post for post in posts if post.get("id") != post_id]
    save_posts(posts)
    return redirect(url_for("index"))


@app.route("/update/<int:post_id>", methods=["GET", "POST"])
def update(post_id):
    posts = load_posts()
    post = fetch_post_by_id(post_id, posts)

    if post is None:
        return "Post not found", 404

    if request.method == "POST":
        post["author"] = request.form.get("author", "").strip()
        post["title"] = request.form.get("title", "").strip()
        post["content"] = request.form.get("content", "").strip()

        save_posts(posts)
        return redirect(url_for("index"))

    return render_template("update.html", post=post)


# ----------------------------
# LIKE BONUS ROUTE ❤️
# ----------------------------

@app.route("/like/<int:post_id>")
def like(post_id):
    posts = load_posts()
    post = fetch_post_by_id(post_id, posts)

    if post is not None:
        post["likes"] += 1
        save_posts(posts)

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
