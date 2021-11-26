FROM cctd/flask

WORKDIR /app

COPY app.py /app

ARG APP_PATH=pyapp

COPY ${APP_PATH} /app/pyapp

CMD [ "python", "./app.py" ]