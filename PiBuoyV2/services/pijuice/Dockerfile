FROM python:3.7-slim
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"
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
WORKDIR /var/lib/pijuice
RUN python3 -c "from pijuice import PiJuice"
ENTRYPOINT ["/usr/local/bin/pijuice_sys.py"]
CMD [""]
