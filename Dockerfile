# Nebra Helium Hotspot - BTLE Configuration Software Container
# (C) Nebra LTD. 2021
# Licensed under the MIT License.

ARG SYSTEM_TIMEZONE="Europe/London"

####################################################################################################
################################## Stage: builder ##################################################

# The balenalib/raspberry-pi-debian-python image was tested but missed many dependencies.
FROM balenalib/raspberry-pi-debian:buster-build as builder

# Nebra uses /opt by convention
WORKDIR /opt/

# Copy python dependencies for `pip install` later
COPY requirements.txt requirements.txt

# Download the variant_definitions in the builder so that runner doesn't need wget
RUN wget -q "https://raw.githubusercontent.com/NebraLtd/helium-hardware-definitions/d84ee2af049b9c033c07788bea577a459aeb3aaa/variant_definitions.py"

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
            --no-install-recommends && \
    # Because the PATH is already updated above, this command creates a new venv AND activates it
    python3 -m venv /opt/venv && \
    # Given venv is active, this `pip` refers to the python3 variant
    pip install --no-cache-dir -r requirements.txt

# No need to cleanup the builder

####################################################################################################
################################### Stage: runner ##################################################

FROM balenalib/raspberry-pi-debian-python:buster-run as runner

# Install bluez, libdbus, network-manager, python3-gi, and venv
RUN \
    apt-get update && \
    DEBIAN_FRONTEND="noninteractive" \
    TZ="$SYSTEM_TIMEZONE" \
    apt-get install -y \
        bluez=5.50-1.2~deb10u1 \
        libdbus-1-3=1.12.20-0+deb10u1 \
        network-manager=1.14.6-2+deb10u1 \
        python3-gi=3.30.4-1 \
        python3-venv=3.7.3-1

# Nebra uses /opt by convention
WORKDIR /opt/

# Copy the code and starter script
COPY config-python/ config-python/
COPY start-gateway-config.sh start-gateway-config.sh

# Switch context to the source code
WORKDIR /opt/config-python/

# Copy variant_definitions from builder
COPY --from=builder /opt/variant_definitions.py variant_definitions.py

# Copy venv from builder and update PATH to activate it
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Cleanup
RUN apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Run start-gateway-config script
ENTRYPOINT ["sh", "/opt/start-gateway-config.sh"]
