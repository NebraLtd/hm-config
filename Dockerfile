# Nebra Helium Hotspot - BTLE Configuration Software Container
# (C) Nebra LTD. 2021
# Licensed under the MIT License.

ARG BUILD_BOARD

####################################################################################################
################################## Stage: builder ##################################################

# The balenalib/raspberry-pi-debian-python image was tested but missed many dependencies.
FROM balenalib/"$BUILD_BOARD"-debian:bullseye-build-20230530 AS builder

# Nebra uses /opt by convention
WORKDIR /opt/

# Copy python dependencies for `poetry install` later
COPY pyproject.toml ./pyproject.toml
COPY poetry.lock ./poetry.lock
COPY README.md ./README.md
COPY lib/ lib/
COPY gatewayconfig/ gatewayconfig/
COPY *.sh ./


# This will be the path that venv uses for installation below
ENV PATH="/opt/venv/bin:$PATH"

# Install python3-minimal, pip3, wget, venv.
# Then set venv environment copied from builder.
# Finally, use pip to install dependencies.
# hadolint ignore=DL3013
RUN \
    install_packages \
            python3-minimal \
            python3-pip \
            wget \
            python3-venv \
            # The remaining dependencies are for PyGObject
            # https://pygobject.readthedocs.io/en/latest/getting_started.html#ubuntu-logo-ubuntu-debian-logo-debian
            libgirepository1.0-dev\
            gcc \
            libcairo2-dev \
            pkg-config \
            python3-dev \
            libdbus-1-dev \
            gir1.2-gtk-3.0 && \
    # Because the PATH is already updated above, this command creates a new venv AND activates it
    python3 -m venv /opt/venv && \
    # Given venv is active, this `pip` refers to the python3 variant
    pip install --no-cache-dir poetry==1.5.1 && \
    poetry install --no-cache --no-root && \
    poetry build && \
    pip install --no-cache-dir dist/hm_config-1.0.tar.gz

# No need to cleanup the builder

####################################################################################################
################################### Stage: runner ##################################################

FROM balenalib/"$BUILD_BOARD"-debian-python:bullseye-run-20230530 AS runner

# Install bluez, libdbus, network-manager, python3-gi, and venv
RUN \
    install_packages \
        bluez \
        wget \
        libdbus-1-3 \
        network-manager \
        python3-gi \
        python3-venv

# Nebra uses /opt by convention
WORKDIR /opt/

COPY *.sh ./
ENV PYTHONPATH="/opt:$PYTHONPATH"

# Copy venv from builder and update PATH to activate it
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# hadolint ignore=DL3008, DL4006
RUN export DISTRO=bullseye-stable && \
    echo "deb https://apt.radxa.com/$DISTRO/ ${DISTRO%-*} main" | tee -a /etc/apt/sources.list.d/apt-radxa-com.list && \
    wget -nv -O - apt.radxa.com/$DISTRO/public.key | apt-key add - && \
    apt-get update && \
    apt-get install --no-install-recommends -y libmraa && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# This is the libmraa install location, because we are using venv
# it must be added to path explicitly
ENV PYTHONPATH="$PYTHONPATH:/usr/local/lib/python3.9/dist-packages"

# Run start-gateway-config script
ENTRYPOINT ["/opt/start-gateway-config.sh"]

