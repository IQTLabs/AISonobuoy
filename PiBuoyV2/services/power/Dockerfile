FROM python:3.10-slim
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"
ENV PYTHONUNBUFFERED 1
ENV PIJUICE_BUILD_BASE 1
ENV PIJUICE_VERSION 1.7
RUN apt-get update && apt-get install --no-install-recommends -y build-essential git i2c-tools
RUN pip3 install smbus urwid
RUN python3 -c "from smbus import SMBus"
RUN python3 -c "import urwid"
RUN git clone https://github.com/PiSupply/PiJuice.git
WORKDIR /PiJuice/Software/Source
RUN python3 setup.py build
RUN python3 setup.py install
WORKDIR /
RUN python3 -c "from pijuice import PiJuice"
RUN groupadd pijuice
RUN useradd -rm -s /bin/bash -g pijuice -u 1001 pi
COPY app.py /app.py
COPY pijuice_config.JSON /pijuice_config.JSON
COPY shutdown.sh /shutdown.sh
RUN chown pi:pijuice /shutdown.sh
ARG VERSION
ENV VERSION $VERSION
ENTRYPOINT ["python3", "/app.py"]
CMD [""]
