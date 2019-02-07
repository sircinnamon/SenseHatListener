FROM python:3.4.9-slim-jessie

RUN apt-get update && apt-get install sense-hat

ADD test.py /test.py

WORKDIR /

CMD ["python", "/test.py"]