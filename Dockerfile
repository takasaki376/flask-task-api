# python3.9のイメージをダウンロード
FROM python:3.9
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
COPY .env src/.env

# poetryでライブラリをインストール (pyproject.tomlが既にある場合)
RUN poetry config virtualenvs.in-project true
RUN if [ -f pyproject.toml ]; then poetry install; fi

