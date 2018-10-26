import os
import logging
import putiopy
from database import User
from menus import MAIN_MENU, FILES_MENU
from utils import human_readable_bytes, required_user_data
from telegram import InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    # ConversationHandler,
    # MessageHandler,
    # Filters,
    # RegexHandler,
)

# LOGGER for warnings, errors, debug outputs etc.
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

# fundamentals
logger = logging.getLogger(__name__)
bot_token = os.environ['BOT_TOKEN']
client = putiopy.Client(os.environ['PUT_IO_TOKEN'])

# put.io folder to collect user files (/BOT_USERS/)
USERS_DIR_ID = 556581296


# catch errors
def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


# /start function
def start(bot, update, user_data):
    # create user instance in the db if doesn't exist
    markup = InlineKeyboardMarkup(MAIN_MENU)
    user = User.select().where(User.telegram_id == update.effective_user.id)
    user = user.first() or False

    # create new user from update
    if not user:
        try:
            # but before, we need to create a folder for user
            create_dir = client.File.create_folder(
                name=update.effective_user.id, parent_id=USERS_DIR_ID)

            # then create a user
            if create_dir:
                user = User.create(
                    telegram_id=update.effective_user.id,
                    first_name=update.effective_user.first_name,
                    last_name=update.effective_user.last_name,
                    username=update.effective_user.username,
                    user_dir=create_dir.id,
                )

            # greeting
            if user:
                message = (
                    "New user added to the DB. Welcome message "
                    "will be placed here.")
        except Exception as e:
            # sure we could check for specific putio errors but it has no
            # specific errors. it just returns client error if something goes
            # wrong
            logger.error(e)
            message = "There is something wrong. Please try again later."
            markup = None

    else:
        # user already exist
        message = "Greeting message for the existing user."

    # send the message
    update.message.reply_text(
        message,
        reply_markup=markup,
    )

    user_data[update.effective_user.id] = user or None


# main menu
def main_menu(bot, update, user_data):
    callback = update.callback_query
    markup = InlineKeyboardMarkup(MAIN_MENU)

    callback.message.edit_text(
        "Sample text for main menu with inline buttons.",
        reply_markup=markup,
    )


# menu to list files
@required_user_data
def menu_files(bot, update, user_data):
    # TODO: Pagination

    user = user_data[update.effective_user.id]
    callback = update.callback_query
    markup = InlineKeyboardMarkup(FILES_MENU)

    try:
        files = client.File.list(parent_id=user.user_dir)
    except Exception as e:
        logger.error(e)

    file_list = ''
    folder_list = ''
    for f in files:
        size = human_readable_bytes(f.size)[0]

        if f.file_type.upper() != 'FOLDER':
            # if the file type is not "FOLDER"
            file_list += (
                "<code>{}</code> "      # FILE ID
                "<a href='{}'>{}</a> "  # FILE LINK AND NAME
                "<b>{}</b>"             # FILE SIZE
                "".format(f.id, '#', f.name, size)
            )
            file_list += '\n'
        else:
            # the case if the file type is equal to "FOLDER"
            folder_list += (
                "<code>{}</code> "      # FOLDER ID
                "<a href='{}'>{}</a> "  # FOLDER LINK AND NAME
                "<b>{}</b>"             # FOLDER SIZE
                "".format(f.id, '#', f.name, size)
            )
            folder_list += '\n'

    message = (
        "The message of the files menu which presents the files of the user."
        "\n\n"
        "<b>FILES</b>\n{}\n\n"
        "<b>FOLDERS</b>\n{}\n\n".format(file_list, folder_list)
    )

    callback.message.edit_text(
        message,
        reply_markup=markup,
        disable_web_page_preview=True,
        parse_mode='HTML',
    )


# definition to do some tests
@required_user_data
def test_case(bot, update, user_data):
    update.message.reply_text('TEST CASE.')


def main():
    updater = Updater(bot_token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler(
        'start',
        start,
        pass_user_data=True,
        ))

    dp.add_handler(CommandHandler(
        'test',
        test_case,
        pass_user_data=True,
        ))

    dp.add_handler(CallbackQueryHandler(
        main_menu,
        pattern='^main$',
        pass_user_data=True
        ))

    dp.add_handler(CallbackQueryHandler(
        menu_files,
        pattern='^files$',
        pass_user_data=True
        ))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
