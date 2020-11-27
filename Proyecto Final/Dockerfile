FROM python:3-alpine

COPY requirements.txt /tmp/

RUN pip install -r /tmp/requirements.txt

WORKDIR /app/

COPY . ./

CMD ["python", "tinyurl.py"]

EXPOSE 5000 