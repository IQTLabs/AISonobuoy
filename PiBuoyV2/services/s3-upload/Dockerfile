FROM python:3.10-alpine
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"
RUN apk update && apk add bash tar xz
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY prep_and_send.py /prep_and_send.py
ARG VERSION
ENV VERSION $VERSION
ENTRYPOINT ["python3", "/prep_and_send.py"]
CMD [""]
