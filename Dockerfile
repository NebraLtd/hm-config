#Nebra Helium Hotspot - BTLE Configuration Software Container
#(C) Nebra LTD. 2021
#Licensed under the MIT License.

FROM arm64v8/ubuntu:20.04

COPY piwheels /opt/piwheels

WORKDIR /opt/piwheels/

# hadolint ignore=DL3013
RUN \
apt-get update && \
DEBIAN_FRONTEND="noninteractive" \
TZ="Europe/London" \
apt-get -y install \
python3-minimal \
bluez \
libdbus-1-3 \
python3-dbus \
python3-gi \
python3-protobuf \
python3-pip \
tar \
wget \
network-manager \
--no-install-recommends &&\
pip3 install \
h3-3.7.1-cp38-cp38-linux_aarch64.whl \
RPi.GPIO-0.7.0-cp38-cp38-linux_aarch64.whl \
colorzero-1.1-py2.py3-none-any.whl \
gpiozero-1.5.1-py2.py3-none-any.whl &&\
apt-get purge python3-pip -y &&\
apt-get autoremove -y &&\
apt-get clean && \
rm -rf /var/lib/apt/lists/*


WORKDIR /opt/

COPY start-gateway-config.sh start-gateway-config.sh
RUN chmod +x start-gateway-config.sh

ARG UPDATE=2021-03-03-2343

RUN wget https://github.com/NebraLtd/helium-miner-config/archive/main.tar.gz \
&& tar -zvxf main.tar.gz \
&& mv helium-miner-config-main helium-miner-config \
&& rm main.tar.gz

#RUN git clone https://github.com/NebraLtd/helium-miner-config.git

WORKDIR /opt/helium-miner-config/

ENTRYPOINT ["sh", "/opt/start-gateway-config.sh"]
