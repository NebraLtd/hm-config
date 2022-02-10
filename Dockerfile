# Nebra Helium Hotspot - BTLE Configuration Software Container
# (C) Nebra LTD. 2021
# Licensed under the MIT License.

####################################################################################################
################################## Stage: builder ##################################################

# The balenalib/raspberry-pi-debian-python image was tested but missed many dependencies.
FROM balenalib/raspberry-pi-debian:buster-build-20211014 as builder

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
    install_packages \
            python3-minimal=3.7.3-1 \
            python3-pip=18.1-5+rpt1 \
            wget=1.20.1-1.1 \
            python3-venv=3.7.3-1 \
            miniupnpc \
            # The remaining dependencies are for PyGObject
            # https://pygobject.readthedocs.io/en/latest/getting_started.html#ubuntu-logo-ubuntu-debian-logo-debian
            libgirepository1.0-dev=1.58.3-2 \
            gcc=4:8.3.0-1+rpi2 \
            libcairo2-dev=1.16.0-4+rpt1 \
            pkg-config=0.29-6 \
            python3-dev=3.7.3-1 \
            gir1.2-gtk-3.0=3.24.5-1+rpt2 && \
    # Because the PATH is already updated above, this command creates a new venv AND activates it
    python3 -m venv /opt/venv && \
    # Given venv is active, this `pip` refers to the python3 variant
    pip install --no-cache-dir -r requirements.txt

# No need to cleanup the builder

####################################################################################################
################################### Stage: runner ##################################################

FROM balenalib/raspberry-pi-debian-python:buster-run-20211014 as runner

# Install bluez, libdbus, network-manager, python3-gi, and venv
RUN \
    install_packages \
        bluez=5.50-1.2~deb10u2+rpt1 \
        wget=1.20.1-1.1 \
        libdbus-1-3=1.12.20-0+deb10u1 \
        network-manager=1.14.6-2+deb10u1 \
        python3-gi=3.30.4-1 \
        python3-venv=3.7.3-1 \
        miniupnpc

# Nebra uses /opt by convention
WORKDIR /opt/

# Copy the code and starter script
COPY lib/ lib/
COPY gatewayconfig/ gatewayconfig/
COPY *.sh ./
ENV PYTHONPATH="/opt:$PYTHONPATH"

# Copy venv from builder and update PATH to activate it
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# hadolint ignore=DL3008, DL4006
RUN export DISTRO=buster-stable && \
    echo "deb http://apt.radxa.com/$DISTRO/ ${DISTRO%-*} main" | tee -a /etc/apt/sources.list.d/apt-radxa-com.list && \
    wget -nv -O - apt.radxa.com/$DISTRO/public.key | apt-key add - && \
    apt-get update && \
    apt-get install --no-install-recommends -y libmraa && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# This is the libmraa install location, because we are using venv
# it must be added to path explicitly
ENV PYTHONPATH="$PYTHONPATH:/usr/local/lib/python3.7/dist-packages"

# Run start-gateway-config script
ENTRYPOINT ["/opt/start-gateway-config.sh"]

