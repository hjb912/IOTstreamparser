import datetime
import asyncio
from torpeewee import *


def get_db_instance():
    return MySQLDatabase("voter", host="127.0.0.1", port=3306, user="root", passwd="")


class BaseModel(Model):
    class Meta:
        database = get_db_instance()


class VoterModel(BaseModel):

    id = IntegerField(primary_key= True)
    user_id = IntegerField(default=0)
    quest_id = IntegerField(default=0)
    item_id = IntegerField(default=0)
    enabled = IntegerField(default=0)
    create_time = DateTimeField()
    update_time = DateTimeField()

    class Meta:
        table_name = 't_vote'

