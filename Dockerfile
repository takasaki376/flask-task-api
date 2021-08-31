# python3.9のイメージをダウンロード
FROM python:3.9
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

# uvicornのサーバーを立ち上げる
ENTRYPOINT ["poetry", "run", "flask", "run" ,"--host", "0.0.0.0", "--port=8000"]
