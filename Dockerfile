FROM cctd/flask

WORKDIR /app

COPY app.py /app

COPY pyapp /app/pyapp

CMD [ "python", "./app.py" ]