FROM python:3.10-alpine

WORKDIR /home/app

COPY /server .

EXPOSE 9999

CMD ["python3", "-t", "ServerHandler.py"]

