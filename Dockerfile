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
python3-minimal=3.8.2-0ubuntu2 \
python3-networkmanager=2.1-2 \
bluez=5.53-0ubuntu3 \
libdbus-1-3=1.12.16-2ubuntu2.1 \
dbus=1.12.16-2ubuntu2.1 \
git=1:2.25.1-1ubuntu3 \
ca-certificates=20210119~20.04.1 \
net-tools=1.60+git20180626.aebd88e-1ubuntu1 \
python3-dbus=1.2.16-1build1 \
python3-gi=3.36.0-1 \
python3-protobuf=3.6.1.3-2ubuntu5 \
openssl=1.1.1f-1ubuntu2.1 \
libssl-dev=1.1.1f-1ubuntu2.1 \
curl=7.68.0-1ubuntu2.4 \
python3-pip=20.0.2-5ubuntu1.1 \
python3-wheel=0.34.2-1 \
--no-install-recommends &&\
apt-get clean && \
rm -rf /var/lib/apt/lists/*

COPY h3-3.7.1-cp38-cp38-linux_aarch64.whl h3-3.7.1-cp38-cp38-linux_aarch64.whl
COPY RPi.GPIO-0.7.0-cp38-cp38-linux_aarch64.whl RPi.GPIO-0.7.0-cp38-cp38-linux_aarch64.whl

# hadolint ignore=DL3013
RUN pip3 install h3-3.7.1-cp38-cp38-linux_aarch64.whl RPi.GPIO-0.7.0-cp38-cp38-linux_aarch64.whl

COPY start-gateway-config.sh start-gateway-config.sh
RUN chmod +x start-gateway-config.sh

RUN git clone https://github.com/NebraLtd/helium-miner-config.git

WORKDIR /opt/helium-miner-config/

ENTRYPOINT ["sh", "/opt/start-gateway-config.sh"]
