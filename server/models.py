from settings import POSTGRES_URI
from peewee import Model, CharField, TextField, DateTimeField, IntegerField, FloatField, BooleanField, AutoField
from playhouse.db_url import connect
import datetime
import json
import os

# database = connect(os.environ.get("POSTGRES_URI") or "sqlite:///tweepee.db")
DEBUG = True
database = connect(POSTGRES_URI)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()

        return super().default(o)

# model definitions -- the standard "pattern" is to define a base model class
# that specifies which database to use.  then, any subclasses will automatically
# use the correct storage. for more information, see:
# http://charlesleifer.com/docs/peewee/peewee/models.html#model-api-smells-like-django


class BaseModel(Model):
    class Meta:
        database = database

# the user model specifies its fields (or columns) declaratively, like django


class Media(BaseModel):
    media_id = AutoField()
    media_type = CharField()
    name = CharField()
    s3_id = CharField()
    date_added = DateTimeField(default=datetime.datetime.now)
    presigned_url = CharField()

    @property
    def serialize(self):
        data = {
            "name": self.name,
            "media_type": self.media_type,
            "s3_id": self.s3_id,
            "date_added": self.date_added.isoformat(),
            "presigned_url": self.presigned_url,
        }
        return data


class Image(Media):
    original_url = TextField()
    nasa_date = DateTimeField()

    @property
    def serialize(self):
        data = {
            "name": self.name,
            "media_type": self.media_type,
            "original_url": self.original_url,
            "s3_id": self.s3_id,
            "nasa_date": self.date_added.isoformat(),
            "date_added": self.date_added.isoformat(),
        }
        return data


class Weather(BaseModel):
    pass

# simple utility function to create tables


def create_tables():
    with database:
        try:
            database.create_tables([Media, Image], safe=True)
        except Exception as e:
            print(e)
            pass


# allow running from the command line
if __name__ == "__main__":
    create_tables()
