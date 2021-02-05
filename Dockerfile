#Yeet
#Packet Forwarder Docker File
#(C) Pi Supply 2019
#Licensed under the GNU GPL V3 License.

FROM arm64v8/ubuntu:20.04

WORKDIR /opt/

ARG override=202101171357

RUN apt-get update && \
apt-get -y install \
python3-minimal=3.7.3-1 \
python3-networkmanager=2.1-1 \
bluez=5.50-1.2~deb10u1 \
libdbus-1-3=1.12.20-0+deb10u1 \
dbus=1.12.20-0+deb10u1 \
git=1:2.20.1-2+deb10u3 \
ca-certificates=20200601~deb10u2 \
net-tools=1.60+git20180626.aebd88e-1 \
python3-dbus=1.2.8-3 \
python3-gi=3.30.4-1 \
python3-protobuf=3.6.1.3-2 \
python3-rpi.gpio=0.6.5-1 \
cmake=3.13.4-1 \
openssl=1.1.1d-0+deb10u4 \
libssl-dev=1.1.1d-0+deb10u4 \
curl=7.64.0-4+deb10u1 \
python3-pip=18.1-5 \
build-essential=12.6 \
python3-setuptools=40.8.0-1 \
gcc=4:8.3.0-1 \
libtool=2.4.6-9 \
python3-wheel=0.32.3-2 \
cython3=0.29.2-2 \
--no-install-recommends &&\
apt-get clean && \
rm -rf /var/lib/apt/lists/*

RUN pip3 install h3==3.7.1 --no-cache-dir --no-binary :all:

COPY start-gateway-config.sh start-gateway-config.sh
RUN chmod +x start-gateway-config.sh

ARG override=202101171530

RUN git clone https://github.com/NebraLtd/helium-miner-config.git

WORKDIR /opt/helium-miner-config/

ENTRYPOINT ["sh", "/opt/start-gateway-config.sh"]
