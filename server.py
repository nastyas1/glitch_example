from flask import Flask, request
import logging
import json

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

sessionStorage = {}

to_buy = [
    'слон',
    'кролик'
]


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info('Response: %r', request.json)

    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:

        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ],
            'to_buy': 0
        }

        res['response']['text'] = 'Привет! Купи ' + to_buy[sessionStorage[user_id]['to_buy']] + 'a!'
        res['response']['buttons'] = get_suggests(user_id, to_buy[sessionStorage[user_id]['to_buy']])
        return

    if req['request']['original_utterance'].lower() in [
        'ладно',
        'куплю',
        'покупаю',
        'хорошо'
    ]:

        sessionStorage[user_id]['suggests'] = [
            "Не хочу.",
            "Не буду.",
            "Отстань!",
        ]
        if sessionStorage[user_id]['to_buy'] == len(to_buy) - 1:
            res['response']['text'] = to_buy[sessionStorage[user_id]['to_buy']] + 'а можно найти на Яндекс.Маркете!'
            sessionStorage[user_id]['to_buy'] += 1
            res['response']['end_session'] = True
        else:
            res['response']['text'] = to_buy[sessionStorage[user_id]['to_buy']] + 'а можно найти на Яндекс.Маркете!'
            sessionStorage[user_id]['to_buy'] += 1
            res['response']['text'] += ' А ' + to_buy[sessionStorage[user_id]['to_buy']] + 'a купишь? '
            res['response']['buttons'] = get_suggests(user_id, to_buy[sessionStorage[user_id]['to_buy']])
        return

    res['response']['text'] = ('Все говорят "%s", а ты купи ' + to_buy[sessionStorage[user_id]['to_buy']] + 'а!') % (
        req['request']['original_utterance']
    )
    res['response']['buttons'] = get_suggests(user_id, to_buy[sessionStorage[user_id]['to_buy']])


def get_suggests(user_id, to_buy):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session


    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=" + to_buy,
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    app.run()
