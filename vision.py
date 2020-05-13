import requests
import os
from google.cloud import vision

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]


def get_text_by_ms(image_url=None, image=None):
    client = vision.ImageAnnotatorClient()
    if image_url == None and image == None:
        return '必要な情報が足りません'

    if image_url:
        image = vision.types.Image()
        image.source.image_uri = image_url
        response = client.document_text_detection(image=image)
        texts = response.full_text_annotation.text
        # for text in texts:
        #     print('\n"{}"'.format(text.description))

        #     vertices = (['({},{})'.format(vertex.x, vertex.y)
        #                  for vertex in text.bounding_poly.vertices])

        # print('bounds: {}'.format(','.join(vertices)))
        # value = '{}'.format(','.join(vertices))

        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))

    elif image is not None:
        image = vision.types.Image()
        image.source.image_uri = image_url
        response = client.document_text_detection(image=image)
        texts = response.full_text_annotation.text

    return texts

    # status = response.status_code
    # data = response.json()

    # if status != 200:

    #     if data['code'] == 'InvalidImageSize':
    #         text = '画像のサイズが大きすぎます'

    #     elif data['code'] == 'InvalidImageUrl':
    #         text = 'この画像URLからは取得できません'

    #     elif data['code'] == 'InvalidImageFormat':
    #         text = '対応していない画像形式です'

    #     else:
    #         text = 'エラーが発生しました'

    #     print(status, data)
    #     return text

    # text = ''
    # for region in data['regions']:
    #     for line in region['lines']:
    #         for word in line['words']:
    #             text += word.get('text', '')
    #             if data['language'] != 'ja':
    #                 text += ' '
    #     text += '\n'

    # if len(text) == 0:
    #     text += '文字が検出できませんでした'

    # print('text:', text)


if __name__ == "__main__":
    get_text_by_ms(image_url)
