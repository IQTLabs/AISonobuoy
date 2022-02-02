FROM alpine:3.15
RUN apk update && apk add alsa-utils alsa-utils-doc alsa-lib alsaconf alsa-ucm-conf bash ffmpeg
RUN addgroup root audio
COPY asound.conf /etc/asound.conf
COPY record.sh /record.sh
ARG VERSION
ENV VERSION $VERSION
ENTRYPOINT ["/record.sh"]
CMD [""]
