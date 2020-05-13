import os
from io import BytesIO
from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (ImageMessage, MessageEvent, TextMessage,
                            TextSendMessage)
from google.cloud import vision
import requests

KEY = os.environ["COMPUTER_VISION_API_KEY"]
endpoint = 'https://eastasia.api.cognitive.microsoft.com/vision/v1.0/ocr'

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
    text = event.message.text
    if (text.startswith('http')):
        image_text = get_text_by_ms(text)
        messages = TextSendMessage(text=image_text)
    else:
        messages = TextSendMessage(text='画像を送信するか、画像のURLを送ってみてね!')
    reply_message(event, messages)


@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    message_id = event.message.id
    message_content = line_bot_api.get_message_content(message_id)
    image = BytesIO(message_content.content)

    try:
        image_text = get_text_by_ms(image)
        message = TextSendMessage(text=image_text)
        reply_message(event, message)

    except Exception as e:
        reply_message(event, TextSendMessage(text='エラーが発生しました'))


def reply_message(event, messages):
    line_bot_api.reply_message(
        event.reply_token,
        messages,
    )


def get_text_by_ms(image_url=None, image=None):
    if image_url is None and image is None:
        return '必要な情報が足りません'

    params = {'visualFeatures': 'Categories,Description,Color'}

    if image_url:
        headers = {
            'Ocp-Apim-Subscription-Key': KEY,
            'Content-Type': 'application/json',
        }
        data = {'url': image_url}
        response = requests.post(
            endpoint,
            headers=headers,
            params=params,
            json=data
        )

    elif image is not None:
        headers = {
            'Ocp-Apim-Subscription-Key': KEY,
            "Content-Type": "application/octet-stream"
        }
        response = requests.post(
            endpoint,
            headers=headers,
            params=params,
            data=image,
        )

    status = response.status_code
    data = response.json()

    if status != 200:

        if data['code'] == 'InvalidImageSize':
            text = '画像のサイズが大きすぎます'

        elif data['code'] == 'InvalidImageUrl':
            text = 'この画像URLからは取得できません'

        elif data['code'] == 'InvalidImageFormat':
            text = '対応していない画像形式です'

        else:
            text = 'エラーが発生しました'

        print(status, data)
        return text

    text = ''
    for region in data['regions']:
        for line in region['lines']:
            for word in line['words']:
                text += word.get('text', '')
                if data['language'] != 'ja':
                    text += ' '
        text += '\n'

    if len(text) == 0:
        text += '文字が検出できませんでした'

    print('text:', text)
    return text


if __name__ == "__main__":
    port = os.environ.get('PORT', 3333)
    app.run(
        host='0.0.0.0',
        port=port,
    )
