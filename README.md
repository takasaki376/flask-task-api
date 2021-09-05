# 参考

[Python の Flask で MySQL を利用した RESTful な API を Docker 環境で実装する](https://qiita.com/kai_kou/items/5d73de21818d1d582f00)

# 実行環境について

Windows10 PowerShell

```
> docker --version
Docker version 20.10.7, build f0df350
> docker-compose --version
docker-compose version 1.29.2, build 5becea4c
```

# MySQL 環境を作成する。

## docker-compose.yaml 作成

docker-compose の定義ファイル。この中で、Dockerfile を呼び出して、Docker コンテナのビルドを行います。

```
version: "3"
services:
  db:
    build: ./mysql/
    volumes:
      - ./mysql/mysql_data:/var/lib/mysql             # データの永続化
      - ./mysql/sqls:/docker-entrypoint-initdb.d      # 初期化時に実行するSQL
    environment:
      - MYSQL_ROOT_PASSWORD=hoge # パスワードだけど、ローカルなので、
```

## mysql/Dockerfile 作成

```
FROM mysql
EXPOSE 3306

ADD ./my.cnf /etc/mysql/conf.d/my.cnf # 設定ファイルの読み込み

CMD ["mysqld"]
```

## 文字コードの設定 mysql/my.cnf 作成

```
[mysqld]
character-set-server=utf8
[mysql]
default-character-set=utf8
[client]
default-character-set=utf8
```

## database 初期化 mysql/sqls/initialize.sql 作成

```
CREATE DATABASE todo;
use todo;
```

## 動作確認

`cd [docker-compose.yamlの格納フォルダ]`

### build

`docker-compose build db`

```
Building db
[+] Building 2.8s (7/7) FINISHED
 => [internal] load build definition from Dockerfile                                                               0.0s
 => => transferring dockerfile: 31B                                                                                0.0s
 => [internal] load .dockerignore                                                                                  0.0s
 => => transferring context: 2B                                                                                    0.0s
 => [internal] load metadata for docker.io/library/mysql:latest                                                    2.6s
 => [internal] load build context                                                                                  0.0s
 => => transferring context: 27B                                                                                   0.0s
 => [1/2] FROM docker.io/library/mysql@sha256:d45561a65aba6edac77be36e0a53f0c1fba67b951cb728348522b671ad63f926     0.0s
 => CACHED [2/2] ADD ./my.cnf /etc/mysql/conf.d/my.cnf                                                             0.0s
 => exporting to image                                                                                             0.0s
 => => exporting layers                                                                                            0.0s
 => => writing image sha256:c8e82494a4c85407e9e1d89d81b1bcd9d9c1823344978523cf5afa23c46aed9c                       0.0s
 => => naming to docker.io/library/flask-task-api_db                                                               0.0s

Use 'docker scan' to run Snyk tests against images to find vulnerabilities and learn how to fix them
```

### 起動

`docker-compose build up -d db`

```
Recreating flask-task-api_db_1 ... done
```

### DB 接続

`docker-compose exec db mysql -u root -p`

```
Enter password:
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 8
Server version: 8.0.26 MySQL Community Server - GPL

Copyright (c) 2000, 2021, Oracle and/or its affiliates.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.
mysql>
```

### データベース確認

`show databases;`

```
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| sys                |
| todo               |
+--------------------+
5 rows in set (0.00 sec)
```

### データベース切断

```
mysql> exit
Bye
```

# Flask の設定

## docker-compose.yaml 修正

```
version: "3"
services:
  api:
    build: .
    ports:
      - 127.0.0.1:5000:5000
    volumes:
      - .dockervenv:/src/.venv
      - ./src:/src
    tty: true
    links:
      - db
    expose:
      - 5000                       # このポートをLISTEN状態にする
    environment:
      TZ: Asia/Tokyo
      FLASK_APP: ./run.py
      FLASK_ENV: development
      PYTHONPATH: /src
  db:
    build: ./mysql/
    volumes:
      - ./mysql/mysql_data:/var/lib/mysql             # データの永続化
      - ./mysql/sqls:/docker-entrypoint-initdb.d      # 初期化時に実行するSQL
    environment:
      - MYSQL_ROOT_PASSWORD=hoge                      # パスワード設定（ローカル環境でしか使用しない）
      - TZ='Asia/Tokyo'                              # タイムゾーンを日本時間に設定
    ports:
      - 33306:3306                                    # ホストマシンのポート33306を、docker内のポート3306に接続する
```

- Dockerfile 作成
  Docker の定義ファイル。利用する公開イメージ（今回は Python 3.8 がインストールされた OS イメージ）を取得し、
  poetry によって、パッケージ定義ファイルである pyproject.toml を元に各 python パッケージをインストールします。

```
# python3.8のイメージをダウンロード
FROM python:3.8
ENV PYTHONUNBUFFERED=1
EXPOSE 5000

ARG project_dir=/src/
WORKDIR $project_dir

# VS Code Remote Containerを使う場合はGitをコンテナ内にインストールすることを推奨
RUN apt-get update && apt-get install -y \
    git \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# pipを使ってpoetryをインストール
RUN pip install poetry

# poetryの定義ファイルをコピー (存在する場合)
COPY src/pyproject.toml* src/poetry.lock* ./

# poetryでライブラリをインストール (pyproject.tomlが既にある場合)
RUN poetry config virtualenvs.in-project true
RUN if [ -f pyproject.toml ]; then poetry install; fi

# サーバーを立ち上げる
ENTRYPOINT ["poetry", "run", "flask", "run" ,"--host", "0.0.0.0", "--port=8000"]
```

## AP サーバ　イメージのビルド

`docker-compose build api`

コマンド実行結果

```
Building api
[+] Building 26.6s (11/11) FINISHED
 => [internal] load build definition from Dockerfile                                                               0.4s
 => => transferring dockerfile: 552B                                                                               0.0s
 => [internal] load .dockerignore                                                                                  0.5s
 => => transferring context: 2B                                                                                    0.0s
 => [internal] load metadata for docker.io/library/python:3.9-buster                                               0.0s
 => [1/6] FROM docker.io/library/python:3.9-buster                                                                 0.0s
 => [internal] load build context                                                                                  0.4s
 => => transferring context: 2B                                                                                    0.1s
 => CACHED [2/6] WORKDIR /src/                                                                                     0.0s
 => [3/6] RUN pip install poetry                                                                                  23.3s
 => [4/6] COPY pyproject.toml* poetry.lock* ./                                                                     0.1s
 => [5/6] RUN poetry config virtualenvs.in-project true                                                            1.2s
 => [6/6] RUN if [ -f pyproject.toml ]; then poetry install; fi                                                    0.6s
 => exporting to image                                                                                             0.6s
 => => exporting layers                                                                                            0.6s
 => => writing image sha256:6436ccf99e9b6d6e47d9f2fa44676d35dcdfd25b26fed40a0f8ce9c300d215fc                       0.0s
 => => naming to docker.io/library/fast-task-api_api                                                               0.0s

Use 'docker scan' to run Snyk tests against images to find vulnerabilities and learn how to fix them
```

## poetry による Python 環境のセットアップ

```
docker-compose run --entrypoint "poetry init --name task-api --dependency flask --dependency flask-restful --dependency flask_marshmallow --dependency marshmallow-sqlalchemy --dependency flask-sqlalchemy --dependency sqlalchemy_utils --dependency flask-migrate --dependency pymysql --dependency cryptography --dependency gunicorn" api
```

コマンド実行結果
Author のみ"n"を入力するが、それ以外は何も入力せずに Enter キー押下する。

```
Creating network "fast-task-api_default" with the default driver
Creating fast-task-api_api_run ... done

This command will guide you through creating your pyproject.toml config.

Version [0.1.0]:
Description []:
Author [None, n to skip]:  n
License []:
Compatible Python versions [^3.9]:

Using version ^2.0.1 for Flask
Using version ^0.3.9 for Flask-RESTful
Using version ^0.14.0 for flask-marshmallow
Using version ^0.26.1 for marshmallow-sqlalchemy
Would you like to define your main dependencies interactively? (yes/no) [yes]
You can specify a package in the following forms:
  - A single name (requests)
  - A name and a constraint (requests@^2.23.0)
  - A git url (git+https://github.com/python-poetry/poetry.git)
  - A git url with a revision (git+https://github.com/python-poetry/poetry.git#develop)
  - A file path (../my-package/my-package.whl)
  - A directory (../my-package/)
  - A url (https://example.com/packages/my-package-0.1.0.tar.gz)

Search for package to add (or leave blank to continue):

Would you like to define your development dependencies interactively? (yes/no) [yes]
Search for package to add (or leave blank to continue):

Generated file

[tool.poetry]
name = "task-api"
version = "0.1.0"
description = ""
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.9"
Flask = "^2.0.1"
Flask-RESTful = "^0.3.9"
flask-marshmallow = "^0.14.0"
marshmallow-sqlalchemy = "^0.26.1"

[tool.poetry.dev-dependencies]

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"


Do you confirm generation? (yes/no) [yes]
```

## Flask のインストール

`$ docker-compose run --entrypoint "poetry install" api`

コマンド実行結果

```
Creating flask-task-api_api_run ... done
The virtual environment found in /src/.venv seems to be broken.
Recreating virtualenv task-api in /src/.venv
Updating dependencies
Resolving dependencies... (22.9s)

Writing lock file

Package operations: 25 installs, 0 updates, 0 removals

  • Installing markupsafe (2.0.1)
  • Installing click (8.0.1)
  • Installing greenlet (1.1.1)
  • Installing itsdangerous (2.0.1)
  • Installing jinja2 (3.0.1)
  • Installing werkzeug (2.0.1)
  • Installing flask (2.0.1)
  • Installing mako (1.1.5)
  • Installing pycparser (2.20)
  • Installing sqlalchemy (1.4.23)
  • Installing alembic (1.7.1)
  • Installing aniso8601 (9.0.1)
  • Installing cffi (1.14.6)
  • Installing flask-sqlalchemy (2.5.1)
  • Installing marshmallow (3.13.0)
  • Installing pytz (2021.1)
  • Installing six (1.16.0)
  • Installing cryptography (3.4.8)
  • Installing flask-marshmallow (0.14.0)
  • Installing flask-migrate (3.1.0)
  • Installing flask-restful (0.3.9)
  • Installing gunicorn (20.1.0)
  • Installing marshmallow-sqlalchemy (0.26.1)
  • Installing pymysql (1.0.2)
  • Installing sqlalchemy-utils (0.37.8)
```

# バックエンド　環境作成

`cd src`


## pylintrc 作成
```
init-hook="."
```

## __init__.py 作成

（中身はなし）

## database.py 作成

```
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()


def init_db(app):
  db.init_app(app)
  Migrate(app, db)
```


## src/config.py 作成

```
import os


class DevelopmentConfig:

  # SQLAlchemy
  SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{user}:{password}@{host}/{database}?charset=utf8'.format(
    **{
      'user': os.getenv('DB_USER', 'root'),
      'password': os.getenv('DB_PASSWORD', 'hoge'),
      'host': os.getenv('DB_HOST', 'db'),
      'database': os.getenv('DB_DATABASE', 'todo'),
    })
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SQLALCHEMY_ECHO = False


Config = DevelopmentConfig
```

## run.py 作成

```
# import app
from flask import Flask
from flask_restful import Api
from src.database import init_db
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

if __name__ == '__main__':
  app.run()
```

## src/app.py 作成

```
from flask import Flask, jsonify
from flask_restful import Api
from src.database import init_db
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

```

# APIリソース作成

## src/apis/views.py 作成

Djangoのファイル名に合わせてviews.pyとしているが、Flaskとしてはルールがないため、
何でも問題なし

```
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
```

## models.py 作成

```
from datetime import datetime
from flask_marshmallow import Marshmallow
#from marshmallow_sqlalchemy import ModelSchema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_marshmallow.fields import fields
from sqlalchemy_utils import UUIDType
from src.database import db

import uuid

ma = Marshmallow()


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
```

# マイグレーション

## サーバ 起動

`docker-compose up -d`

## コンテナに入る

`docker-compose exec api bash`

## 初期化

`poetry run flask db init`

```

Creating directory /src/migrations ... done
Creating directory /src/migrations/versions ... done
Generating /src/migrations/alembic.ini ... done
Generating /src/migrations/env.py ... done
Generating /src/migrations/README ... done
Generating /src/migrations/script.py.mako ... done
Please edit configuration/connection/logging settings in '/src/migrations/alembic.ini' before proceeding.

```

## migration ファイルの作成

`poetry run flask db migrate`

```

INFO [alembic.runtime.migration] Context impl MySQLImpl.
INFO [alembic.runtime.migration] Will assume non-transactional DDL.
INFO [alembic.autogenerate.compare] Detected added table 'tasks'
Generating /src/migrations/versions/35741dfd27ef\_.py ... done

```

## migrate 実行

※不具合があるため、暫定措置対応として自動的に生成されたmigrateファイルを手動で修正する。
src/migrations/versions配下のファイルにimport文を追加する。
（`poetry run flask db upgrade`実行時に、`NameError: name 'sqlalchemy_utils' is not defined`が発生した場合に対応する。）
```
import sqlalchemy_utils
```

`poetry run flask db upgrade`

```
root@6d0bb7b7ff47:/src# poetry run flask db upgrade
INFO  [alembic.runtime.migration] Context impl MySQLImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 871770cd087a, empty message
```

## コンテナから抜ける

`exit`

## テーブル作成済のチェック

`docker-compose exec db mysql -u root -p`

```

> > Enter password:
> > Welcome to the MySQL monitor. Commands end with ; or \g.
> > Your MySQL connection id is 10
> > Server version: 8.0.26 MySQL Community Server - GPL

Copyright (c) 2000, 2021, Oracle and/or its affiliates.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql>

```

### 使用するデータベースを選択

`use todo`

```

Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed

```

`show tables;`

# 起動

`$ docker-compose up -d`

```

```



# git cloneから開始


```
> docker-compose build
> docker-compose run --entrypoint "poetry install" api
> docker-compose up -d
> docker-compose exec api bash

# bpoetry run flask db init
# poetry run flask db upgrade
# poetry run flask db upgrade
# exit


```

