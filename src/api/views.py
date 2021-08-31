from flask_restful import Resource, reqparse, abort
from flask import jsonify
from src.api.models import TaskModel, TaskSchema
from src.database import db


class TaskListAPI(Resource):
  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('title', required=True)
    self.reqparse.add_argument('done', required=True)
    super(TaskListAPI, self).__init__()


  def get(self):
    results = TaskModel.query.all()
    jsonData = TaskSchema(many=True).dump(results).data
    return jsonify({'items': jsonData})


  def post(self):
    args = self.reqparse.parse_args()
    task = TaskModel(args.title, args.done)
    db.session.add(task)
    db.session.commit()
    res = TaskSchema().dump(task).data
    return res, 201


class TaskAPI(Resource):
  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('title')
    self.reqparse.add_argument('done')
    super(TaskAPI, self).__init__()


  def get(self, id):
    task = db.session.query(TaskModel).filter_by(id=id).first()
    if task is None:
      abort(404)

    res = TaskSchema().dump(task).data
    return res


  def put(self, id):
    task = db.session.query(TaskModel).filter_by(id=id).first()
    if task is None:
      abort(404)
    args = self.reqparse.parse_args()
    for title, done in args.items():
      if done is not None:
        setattr(task, title, done)
    db.session.add(task)
    db.session.commit()
    res = TaskSchema().dump(task).data
    return res, 204


  def delete(self, id):
    task = db.session.query(TaskModel).filter_by(id=id).first()
    if task is not None:
      db.session.delete(task)
      db.session.commit()
    return None, 204

