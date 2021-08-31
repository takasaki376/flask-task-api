from flask import Flask, jsonify
from flask_restful import Api
from database import init_db
from src.api.views import TaskListAPI, TaskAPI


def create_app():

  app = Flask(__name__)
  app.config.from_object('config.Config')

  init_db(app)

  api = Api(app)
  api.add_resource(TaskListAPI, '/task')
  api.add_resource(TaskAPI, '/task/<id>')

  return app


app = create_app()

