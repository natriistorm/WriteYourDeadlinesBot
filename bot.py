import temp
import users_emails
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, User
from telegram.ext import (
    CallbackQueryHandler,
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
import calendartest
import os
PORT = int(os.environ.get('PORT', '8443'))

BEGIN_STAGE, END_STAGE, EVENT_DESCRIPTION, START_EVENT, END_EVENT, EMAIL = range(6)
user_data = []


def get_email(update: Update, _: CallbackContext, user_id):
    user_message = update.message.from_user
    update.message.reply_text(text="Введи ID твоего календаря")
    hand_email(update, _, user_id)


def hand_email(update: Update, _: CallbackContext, user_id):
    user_message = update.message.from_user
    users_emails.users[user_id] = update.message.text
    user_data.append(update.message.text)
    update.message.reply_text(text="Подключаюсь..")


def start(update: Update, _: CallbackContext) -> int:
    user_id = update.message.chat_id
    user_data.clear()
    if user_id not in users_emails.users:
        get_email(update, _, user_id)
    else:
        user_data.append(users_emails.users[user_id])
    keyboard = [
        [
            InlineKeyboardButton("Добавить событие в календарь", callback_data=str(1)),
            InlineKeyboardButton("Просмотреть ближайшие события", callback_data=str(2)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Что мне сделать?", reply_markup=reply_markup)
    return BEGIN_STAGE


def name(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_data.append('Add')
    query.edit_message_text(text="Введите название мероприятия")
    return EVENT_DESCRIPTION


def description(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    user_data.append(update.message.text)
    update.message.reply_text(text="Введите описание мероприятия")
    return START_EVENT


def start_event(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    user_data.append(update.message.text)
    update.message.reply_text(text="Введите дату начала мероприятия в формате день-месяц-год")
    return END_EVENT


def end_event(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    start_str = update.message.text
    user_data.append(start_str)
    update.message.reply_text(text="Введите дату окончания мероприятия в формате день-месяц-год")
    return END_STAGE


def checker(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_data.append('Check')
    calendar = calendartest.GoogleCalendar(user_data)
    query.edit_message_text(text=calendar.answer)
    return ConversationHandler.END


def adder_end(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    user_data.append(update.message.text)
    calendartest.GoogleCalendar(user_data)
    update.message.reply_text(text="Готово!")
    return ConversationHandler.END


def main() -> None:

    updater = Updater(temp.TOKEN)

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            BEGIN_STAGE: [
                CallbackQueryHandler(name, pattern='^' + str(1) + '$'),
                CallbackQueryHandler(checker, pattern='^' + str(2) + '$'),
            ],
            END_STAGE: [
                MessageHandler(Filters.text, adder_end)
            ],
            EVENT_DESCRIPTION: [
                MessageHandler(Filters.text, description),
            ],
            START_EVENT: [
                MessageHandler(Filters.text, start_event)
            ],
            END_EVENT: [
                MessageHandler(Filters.text, end_event)
            ],
            EMAIL: [
                MessageHandler(Filters.text, hand_email)
            ]
        },
        fallbacks=[CommandHandler('start', start)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=temp.TOKEN,
                          webhook_url='https://writeyourdeadlinesbot.herokuapp.com/' + temp.TOKEN)

    updater.idle()


if __name__ == '__main__':
    main()
