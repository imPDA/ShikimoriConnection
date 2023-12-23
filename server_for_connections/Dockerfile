FROM python:3.11
LABEL authors="imPDA"

WORKDIR /code

COPY ./requirements.txt  /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /tmp/requirements.txt

COPY . /code

EXPOSE 8000

ENTRYPOINT [ "uvicorn", "main:app","--proxy-headers", "--forwarded-allow-ips=*", "--host", "0.0.0.0" ]