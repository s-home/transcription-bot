import os
from io import BytesIO
from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (ImageMessage, MessageEvent, TextMessage,
                            TextSendMessage)
from transcribe import get_text

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ["YOUR_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["YOUR_CHANNEL_SECRET"])


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    messages = TextSendMessage(text='画像を送信してみてね!')
    reply_message(event, messages)


@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    message_id = event.message.id
    message_content = line_bot_api.get_message_content(message_id)
    image = BytesIO(message_content.content)

    try:
        image_text = get_text(image)
        message = TextSendMessage(text=image_text)
        reply_message(event, message)

    except Exception as e:
        reply_message(event, TextSendMessage(text='エラーが発生しました'))


def reply_message(event, messages):
    line_bot_api.reply_message(
        event.reply_token,
        messages,
    )


if __name__ == "__main__":
    port = os.environ.get('PORT', 3333)
    app.run(
        host='0.0.0.0',
        port=port,
    )
