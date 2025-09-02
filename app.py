import os
from flask import Flask, render_template
from markupsafe import Markup

app = Flask(__name__)

POSTS_DIR = "posts"


def load_posts():
    posts = []
    for filename in os.listdir(POSTS_DIR):
        if filename.endswith(".md"):
            filepath = os.path.join(POSTS_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                md_content = f.read()
                html_content = markdown.markdown(md_content)
                posts.append({
                    "title": filename.replace(".md", ""),
                    "content": Markup(html_content),
                })
    return posts


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/portfolio")
def portfolio():
    posts = load_posts()
    return render_template("portfolio.html", posts=posts)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=85)