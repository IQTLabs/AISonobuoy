FROM python:3.10-slim
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"
RUN apt-get update && apt-get install --no-install-recommends -y git i2c-tools python3-smbus python3-urwid
RUN git clone https://github.com/PiSupply/PiJuice.git
RUN dpkg -i /PiJuice/Software/Install/pijuice-base_1.7_all.deb
COPY app.py /app.py
ENTRYPOINT ["python3", "/app.py"]
CMD [""]
