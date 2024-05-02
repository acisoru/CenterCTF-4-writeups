FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev 

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt


COPY . /code/
RUN sqlite3 cats.db < init.sql
# 


CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "5643"]