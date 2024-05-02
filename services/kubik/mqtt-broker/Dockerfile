FROM eclipse-mosquitto@sha256:0953ddaaeb90a9df827a79459265f270888e0e9c1bb96f08b70687be2d583c9a

COPY ./mosquitto.conf /mosquitto/config/mosquitto.conf
COPY ./acl /mosquitto/config/acl

RUN echo "admin:admin" > /mosquitto/config/passwd-admin
RUN chmod 0700 /mosquitto/config/passwd-admin
RUN mosquitto_passwd -U /mosquitto/config/passwd-admin

RUN echo "device:device" > /mosquitto/config/passwd-device
RUN chmod 0700 /mosquitto/config/passwd-device
RUN mosquitto_passwd -U /mosquitto/config/passwd-device

RUN chmod 0700 /mosquitto/config/acl

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["mosquitto", "-c", "/mosquitto/config/mosquitto.conf"]
