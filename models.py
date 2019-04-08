from datetime import datetime

from peewee import Model, SqliteDatabase, TextField, DateTimeField

db = SqliteDatabase('db.sqlite3')
# db = PostgresqlDatabase()


class BaseModel(Model):
    class Meta:
        database = db


class Address(BaseModel):
    email = TextField()
    save_datetime = DateTimeField(default=datetime.now)


class Email(BaseModel):
    subject = TextField()
    text = TextField()

