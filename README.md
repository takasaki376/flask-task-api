# 参考
[PythonのFlaskでMySQLを利用したRESTfulなAPIをDocker環境で実装する](https://qiita.com/kai_kou/items/5d73de21818d1d582f00)


# コマンドの実行環境について
Windows10 PowerShell

# docker-compose関連ファイルの作成

-docker-compose.yaml 作成
docker-composeの定義ファイル。この中で、Dockerfileを呼び出して、Dockerコンテナのビルドを行います。

```
version: '3'
services:
  api:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - "./src:/src"
    tty: true
    environment:
      TZ: Asia/Tokyo
      FLASK_APP: run.py
      FLASK_ENV: development
    command: flask run -h 0.0.0.0
  db:
    build: ./mysql/
    volumes:
      - ./mysql/mysql_data:/var/lib/mysql # データの永続化
      - ./mysql/sqls:/docker-entrypoint-initdb.d # 初期化時に実行するSQL
    environment:
      - MYSQL_ROOT_PASSWORD=hoge # パスワードだけど、ローカルなので、
```


- Dockerfile 作成
Dockerの定義ファイル。利用する公開イメージ（今回はPython 3.9がインストールされたOSイメージ）を取得し、 
poetryによって、パッケージ定義ファイルである pyproject.toml を元に各pythonパッケージをインストールします。

```
# python3.9のイメージをダウンロード
FROM python:3.9-buster
ENV PYTHONUNBUFFERED=1

ARG project_dir=/src/
WORKDIR $project_dir

# pipを使ってpoetryをインストール
RUN pip install poetry

# poetryの定義ファイルをコピー (存在する場合)
COPY pyproject.toml* poetry.lock* ./

# poetryでライブラリをインストール (pyproject.tomlが既にある場合)
RUN poetry config virtualenvs.in-project true
RUN if [ -f pyproject.toml ]; then poetry install; fi
```

# イメージのビルド(MySQL設定用)

`$ docker-compose build db`

コマンド実行結果

```
Building db
[+] Building 31.8s (7/7) FINISHED
 => [internal] load build definition from Dockerfile                                                               0.0s
 => => transferring dockerfile: 121B                                                                               0.0s
 => [internal] load .dockerignore                                                                                  0.0s
 => => transferring context: 2B                                                                                    0.0s
 => [internal] load metadata for docker.io/library/mysql:latest                                                    1.5s
 => [internal] load build context                                                                                  0.0s
 => => transferring context: 149B                                                                                  0.0s
 => [1/2] FROM docker.io/library/mysql@sha256:d45561a65aba6edac77be36e0a53f0c1fba67b951cb728348522b671ad63f926    28.1s
 => => resolve docker.io/library/mysql@sha256:d45561a65aba6edac77be36e0a53f0c1fba67b951cb728348522b671ad63f926     0.0s
 => => sha256:5a4e492065c722ec8cc7413552bafc6fd5434c5ad90797e898ccc4e347e21aa5 7.09kB / 7.09kB                     0.0s
 => => sha256:d45561a65aba6edac77be36e0a53f0c1fba67b951cb728348522b671ad63f926 320B / 320B                         0.0s
 => => sha256:c744f48715807b821411cc52862676fdd18a2458b4a179cae56854d320c85538 2.83kB / 2.83kB                     0.0s
 => => sha256:03285f80bafd8314f1454a95519f147a8a23a1513d87f1b58a10b9eaec220005 4.18MB / 4.18MB                     1.3s
 => => sha256:e1acddbe380c63f0de4b77d3f287b7c81cd9d89563a230692378126b46ea6546 27.15MB / 27.15MB                   6.2s
 => => sha256:bed879327370a64c0bce7b3105f32557f95bbab187b23f88eef1f7eabedd73aa 1.73kB / 1.73kB                     1.1s
 => => sha256:ccc17412a00a6b2ffb9d46adc91d61efac70ff52fb6833b144df9783d4e8279d 1.42MB / 1.42MB                     3.5s
 => => sha256:1f556ecc09d1be245be2316ca09f4de24383e180185ff83e2acd3d96186d7dbf 149B / 149B                         1.8s
 => => sha256:adc5528e468d8f57ba7b35a246fb6c5170467046ddb4ac3f47d6cab6334c7b48 13.45MB / 13.45MB                   7.4s
 => => sha256:1afc286d5d531578457cd0090779d173dcde261905a4298e64826ad09563e255 1.87kB / 1.87kB                     4.3s
 => => sha256:6c724a59adff64de723ca4ee2528de62c2b399f0a8894dcecc9e9332e5c33ff1 221B / 221B                         5.6s
 => => sha256:0f2345f8b0a3fc69b36f1f2b2870629cf840553bfab5b23ba27703a59d4bac7a 104.39MB / 104.39MB                22.9s
 => => sha256:c8461a25b23b9c6c8aeae4d7f48d6ff97020bb81bbfbe8bb081ae23ab510a0e0 843B / 843B                         6.5s
 => => extracting sha256:e1acddbe380c63f0de4b77d3f287b7c81cd9d89563a230692378126b46ea6546                          1.5s
 => => sha256:3adb49279bed24155b18b49b9f8fdaac948e5f3020a5e70209607b8b2e723599 5.54kB / 5.54kB                     6.9s
 => => sha256:77f22cd6c363b28c51bf66c5d11695951a05cf7a88eb9d6a9ca6b243ceb24218 121B / 121B                         7.2s
 => => extracting sha256:bed879327370a64c0bce7b3105f32557f95bbab187b23f88eef1f7eabedd73aa                          0.1s
 => => extracting sha256:03285f80bafd8314f1454a95519f147a8a23a1513d87f1b58a10b9eaec220005                          0.2s
 => => extracting sha256:ccc17412a00a6b2ffb9d46adc91d61efac70ff52fb6833b144df9783d4e8279d                          0.1s
 => => extracting sha256:1f556ecc09d1be245be2316ca09f4de24383e180185ff83e2acd3d96186d7dbf                          0.0s
 => => extracting sha256:adc5528e468d8f57ba7b35a246fb6c5170467046ddb4ac3f47d6cab6334c7b48                          0.8s
 => => extracting sha256:1afc286d5d531578457cd0090779d173dcde261905a4298e64826ad09563e255                          0.0s
 => => extracting sha256:6c724a59adff64de723ca4ee2528de62c2b399f0a8894dcecc9e9332e5c33ff1                          0.0s
 => => extracting sha256:0f2345f8b0a3fc69b36f1f2b2870629cf840553bfab5b23ba27703a59d4bac7a                          4.4s
 => => extracting sha256:c8461a25b23b9c6c8aeae4d7f48d6ff97020bb81bbfbe8bb081ae23ab510a0e0                          0.0s
 => => extracting sha256:3adb49279bed24155b18b49b9f8fdaac948e5f3020a5e70209607b8b2e723599                          0.0s
 => => extracting sha256:77f22cd6c363b28c51bf66c5d11695951a05cf7a88eb9d6a9ca6b243ceb24218                          0.0s
 => [2/2] ADD ./my.cnf /etc/mysql/conf.d/my.cnf                                                                    1.8s
 => exporting to image                                                                                             0.1s
 => => exporting layers                                                                                            0.1s
 => => writing image sha256:c8e82494a4c85407e9e1d89d81b1bcd9d9c1823344978523cf5afa23c46aed9c                       0.0s
 => => naming to docker.io/library/fast-task-api_db                                                                0.0s

Use 'docker scan' to run Snyk tests against images to find vulnerabilities and learn how to fix them
```

# MySQLの設定

mysqlフォルダ作成

Dockerfileファイル作成
```
FROM mysql
EXPOSE 3306

ADD ./my.cnf /etc/mysql/conf.d/my.cnf # 設定ファイルの読み込み

CMD ["mysqld"]

```

my.cnfファイルにて、文字コード指定
```
[mysqld]
character-set-server=utf8
[mysql]
default-character-set=utf8
[client]
default-character-set=utf8
```

sqls/initialize.sqlファイル作成
データベースが初期化時に作成されるようにする。
```
CREATE DATABASE todo;
use todo;
```

# DB起動
`docker-compose up -d db`

# DB接続
`docker-compose exec db mysql -u root -p`
Enter password:

mysql>show databases;



# APサーバ　イメージのビルド
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


# poetryによるPython環境のセットアップ
```
$ docker-compose run --entrypoint "poetry init --name task-api --dependency flask --dependency flask-restful --dependency flask_marshmallow --dependency marshmallow-sqlalchemy" api
```

コマンド実行結果
Authorのみ"n"を入力するが、それ以外は何も入力せずにEnterキー押下する。

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

# Flaskのインストール

`$ docker-compose run --entrypoint "poetry install" api`

コマンド実行結果

```
Creating fast-task-api_api_run ... done
Creating virtualenv task-api in /src/.venv
Updating dependencies
Resolving dependencies... (21.5s)

Writing lock file

Package operations: 15 installs, 0 updates, 0 removals

  • Installing markupsafe (2.0.1)
  • Installing click (8.0.1)
  • Installing greenlet (1.1.1)
  • Installing itsdangerous (2.0.1)
  • Installing jinja2 (3.0.1)
  • Installing werkzeug (2.0.1)
  • Installing aniso8601 (9.0.1)
  • Installing flask (2.0.1)
  • Installing marshmallow (3.13.0)
  • Installing pytz (2021.1)
  • Installing six (1.16.0)
  • Installing sqlalchemy (1.4.23)
  • Installing flask-marshmallow (0.14.0)
  • Installing flask-restful (0.3.9)
  • Installing marshmallow-sqlalchemy (0.26.1)
```

# 追加ライブラリのインストール
```
docker-compose run --entrypoint "poetry add flask-sqlalchemy sqlalchemy_utils flask-migrate" api
docker-compose run --entrypoint "poetry add pymysql" api
docker-compose run --entrypoint "poetry add gunicorn" api

```
# DB起動
`docker-compose up -d api`



# 起動確認用　環境作成

apiフォルダを作成する。

```
cd src
mkdir api
`

api/__init__.pyファイルを作成する。（中身はなし）

api/main.py

```
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World'


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
```


# 起動
`$ docker-compose up`
