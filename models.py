from datetime import datetime

from peewee import Model, SqliteDatabase, TextField, DateTimeField, ForeignKeyField, DateField

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
    _datetime = DateTimeField(default=datetime.now)
    _date = DateField(default=datetime.now().date)


class Launch(BaseModel):
    email = ForeignKeyField(Email, backref='launches')
    _datetime = DateTimeField(default=datetime.now)


