FROM python:3.9

WORKDIR /code

COPY sensors/requirements.txt .

RUN pip install -r requirements.txt

COPY ./ .
COPY sensors/src/ .

CMD [ "python", "./main.py" ]
