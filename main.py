from app import app

import os
from flask import Flask, url_for, redirect, send_from_directory, render_template, abort, request
import redis

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)
r = redis.Redis(host="redis-17990.c1.ap-southeast-1-1.ec2.cloud.redislabs.com", port=17990, password=os.environ.get("REDIS_PASS"), health_check_interval=30)
line_bot_api = LineBotApi(os.environ.get("LINE_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("LINE_SECRET"))
# client = pymongo.MongoClient("mongodb+srv://default:"+os.environ.get("MONGO_CRED")+"@database.07g0f.gcp.mongodb.net/?retryWrites=true&w=majority")
# db = client.websh
# sh = db.links

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text=="Ed":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Moved App Engine to Jakarta"))

@app.route("/")
def home():
    r.incr("visitor")
    return render_template("index.html", visitor=r.get("visitor").decode('ascii'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/test/<key>')
def test(key):
    return r.get(key)

# @app.route('/sh/<path>')
# def redirect(path):
#     data = sh.find_one({"path":path})
#     return redirect(data["target"], 301)

@app.route('/discord')
def discord():
    return redirect("https://discord.gg/mNn4HJw", 301)

@app.route('/gmeet')
def gmeet():
    return redirect("https://meet.google.com/kps-eafk-krb", 301)

@app.route('/resume')
def resume():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                                'resume.pdf', mimetype='application/pdf')

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080)