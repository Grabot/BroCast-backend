FROM python:3.12.3-slim-bullseye

WORKDIR /app

# install static dependencies
RUN apt-get update &&\
    apt install -y git &&\
    pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir poetry && \
    pip3 install --no-cache-dir pre-commit && \
    poetry config virtualenvs.create false

# add dependency file
COPY pyproject.toml /app/pyproject.toml

# install project dependencies
RUN poetry install --no-root --only main

# add other project files
COPY app /app/.
RUN mkdir -p static/uploads
