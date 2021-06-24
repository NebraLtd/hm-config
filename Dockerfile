#Nebra Helium Hotspot - BTLE Configuration Software Container
#(C) Nebra LTD. 2021
#Licensed under the MIT License.

FROM balenalib/raspberry-pi-debian:buster-run

WORKDIR /opt/

COPY requirements.txt requirements.txt

RUN \
apt-get update && \
DEBIAN_FRONTEND="noninteractive" \
TZ="Europe/London" \
apt-get -y install \
python3-minimal=3.7.3-1 \
bluez=5.50-1.2~deb10u1 \
libdbus-1-3=1.12.20-0+deb10u1 \
python3-pip=18.1-5+rpt1 \
network-manager=1.14.6-2+deb10u1 \
python3-gi=3.30.4-1 \
wget=1.20.1-1.1 \
--no-install-recommends && \
pip3 install --no-cache-dir -r requirements.txt &&\
apt-get purge python3-pip -y &&\
apt-get autoremove -y &&\
apt-get clean && \
rm -rf /var/lib/apt/lists/*

WORKDIR /opt/

COPY start-gateway-config.sh start-gateway-config.sh
RUN chmod +x start-gateway-config.sh

COPY config_python/ config_python/

WORKDIR /opt/config_python/

RUN wget -q "https://raw.githubusercontent.com/NebraLtd/helium-hardware-definitions/master/variant_definitions.py"

ENV LANG=C

ENTRYPOINT ["sh", "/opt/start-gateway-config.sh"]
