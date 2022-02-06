FROM python:3.10-slim
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"
ENV PIJUICE_BUILD_BASE 1
ENV PIJUICE_VERSION 1.7
RUN useradd -rm -d /home/pi -s /bin/bash -g root -G sudo -u 1001 pi
RUN apt-get update && apt-get install --no-install-recommends -y build-essential git i2c-tools python3-smbus python3-urwid
RUN pip3 install smbus urwid
RUN python3 -c "from smbus import SMBus"
RUN python3 -c "import urwid"
RUN git clone https://github.com/PiSupply/PiJuice.git
WORKDIR /PiJuice/Software/Source
RUN python3 setup.py build
RUN python3 setup.py install
WORKDIR /PiJuice/Software/Install
RUN dpkg -i ./pijuice-base_1.7_all.deb
RUN chown -R root:root /usr/bin/pijuice*
WORKDIR /var/lib/pijuice
RUN python3 -c "from pijuice import PiJuice"
COPY pijuice_config.JSON /var/lib/pijuice/pijuice_config.JSON
COPY shutdown.sh /shutdown.sh
RUN usermod -a -G pijuice pi
RUN chown pi:root /shutdown.sh
ARG VERSION
ENV VERSION $VERSION
ENTRYPOINT ["/usr/bin/pijuice_sys.py"]
CMD [""]
