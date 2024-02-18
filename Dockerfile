# ベースイメージ
FROM python:3.12-slim as base

# 作業ディレクトリの設定
ENV APP_ROOT /app
WORKDIR ${APP_ROOT}

# 依存関係のインストールのためのレイヤーのキャッシュを最適化
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルのコピー
COPY . .

# ユーザーの追加
RUN useradd -r -s /bin/false appuser
USER appuser

# 環境変数の設定
ENV PYTHONPATH "${PYTHONPATH}:${APP_ROOT}"

# アプリケーションの実行
ENTRYPOINT ["python", "main.py"]
