#Nebra Helium Hotspot - BTLE Configuration Software Container
#(C) Nebra LTD. 2021
#Licensed under the MIT License.

FROM balenalib/raspberry-pi-debian:buster-run

COPY piwheels /opt/piwheels

WORKDIR /opt/piwheels/

# hadolint ignore=DL3013
RUN \
apt-get update && \
DEBIAN_FRONTEND="noninteractive" \
TZ="Europe/London" \
apt-get -y install \
python3-minimal=3.7.3-1 \
bluez=5.50-1.2~deb10u1 \
libdbus-1-3=1.12.20-0+deb10u1 \
python3-dbus=1.2.8-3 \
python3-gi=3.30.4-1 \
python3-protobuf \
python3-pip=18.1-5 \
tar=1.30+dfsg-6 \
wget=1.20.1-1.1 \
network-manager=1.14.6-2+deb10u1 \
--no-install-recommends && \
pip3 install \
h3 \
RPi.GPIOl \
colorzero \
gpiozero &&\
apt-get purge python3-pip -y &&\
apt-get autoremove -y &&\
apt-get clean && \
rm -rf /var/lib/apt/lists/*


WORKDIR /opt/

COPY start-gateway-config.sh start-gateway-config.sh
RUN chmod +x start-gateway-config.sh

ARG UPDATE=2021-03-05-1103

RUN wget https://github.com/NebraLtd/helium-miner-config/archive/main.tar.gz \
&& tar -zvxf main.tar.gz \
&& mv helium-miner-config-main helium-miner-config \
&& rm main.tar.gz

#RUN git clone https://github.com/NebraLtd/helium-miner-config.git

WORKDIR /opt/helium-miner-config/

ENTRYPOINT ["sh", "/opt/start-gateway-config.sh"]
