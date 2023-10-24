FROM python:3.9-slim-buster

WORKDIR /flask

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY app ./app
COPY config.py start.py ./

CMD ["gunicorn", "--bind=0.0.0.0:5000", "--workers=4", "--log-level=info", "start:app"]
