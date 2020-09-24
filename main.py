import json
import logging
import os

from viberbot import Api
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.keyboard_message import KeyboardMessage
from viberbot.api.messages.message import Message

from flask import Flask, request, Response

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

START = {KEY_ACTION_TYPE: "start",
         KEY_TEXT: "Начать"}

NEWS = {KEY_ACTION_TYPE: "news",
        KEY_TEXT: "Новости ЦМИТ"}


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
        "ActionBody": "Назад",
        "Text": "Назад"
    })

    return buttons


START_KEYBOARD = {
    "Type": "keyboard",
    "Buttons": [{
        "Columns": 6,
        "Rows": 1,
        "BgColor": "#FFFFFF",
        "ActionType": "reply",
        "ActionBody": START.get(KEY_TEXT),
        "Text": START.get(KEY_TEXT)
    },
        {
            "Columns": 6,
            "Rows": 1,
            "BgColor": "#FFFFFF",
            "ActionType": "reply",
            "ActionBody": NEWS.get(KEY_TEXT),
            "Text": NEWS.get(KEY_TEXT)
        }]
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
    messages = []
    keyboard = ""
    reply_message = ""
    if text == START.get(KEY_ACTION_TYPE):
        keyboard = TIMETABLE_KEYBOARD
        reply_message = NEWS.get(KEY_TEXT)
    elif text == NEWS.get(KEY_ACTION_TYPE):
        keyboard = START_KEYBOARD
        reply_message = NEWS.get(KEY_TEXT)

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

    messages.append(TextMessage(keyboard=keyboard, text=reply_message))

    return messages


@app.route('/', methods=['POST'])
def incoming():
    logger.debug("Recieve request. Post data: {0}".format(request.get_data()))
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    viber_request = viber.parse_request(request.get_data())

    if isinstance(viber_request, ViberMessageRequest):
        print("message.tracking_data: {0}, message.action_body{1}".format(viber_request.message.tracking_data,
                                                                          viber_request.message.text))

        viber.send_messages(viber_request.sender.id, get_messages(viber_request.message))
    elif isinstance(viber_request, ViberSubscribedRequest):
        viber.send_messages(viber_request.user.id, [TextMessage(text=HELLO_MESSAGE, keyboard=START_KEYBOARD)])
    elif isinstance(viber_request, ViberFailedRequest):
        logger.warn("Client failed receiving message. Failure: {0}".format(viber_request))

    return Response(status=200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
