FROM python:3.10-alpine
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"
ENV PYTHONUNBUFFERED 1
RUN apk update && apk add bash tar xz
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY app.py /app.py
ARG VERSION
ENV VERSION $VERSION
ENTRYPOINT ["python3", "/app.py"]
CMD [""]
