import os
import peewee


# DB CONNECTION
DB = peewee.PostgresqlDatabase(
    'putio_bot',
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASS'],
    host='localhost',
    port=5432,
    autorollback=True,
)


class BaseDatabaseModel(peewee.Model):
    """
        Base database model
        to prevent DRY for 'class Meta:'
    """
    class Meta:
        database = DB


class User(BaseDatabaseModel):
    """
        User Model for database.
        It contains users that using the bot
    """
    telegram_id = peewee.IntegerField(unique=True)
    first_name = peewee.CharField(max_length=100)
    last_name = peewee.CharField(max_length=100, null=True)
    username = peewee.CharField(max_length=40, null=True)
    user_dir = peewee.IntegerField()
    active_dir = peewee.CharField(null=True)
