FROM python:3.10-slim
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install --no-install-recommends -y build-essential curl git libjpeg62-turbo-dev procps wget zlib1g-dev
RUN python3 -m pip install -U pip
RUN git clone https://github.com/RPi-Distro/RTIMULib.git -b V7.2.1
WORKDIR /RTIMULib/Linux/python
RUN python3 setup.py build && python3 setup.py install
WORKDIR /
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY sense_app.py /sense_app.py
COPY hooks.py /hooks.py
COPY internet_check.sh /internet_check.sh
COPY shutdown.sh /shutdown.sh
ARG VERSION
ENV VERSION $VERSION
ENTRYPOINT ["python3", "/sense_app.py"]
CMD [""]
