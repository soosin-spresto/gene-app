FROM python:3.8-slim

# Configure python
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
ENV POETRY_VERSION=1.1.4

RUN apt-get -qq update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    git \
    default-libmysqlclient-dev python-dev

RUN apt-get install -y gstreamer1.0-libav libnss3-tools libatk-bridge2.0-0 libcups2-dev libxkbcommon-x11-0 libxcomposite-dev libxrandr2 libgbm-dev libgtk-3-0
RUN rm -rf /var/lib/apt/lists/*

RUN wget -O - https://raw.githubusercontent.com/python-poetry/poetry/901bdf0491005f1b3db41947d0d938da6838ecb9/get-poetry.py | python
ENV PATH=/root/.poetry/bin:$PATH

RUN poetry config virtualenvs.create false

WORKDIR /gene-app
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-interaction --no-ansi --no-dev --no-root
COPY . ./

RUN chmod +x *.sh

ENTRYPOINT ./entrypoint.sh