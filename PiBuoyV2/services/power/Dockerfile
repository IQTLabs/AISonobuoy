FROM python:3.10-slim
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"
ENV PYTHONUNBUFFERED 1
ENV PIJUICE_BUILD_BASE 1
ENV PIJUICE_VERSION 1.8
RUN apt-get update && apt-get install --no-install-recommends -y build-essential curl i2c-tools
RUN pip3 install smbus urwid
RUN python3 -c "from smbus import SMBus"
RUN python3 -c "import urwid"
RUN curl -L https://github.com/pisupply/pijuice/tarball/V1.8 | tar -xz
WORKDIR /PiSupply-PiJuice-bc61c0f/Software/Source
RUN python3 setup.py build
RUN python3 setup.py install
WORKDIR /
RUN python3 -c "from pijuice import PiJuice"
RUN groupadd -g 1001 pijuice
RUN useradd -rm -s /bin/bash -g pijuice -u 1000 pi
COPY power_app.py /power_app.py
COPY pijuice_config.JSON /pijuice_config.JSON
COPY shutdown.sh /shutdown.sh
ARG VERSION
ENV VERSION $VERSION
ENTRYPOINT ["python3", "/power_app.py"]
CMD [""]
