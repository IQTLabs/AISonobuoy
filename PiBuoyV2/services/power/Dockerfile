FROM python:3.9-slim
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"
ENV PIJUICE_BUILD_BASE 1
ENV PIJUICE_VERSION 1.7
RUN apt-get update && apt-get install --no-install-recommends -y git i2c-tools python3-smbus python3-urwid
RUN git clone https://github.com/PiSupply/PiJuice.git
WORKDIR /PiJuice/Software/Source
RUN python3 setup.py build
RUN python3 setup.py install
WORKDIR /
COPY app.py /app.py
ENTRYPOINT ["python3", "/app.py"]
CMD [""]
