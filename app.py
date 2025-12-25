# Copyright © 2025 Jacob Jones. All rights reserved.
# Licensed for private, personal, non-commercial use only.
# Commercial licence available: https://jacobjones.gumroad.com/l/Coffee

import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from itsdangerous import URLSafeTimedSerializer
from notion_client import Client
from dotenv import load_dotenv
from flask_wtf import FlaskForm
from flask_mail import Message, Mail
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")


NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
PAGE_ID = os.getenv("NOTION_PAGE_ID")
SMTP_API_TOKEN = os.getenv("SMTP_API_TOKEN")


if not NOTION_API_KEY or not DATABASE_ID or not PAGE_ID:
    raise ValueError("⚠️ NOTION_API_KEY or NOTION_DATABASE_ID or NOTION_PAGE_ID not set. Check your .env file.")

notion = Client(auth=NOTION_API_KEY)


app.config['MAIL_SERVER']='live.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'api'
app.config['MAIL_PASSWORD'] = SMTP_API_TOKEN
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

s = URLSafeTimedSerializer(app.secret_key)

def generate_verification_token(email):
    return s.dumps(email, salt='email-confirm')

def confirm_verification_token(token, expiration=3600):
    try:
        email = s.loads(token, salt='email-confirm', max_age=expiration)
    except:
        return False
    return email

mail = Mail(app)

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10)])


def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender='noreply@jacobjones.com.au'
    )
    mail.send(msg)

def sendEmail(email_template):
    msg = Message(
        subject='New Message from portfolio contact',
        recipients=['admin@jacobjones.com.au'],
        html=email_template,
        sender='portfolio@jacobjones.com.au'
    )
    mail.send(msg)

def get_data_source_id(database_id: str) -> str:
    resp = notion.databases.retrieve(database_id=database_id)
    data_sources = resp.get("data_sources", [])
    if not data_sources:
        raise Exception("No data sources found in database")
    # pick the first (or choose by name if multiple)
    return data_sources[0]["id"]

def load_posts_from_notion(data_source_id: str):
    # 1. Query the data source
    resp = notion.data_sources.query(
        data_source_id=data_source_id,
        filter={
            "property": "Status",
            "status": {
                "equals": "Completed"
            }
        },
        sorts=[
            {"timestamp": "created_time", "direction": "descending"}
        ]
    )

    posts = []

    for item in resp["results"]:
        post_id = item["id"]

        # 2. Extract title
        title = "Untitled"
        if "Project Name" in item["properties"]:
            project_name = item["properties"]["Project Name"]["title"]
            if project_name:
                title = project_name[0]["plain_text"]

        # 3. Load block content
        blocks = notion.blocks.children.list(post_id)
        content = ""

        for block in blocks["results"]:
            t = block["type"]
            data = block[t]
            rich_texts = data.get("rich_text", [])
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
            elif t == "divider":
                content += "<hr>"
            elif t == "quote":
                content += f"<blockquote>{text}</blockquote>"
            elif t == "code":
                content += f"<pre><code>{text}</code></pre>"
            elif t == "to_do":
                checkbox = "☑" if data.get("checked", False) else "☐"
                content += f"{checkbox} {text}<br>"
            elif t == "toggle":
                content += f"<details><summary>{text}</summary></details>"
            elif t == "image":
                image_url = data["file"]["url"]
                content += f'<img src="{image_url}" alt="Image"><br>'

        posts.append({
            "title": title,
            "content": content
        })

    return posts


def get_page_icon(page_id):
    page = notion.pages.retrieve(page_id)
    icon = page.get("icon")
    if icon["type"] == "emoji":
        return icon["emoji"]
    elif icon["type"] in ["file", "external"]:
        return icon[icon["type"]]["url"]

    return None

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html", title="Home")

@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html", title="About Me")

@app.route("/portfolio", methods=["GET"])
def portfolio():
    data_source_id = get_data_source_id(DATABASE_ID)
    posts = load_posts_from_notion(data_source_id=data_source_id)
    page_icon = get_page_icon(PAGE_ID)
    
    if not posts:
        return render_template("portfolio.html", post={"title": "No Posts Found", "content": "Jacob has not just posted anything as of yet"}, prev_index=0, next_index=0)

    index = int(request.args.get("index", 0))   
    index = max(0, min(index, len(posts) - 1))  

    post = posts[index]

    prev_index = (index - 1) % len(posts)
    next_index = (index + 1) % len(posts)

    return render_template("portfolio.html", page_icon=page_icon, post=post, prev_index=prev_index, next_index=next_index)

info = ''
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        if not name or not email or not message:
            flash('All fields are required!', 'danger')
            return redirect(url_for('contact'))

        session['contact_data'] = {
            'name': name,
            'email': email,
            'message': message
        }

        token = generate_verification_token(email)
        verify_url = url_for('verify_email', token=token, _external=True)
        html = render_template('verify_email.html', verify_url=verify_url)
        subject = "Please verify your email"
        send_email(email, subject, html)

        flash('A verification email has been sent to your email address. Please note the link will NOT work if you are in a private tab', 'info')
        return redirect(url_for('contact'))


    return render_template('contact.html', title="Contact Me")

@app.route('/verify/<token>')
def verify_email(token):
    email = confirm_verification_token(token)

    if not email:
        flash('The verification link is invalid or has expired.', 'danger')
        return redirect(url_for('contact'))


    contact_data = session.get('contact_data')
    if not contact_data:
        flash('Session expired. Please resubmit the form.', 'warning')
        return redirect(url_for('contact'))

    name = contact_data['name']
    message = contact_data['message']


    email_template = render_template('Email.html', name=name, email=email, msg=message)
    sendEmail(email_template)

    session.pop('contact_data', None)

    flash('Your email has been verified successfully and your message has been sent!', 'success')
    return redirect(url_for('contact'))

