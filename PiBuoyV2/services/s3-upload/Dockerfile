FROM python:3.9-alpine
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"
RUN apk update && apk add bash ffmpeg tar xz
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY prep_and_send.sh /prep_and_send.sh
ENTRYPOINT ["/prep_and_send.sh"]
CMD [""]
