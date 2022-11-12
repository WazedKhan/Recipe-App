FROM python:3.9-alpine3.15
LABEL maintainer="wazed"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /temp/requirements.txt
COPY ./app /app
WORKDIR /app
EXPOSE 800

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /temp/requirements.txt && \
    rm -rf /tem && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

ENV PATH="/py/bin:$PATH"

USER django-user
