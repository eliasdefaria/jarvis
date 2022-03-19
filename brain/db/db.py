from typing import Text
from peewee import *
from os.path import realpath

db = SqliteDatabase(
    realpath(__file__).replace('db.py', 'jarvis.db'),
    pragmas={
        'foreign_keys': 'on'
    }
)

status_verifier = 'status < 2 AND status > -2'

class JarvisStatus(Model):
    id = AutoField()
    created = TimestampField(utc=True)
    status = SmallIntegerField(constraints=[Check(status_verifier)]) # -1 = ERROR, 0 = OFF, 1 = ON

    class Meta:
        database = db

class Device(Model):
    id = AutoField()
    created = TimestampField(utc=True)
    kasa_device_id = TextField()
    name = TextField()
    ip = TextField()
    type = IntegerField(constraints=[Check('type < 7 AND type > 0')])
    
    class Meta:
        database = db

class Plug(Model):
    id = AutoField()
    created = TimestampField(utc=True)
    name = TextField()
    kasa_device_id = TextField()
    status = SmallIntegerField(constraints=[Check(status_verifier)]) # -1 = ERROR, 0 = OFF, 1 = ON
    device = ForeignKeyField(Device, backref='plugs') # Gives the device model a plugs property w/ backref

    class Meta:
        database = db

class Bulb(Model):
    id = AutoField()
    created = TimestampField(utc=True)
    name = TextField()
    kasa_device_id = TextField()
    status = SmallIntegerField(constraints=[Check(status_verifier)]) # -1 = ERROR, 0 = OFF, 1 = ON
    device = ForeignKeyField(Device, backref='bulbs') # Gives the device model a plugs property w/ backref

    class Meta:
        database = db

def init_db():
    print('Initializing database...')
    db.connect()
    db.drop_tables([ JarvisStatus, Device, Plug, Bulb ])
    db.create_tables([ JarvisStatus, Device, Plug, Bulb ])

if __name__ == '__main__':
    init_db()