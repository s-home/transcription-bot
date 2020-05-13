import os
from io import BytesIO
from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (ImageMessage, MessageEvent, TextMessage,
                            TextSendMessage)
# from vision import get_text_by_ms
from google.cloud import vision
import base64
import json
import requests

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
API_KEY = os.environ["GOOGLE_API_KEY"]

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
        print('0')
        image_text = get_text_by_ms(image)
        print('1')
        message = TextSendMessage(text=image_text)
        print('2')
        reply_message(event, message)

    except Exception as e:
        reply_message(event, TextSendMessage(text='エラーが発生しました'))


def reply_message(event, messages):
    line_bot_api.reply_message(
        event.reply_token,
        messages,
    )


def get_text_by_ms(image_url):
    api_url = 'https://vision.googleapis.com/v1/images:annotate?key={}'.format(
        API_KEY)
    print('before open')
    # with open(image_url, "rb") as img:
    #     print('opened')
    #     image_content = base64.b64encode(img.read())
    req_body = json.dumps({
        'requests': [{
            'image': {
                # base64でエンコードしたものjsonにするためdecodeする
                'content': image_url.decode('utf-8')
            },
            'features': [{
                'type': 'TEXT_DETECTION'
            }]
        }]
    })
    print('changed')
    res = requests.post(api_url, data=req_body)
    res_json = res.json()
    labels = res_json['responses'][0]['labelAnnotations']
    return labels

    # if image_url == None and image == None:
    #     return '必要な情報が足りません'

    # if image_url:
    #     image = vision.types.Image()
    #     image.source.image_uri = image_url
    #     response = client.document_text_detection(image=image)
    #     texts = response.full_text_annotation.text
    #     if response.error.message:
    #         raise Exception(
    #             '{}\nFor more info on error messages, check: '
    #             'https://cloud.google.com/apis/design/errors'.format(
    #                 response.error.message))

    # elif image is not None:
    #     image = vision.types.Image()
    #     image.source.image_uri = image_url
    #     response = client.document_text_detection(image=image)
    #     texts = response.full_text_annotation.text

    # return texts


if __name__ == "__main__":
    port = os.environ.get('PORT', 3333)
    app.run(
        host='0.0.0.0',
        port=port,
    )
