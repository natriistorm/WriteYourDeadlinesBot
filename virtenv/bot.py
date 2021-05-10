import config
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
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

user_data = []

BEGIN_STAGE, END_STAGE, EVENT_DESCRIPTION, START_EVENT, END_EVENT, EMAIL = range(6)
ONE, TWO, THREE = range(3)


def start(update: Update, _: CallbackContext) -> int:
    keyboard = [
        [
            InlineKeyboardButton("Добавить событие в календарь", callback_data=str(ONE)),
            InlineKeyboardButton("Просмотреть ближайшие события", callback_data=str(TWO)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Что мне сделать?", reply_markup=reply_markup)
    return FIRST

def one(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_data.append('Add')
    query.edit_message_text(text="Введите название мероприятия")
    return T


def two(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    user_data.append(update.message.text)
    update.message.reply_text(text="Введите описание мероприятия")
    return THIRD


def three(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    user_data.append(update.message.text)
    update.message.reply_text(text="Введите дату начала мероприятия в формате день-месяц-год")
    return FOURTH


def four(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    start_str = update.message.text
    user_data.append(start_str)
    update.message.reply_text(text="Введите дату окончания мероприятия в формате день-месяц-год")
    return SECOND

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

def get_email():
    pass


def main() -> None:
    updater = Updater(config.TOKEN)

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            BEGIN_STAGE: [
                CallbackQueryHandler(one, pattern='^' + str(ONE) + '$'),
                CallbackQueryHandler(checker, pattern='^' + str(TWO) + '$'),
            ],
            END_STAGE: [
                MessageHandler(Filters.text, adder_end)
            ],
            EVENT_DESCRIPTION: [
                MessageHandler(Filters.text, two),
            ],
            START_EVENT: [
                MessageHandler(Filters.text, three)
            ],
            END_EVENT: [
                MessageHandler(Filters.text, four)
            ],
            EMAIL: [
                MessageHandler(Filters.text, get_email)
            ]
        },
        fallbacks=[CommandHandler('start', start)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
