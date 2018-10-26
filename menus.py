from telegram import InlineKeyboardButton


MAIN_MENU = [
    [
        InlineKeyboardButton('📁 Files', callback_data='files'),
        InlineKeyboardButton('...', callback_data='...'),
    ],
]

FILES_MENU = [
    [
        InlineKeyboardButton('⬅️ Previous', callback_data='files:previous'),
        InlineKeyboardButton('➡️ Next', callback_data='files:next'),
    ],
    [
        InlineKeyboardButton('🔙 Back', callback_data='main'),
    ],
]
