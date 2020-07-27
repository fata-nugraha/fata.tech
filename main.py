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
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage
)
from pubsub_helper import pubsub_helper
from vision_helper import vision_helper
from sheets_helper import sheets_helper

app = Flask(__name__)
r = redis.Redis(host=os.environ.get("REDIS_HOST"), port=17990, password=os.environ.get("REDIS_PASS"), health_check_interval=30)
line_bot_api = LineBotApi(os.environ.get("LINE_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("LINE_SECRET"))
tempfile = "/tmp/ss.jpg"
keyword = os.environ.get("KEYWORD")

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text.lower()=="ed":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="aing cupu")
        )
    elif event.message.text.lower()==keyword:
        r.set(keyword, 1)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Keyword accepted")
        )

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    with open(tempfile, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)
    output = vision_helper.ocr(tempfile)
    if int(r.get(keyword).decode('ascii'))==1:
        currencies = sheets_helper.convert_currencies(output)
        output = sheets_helper.update_sheets(currencies)
        r.set(keyword, 0)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=str(output))
    )

@app.route('/publish/<message>')
def sendemail(message):
    pubsub_helper.publish(message)
    return "Email Sent"

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