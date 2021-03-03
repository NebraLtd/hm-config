#Nebra Helium Hotspot - BTLE Configuration Software Container
#(C) Nebra LTD. 2021
#Licensed under the MIT License.

FROM arm64v8/ubuntu:20.04

WORKDIR /opt/

RUN \
apt-get update && \
DEBIAN_FRONTEND="noninteractive" \
TZ="Europe/London" \
apt-get -y install \
python3-minimal \
python3-networkmanager \
bluez \
libdbus-1-3 \
dbus \
git \
ca-certificates \
net-tools \
python3-dbus \
python3-gi \
python3-protobuf \
python3-pip \
--no-install-recommends &&\
apt-get clean && \
rm -rf /var/lib/apt/lists/*

COPY start-gateway-config.sh start-gateway-config.sh
RUN chmod +x start-gateway-config.sh

RUN git clone https://github.com/NebraLtd/helium-miner-config.git

COPY piwheels /opt/piwheels

WORKDIR /opt/piwheels/

# hadolint ignore=DL3013
RUN pip3 install \
h3-3.7.1-cp38-cp38-linux_aarch64.whl \
RPi.GPIO-0.7.0-cp38-cp38-linux_aarch64.whl \
colorzero-1.1-py2.py3-none-any.whl \
gpiozero-1.5.1-py2.py3-none-any.whl

WORKDIR /opt/helium-miner-config/

ENTRYPOINT ["sh", "/opt/start-gateway-config.sh"]
