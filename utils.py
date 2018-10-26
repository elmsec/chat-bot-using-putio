from functools import wraps
from database import User


# decorator for functions need user_data
def required_user_data(f):
    @wraps(f)
    def wrapped(bot, update, user_data, *args, **kwargs):
        if not user_data:
            # get user data
            user = User.select().where(
                User.telegram_id == update.effective_user.id).first()

            if user:
                user_data[user.telegram_id] = user
            else:
                update.message.reply_text(
                    'Something went wrong. Please try to use /start'
                )
                return False

        # run the function
        r = f(bot, update, user_data, *args, **kwargs)
        return r
    return wrapped


# makes bytes more human readable
# eg: 10000000000 > 9.3 GB
def human_readable_bytes(bytes):
        KB = 1024
        MB = 1024 * 1024
        GB = MB * 1024

        if bytes >= KB and bytes < MB:
            result = bytes / KB
            converted = 'KB'
        elif bytes >= MB and bytes < GB:
            result = bytes / MB
            converted = 'MB'
        elif bytes >= GB:
            result = bytes / GB
            converted = 'GB'
        else:
            result = bytes
            converted = 'byte'

        result = "%.1f" % result
        results = (
            str(result) + ' ' + converted,
            result,
            converted
        )

        return results
