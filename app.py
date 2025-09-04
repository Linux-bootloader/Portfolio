import os
from flask import Flask, render_template, request
from notion_client import Client
from dotenv import load_dotenv

# Load .env file into environment
load_dotenv(dotenv_path='./.env')

app = Flask(__name__)

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

if not NOTION_API_KEY or not DATABASE_ID:
    raise ValueError("⚠️ NOTION_API_KEY or NOTION_DATABASE_ID not set. Check your .env file.")

notion = Client(auth=NOTION_API_KEY)


# ---- Function to fetch posts from Notion database ----
def load_posts_from_notion():
    results = notion.databases.query(
        database_id=DATABASE_ID,
        filter={
            "property": "Status",
            "status": {
                "equals": "Completed"
            }
        },
        sorts=[  # must use `timestamp`, not "Created time"
            {"timestamp": "created_time", "direction": "descending"}
        ]
    )
    
    posts = []
    for item in results["results"]:
        post_id = item["id"]

        # Title from Project Name (your DB screenshot shows that)
        title = "Untitled"
        if "Project Name" in item["properties"]:
            project_name = item["properties"]["Project Name"]["title"]
            if project_name:
                title = project_name[0]["plain_text"]

        # Fetch block children
        blocks = notion.blocks.children.list(post_id)
        content = ""

        for block in blocks["results"]:
            t = block["type"]
            rich_texts = block[t].get("rich_text", [])
            text = " ".join([r["plain_text"] for r in rich_texts])

            if t == "paragraph":
                content += text + "<br>"
            elif t == "heading_1":
                content += f"<h1>{text}</h1>"
            elif t == "heading_2":
                content += f"<h2>{text}</h2>"
            elif t == "heading_3":
                content += f"<h3>{text}</h3>"
            elif t == "bulleted_list_item":
                content += f"<ul><li>{text}</li></ul>"
            elif t == "numbered_list_item":
                content += f"<ol><li>{text}</li></ol>"

        posts.append({"title": title, "content": content})
    return posts


# ---- ROUTES ----

@app.route("/")
def home():
    return render_template("index.html", title="Home")

@app.route("/about")
def about():
    return render_template("about.html", title="About Me")

@app.route("/portfolio")
def portfolio():
    posts = load_posts_from_notion()

    if not posts:
        return render_template("portfolio.html", post={"title": "No Posts Found", "content": "Please add posts to your Notion database"}, prev_index=0, next_index=0)

    index = int(request.args.get("index", 0))   # default: first post (latest)
    index = max(0, min(index, len(posts) - 1))  # clamp index in range

    post = posts[index]

    prev_index = (index - 1) % len(posts)
    next_index = (index + 1) % len(posts)

    return render_template("portfolio.html", post=post, prev_index=prev_index, next_index=next_index)


# ---- Run locally ----
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=85, debug=True)