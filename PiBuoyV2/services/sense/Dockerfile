FROM python:3.10-slim
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"
RUN apt-get update && apt-get install --no-install-recommends -y build-essential curl git procps wget
RUN git clone https://github.com/RPi-Distro/RTIMULib.git -b V7.2.1
WORKDIR /RTIMULib/Linux/python
RUN python3 setup.py build && python3 setup.py install
WORKDIR /
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY app.py /app.py
COPY internet_check.sh /internet_check.sh
ENTRYPOINT ["python3", "/app.py"]
CMD [""]
