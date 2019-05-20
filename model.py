import datetime
import asyncio
from torpeewee import *
from settings import DB_HOST, DB_NAME, DB_PORT, DB_USER, DB_PASSWD


def get_db_instance():
    return MySQLDatabase(
        DB_NAME,
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        passwd=DB_PASSWD
    )


class BaseModel(Model):
    class Meta:
        database = get_db_instance()


class SensorDataModel(BaseModel):
    id = IntegerField(primary_key=True)
    pm2d5 = IntegerField(default=0, help_text='pm2.5, ug/m3'),
    pm10 = IntegerField(default=0, help_text='pm 10'),
    noise = IntegerField(default=0, help_text='噪声, dB'),
    temperature = IntegerField(default=0, help_text='温度, 摄氏度, 补码标示负数'),
    humidity = IntegerField(default=0, help_text='湿度, RH %'),
    wind_direction = IntegerField(default=0, help_text='风向'),
    wind_speed = IntegerField(default=0, help_text='风速, m/s'),
    air_pressure = IntegerField(default=0, help_text='气压, kpa'),
    dust = IntegerField(default=0, help_text='扬尘, ug/m3'),

    create_time = DateTimeField()
    update_time = DateTimeField()

    class Meta:
        table_name = 't_sensor_data'
