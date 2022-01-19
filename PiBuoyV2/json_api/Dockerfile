FROM python:3-slim
COPY bottle.py /bottle.py
COPY data-source.py /data-source.py
WORKDIR /
EXPOSE 8081
ENV PYTHONUNBUFFERED 1
CMD python3 /data-source.py
