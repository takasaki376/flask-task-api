from datetime import datetime
# from flask_marshmallow import Marshmallow
# from marshmallow_sqlalchemy import ModelSchema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_marshmallow.fields import fields
from sqlalchemy_utils import UUIDType
from database import db

import uuid

# ma = Marshmallow()


class TaskModel(db.Model):
  __tablename__ = 'tasks'

  id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
  title = db.Column(db.String(255), nullable=False)
  done = db.Column(db.Boolean, nullable=False)

  createAt = db.Column(db.DateTime, nullable=False, default=datetime.now)
  updateAt = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

  def __init__(self, title, done):
    self.title = title
    self.done = done


  def __repr__(self):
    return '<TaskModel {}:{}>'.format(self.id, self.title)


# class TaskSchema(ma.ModelSchema):
class TaskSchema(SQLAlchemyAutoSchema):
  class Meta:
    model = TaskModel
    load_instance = True

  createAt = fields.DateTime('%Y-%m-%dT%H:%M:%S')
  updateAt = fields.DateTime('%Y-%m-%dT%H:%M:%S')
