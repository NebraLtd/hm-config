# Nebra Helium Hotspot - BTLE Configuration Software Container
# (C) Nebra LTD. 2021
# Licensed under the MIT License.

ARG SYSTEM_TIMEZONE="Europe/London"

####################################################################################################
################################## Stage: builder ##################################################

# The balenalib/raspberry-pi-debian-python image was tested but missed many dependencies.
FROM balenalib/raspberry-pi-debian:buster-build-20210705 as builder

# Nebra uses /opt by convention
WORKDIR /opt/

# Copy python dependencies for `pip install` later
COPY requirements.txt requirements.txt

# This will be the path that venv uses for installation below
ENV PATH="/opt/venv/bin:$PATH"

# Install python3-minimal, pip3, wget, venv.
# Then set venv environment copied from builder.
# Finally, use pip to install dependencies.
RUN \
    apt-get update && \
    DEBIAN_FRONTEND="noninteractive" \
    TZ="$SYSTEM_TIMEZONE" \
        apt-get -y install \
            python3-minimal=3.7.3-1 \
            python3-pip=18.1-5+rpt1 \
            wget=1.20.1-1.1 \
            python3-venv=3.7.3-1 \
            # The remaining dependencies are for PyGObject
            # https://pygobject.readthedocs.io/en/latest/getting_started.html#ubuntu-logo-ubuntu-debian-logo-debian
            libgirepository1.0-dev=1.58.3-2 \
            gcc=4:8.3.0-1+rpi2 \
            libcairo2-dev=1.16.0-4+rpt1 \
            pkg-config=0.29-6 \
            python3-dev=3.7.3-1 \
            gir1.2-gtk-3.0=3.24.5-1+rpt2 \
            --no-install-recommends && \
    # Because the PATH is already updated above, this command creates a new venv AND activates it
    python3 -m venv /opt/venv && \
    # Given venv is active, this `pip` refers to the python3 variant
    pip install --no-cache-dir -r requirements.txt

# No need to cleanup the builder

####################################################################################################
################################### Stage: runner ##################################################

FROM balenalib/raspberry-pi-debian-python:buster-run-20210705 as runner

# Install bluez, libdbus, network-manager, python3-gi, and venv
RUN \
    apt-get update && \
    DEBIAN_FRONTEND="noninteractive" \
    TZ="$SYSTEM_TIMEZONE" \
    apt-get install -y \
        bluez=5.50-1.2~deb10u2+rpt1 \
        rfkill \
        libdbus-1-3=1.12.20-0+deb10u1 \
        network-manager=1.14.6-2+deb10u1 \
        python3-gi=3.30.4-1 \
        python3-venv=3.7.3-1

# Nebra uses /opt by convention
WORKDIR /opt/

# Copy the code and starter script
COPY lib/ lib/
COPY gatewayconfig/ gatewayconfig/
COPY *.sh .
ENV PYTHONPATH="/opt:$PYTHONPATH"

# Copy venv from builder and update PATH to activate it
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Cleanup
RUN apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# START DEBUGGING
# Uncomment the lines below to mock parts of the configuration
# COPY example/ example/
# ENV ONBOARDING_KEY_FILEPATH=/opt/example/device_keys.txt 
# ENV ETH0_MAC_ADDRESS_PATH=/opt/example/eth0_mac_address.txt
# END DEBUGGING

# Run start-gateway-config script
ENTRYPOINT ["sh", "/opt/start-gateway-config.sh"]
