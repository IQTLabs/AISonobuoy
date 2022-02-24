FROM python:3.10-slim
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install --no-install-recommends -y build-essential
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY ais_app.py /ais_app.py
ARG VERSION
ENV VERSION $VERSION
ENTRYPOINT ["python3", "/ais_app.py"]
CMD [""]
