import requests
import os

KEY1 = os.environ["COMPUTER_VISION_API_KEY"]

endpoint = 'https://eastasia.api.cognitive.microsoft.com/vision/v1.0/ocr'


def get_text(image):

    params = {'visualFeatures': 'Categories,Description,Color'}

    if image != None:
        headers = {
            'Ocp-Apim-Subscription-Key': KEY1,
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

    if len(text) == 0:
        text += '文字が検出できませんでした'

    print('text:', text)
    return text
