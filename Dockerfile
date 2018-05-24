FROM python:3.6

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /

RUN apt update

RUN mkdir /code
WORKDIR /code

ADD requirements.txt /code
RUN pip install -r requirements.txt

ADD . /code
RUN pip install .

CMD ["python", "-m", "eventbot"]
