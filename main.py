import logging
import os
from threading import Thread

from viberbot import Api
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.keyboard_message import KeyboardMessage
from viberbot.api.messages.message import Message
from viberbot.api.messages.url_message import URLMessage

from flask import Flask, request, Response

import schedule
import time

user_ids = []

KEY_ACTION_TYPE = "action_type"
KEY_TEXT = "text"

BACK = {
    KEY_ACTION_TYPE: "back",
    KEY_TEXT: "Назад"
}

DAY_OF_WEAK = [
    {KEY_ACTION_TYPE: "monday",
     KEY_TEXT: "Понедельник"},
    {KEY_ACTION_TYPE: "tuesday",
     KEY_TEXT: "Вторник"},
    {KEY_ACTION_TYPE: "wednesday",
     KEY_TEXT: "Среда"},
    {KEY_ACTION_TYPE: "thursday",
     KEY_TEXT: "Четверг"},
    {KEY_ACTION_TYPE: "friday",
     KEY_TEXT: "Пятница"},
    {KEY_ACTION_TYPE: "saturday",
     KEY_TEXT: "Суббота"},
    {KEY_ACTION_TYPE: "sunday",
     KEY_TEXT: "Воскресенье"},
]

TIMETABLE = {KEY_ACTION_TYPE: "timetable",
             KEY_TEXT: "Расписание"}

NEWS = {KEY_ACTION_TYPE: "news",
        KEY_TEXT: "Новости ЦМИТ"}

PAY_NOW = {KEY_ACTION_TYPE: "pay_now",
           KEY_TEXT: "Оплатить сейчас"}

PAY_LATE = {KEY_ACTION_TYPE: "pay_late",
            KEY_TEXT: "Оплатить позже"}


def get_timetable_buttons():
    buttons = []
    for day_of_weak in DAY_OF_WEAK:
        if day_of_weak.get(KEY_ACTION_TYPE) == DAY_OF_WEAK[6].get(KEY_ACTION_TYPE):
            break
        buttons.append({
            "Columns": 3,
            "Rows": 1,
            "BgColor": "#FFFFFF",
            "ActionType": "reply",
            "ActionBody": day_of_weak.get(KEY_ACTION_TYPE),
            "Text": day_of_weak.get(KEY_TEXT)
        })

    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "BgColor": "#FFFFFF",
        "ActionType": "reply",
        "ActionBody": DAY_OF_WEAK[6].get(KEY_ACTION_TYPE),
        "Text": DAY_OF_WEAK[6].get(KEY_TEXT)
    })

    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "BgColor": "#FFFFFF",
        "ActionType": "reply",
        "ActionBody": BACK.get(KEY_ACTION_TYPE),
        "Text": BACK.get(KEY_TEXT)
    })

    return buttons


START_KEYBOARD = {
    "Type": "keyboard",
    "Buttons": [{
        "Columns": 6,
        "Rows": 1,
        "BgColor": "#FFFFFF",
        "ActionType": "reply",
        "ActionBody": TIMETABLE.get(KEY_ACTION_TYPE),
        "Text": TIMETABLE.get(KEY_TEXT)
    },
        {
            "Columns": 6,
            "Rows": 1,
            "BgColor": "#FFFFFF",
            "ActionType": "reply",
            "ActionBody": NEWS.get(KEY_ACTION_TYPE),
            "Text": NEWS.get(KEY_TEXT)
        },
        {
            "Columns": 6,
            "Rows": 1,
            "BgColor": "#FFFFFF",
            "ActionType": "reply",
            "ActionBody": PAY_NOW.get(KEY_ACTION_TYPE),
            "Text": PAY_NOW.get(KEY_TEXT)
        },
        {
            "Columns": 6,
            "Rows": 1,
            "BgColor": "#FFFFFF",
            "ActionType": "reply",
            "ActionBody": PAY_LATE.get(KEY_ACTION_TYPE),
            "Text": PAY_LATE.get(KEY_TEXT)
        }
    ]
}

TIMETABLE_KEYBOARD = {
    "Type": "keyboard",
    "Buttons": get_timetable_buttons()
}

bot_configuration = BotConfiguration(
    name="CmitUgraBot",
    avatar="",
    auth_token="4a94130713a7d0bb-3633cc6c70d45392-94364c0dd093822"
)

viber = Api(bot_configuration)

app = Flask(__name__)

logger = logging.getLogger()

HELLO_MESSAGE = "Вас приветствует цифровой помощник ЦМИТа Вертикаль.\nДля начала взаимодействия нажмите кнопку начать"


def get_messages(message: Message):
    text = message.text
    if text == TIMETABLE.get(KEY_ACTION_TYPE):
        keyboard = TIMETABLE_KEYBOARD
        reply_message = None
    elif text == NEWS.get(KEY_ACTION_TYPE):
        keyboard = START_KEYBOARD
        reply_message = NEWS.get(KEY_TEXT)
    elif text == PAY_NOW.get(KEY_ACTION_TYPE):
        keyboard = START_KEYBOARD
        reply_message = PAY_NOW.get(KEY_TEXT)
    elif text == PAY_LATE.get(KEY_ACTION_TYPE):
        keyboard = START_KEYBOARD
        reply_message = "Здесь должны быть реквизиты"

    elif text == DAY_OF_WEAK[0].get(KEY_ACTION_TYPE):
        keyboard = TIMETABLE_KEYBOARD
        reply_message = DAY_OF_WEAK[0].get(KEY_TEXT)
    elif text == DAY_OF_WEAK[1].get(KEY_ACTION_TYPE):
        keyboard = TIMETABLE_KEYBOARD
        reply_message = DAY_OF_WEAK[1].get(KEY_TEXT)
    elif text == DAY_OF_WEAK[2].get(KEY_ACTION_TYPE):
        keyboard = TIMETABLE_KEYBOARD
        reply_message = DAY_OF_WEAK[2].get(KEY_TEXT)
    elif text == DAY_OF_WEAK[3].get(KEY_ACTION_TYPE):
        keyboard = TIMETABLE_KEYBOARD
        reply_message = DAY_OF_WEAK[3].get(KEY_TEXT)
    elif text == DAY_OF_WEAK[4].get(KEY_ACTION_TYPE):
        keyboard = TIMETABLE_KEYBOARD
        reply_message = DAY_OF_WEAK[4].get(KEY_TEXT)
    elif text == DAY_OF_WEAK[5].get(KEY_ACTION_TYPE):
        keyboard = TIMETABLE_KEYBOARD
        reply_message = DAY_OF_WEAK[5].get(KEY_TEXT)
    elif text == DAY_OF_WEAK[6].get(KEY_ACTION_TYPE):
        keyboard = TIMETABLE_KEYBOARD
        reply_message = DAY_OF_WEAK[6].get(KEY_TEXT)
    elif text == BACK.get(KEY_ACTION_TYPE):
        keyboard = START_KEYBOARD
        reply_message = None

    else:
        keyboard = START_KEYBOARD
        reply_message = HELLO_MESSAGE

    if reply_message is None:
        return [KeyboardMessage(keyboard=keyboard)]
    elif reply_message == PAY_NOW.get(KEY_TEXT):
        print("here")
        return [URLMessage(keyboard=keyboard, media="https://www.google.com")]
    else:
        return [TextMessage(text=reply_message, keyboard=keyboard)]


def mailing():
    for user_id in user_ids:
        viber.send_messages(user_id, [TextMessage(keyboard=START_KEYBOARD, text="Тест авторассылки")])


schedule.every().minutes.do(mailing)


def schedule_mailing():
    while True:
        schedule.run_pending()
        time.sleep(1)


thread = Thread(target=schedule_mailing)
thread.start()


@app.route('/', methods=['POST'])
def incoming():
    print(thread.is_alive())
    logger.debug("Recieve request. Post data: {0}".format(request.get_data()))
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    viber_request = viber.parse_request(request.get_data())

    if isinstance(viber_request, ViberMessageRequest):
        print("message.tracking_data: {0}, message.action_body{1}".format(viber_request.message.tracking_data,
                                                                          viber_request.message.text))
        if viber_request.sender.id not in user_ids:
            user_ids.append(viber_request.sender.id)

        viber.send_messages(viber_request.sender.id, get_messages(viber_request.message))
    elif isinstance(viber_request, ViberSubscribedRequest):
        viber.send_messages(viber_request.user.id, [TextMessage(text=HELLO_MESSAGE, keyboard=START_KEYBOARD)])
    elif isinstance(viber_request, ViberFailedRequest):
        logger.warn("Client failed receiving message. Failure: {0}".format(viber_request))

    return Response(status=200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
