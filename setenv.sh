#!/bin/bash

base_path="/var/nebra/envvars"

export_param_if_not_exists() {
    local name="$1"
    local fullpath="${base_path}/${name}"

    if [ -f "${fullpath}" ]; then
        contents=$(<"${fullpath}");
        export "${name}"="${contents}"
        echo "${name} is set as ${contents}.";
        success_func=1
    else
        echo "Error: Cannot set ${name} variable.";
        success_func=0
    fi
}

success_freq=0
success_variant=0

#FREQ
if [ -z ${FREQ+x} ]; then
    export_param_if_not_exists FREQ
    if [ $success_func == 1 ]; then
        success_freq=1
    fi
else
    echo "FREQ variable is already set as ${FREQ}.";
    success_freq=1
fi

#VARIANT
if [ -z ${VARIANT+x} ]; then
    export_param_if_not_exists VARIANT
    if [ $success_func == 1 ]; then
        success_variant=1
    fi
else
    echo "VARIANT variable is already set as ${VARIANT}.";
    success_variant=1
fi

if [[ $success_variant != 1 ]]; then
    echo "Error: Required VARIANT parameter has not been set. Container will be reset after 10 sec."
    sleep 10     # sleep for some time before exiting and make the container restart. This would give diagnostics a chance to create necessary data
    exit 1
fi

if [[ $success_freq != 1 ]]; then
    echo "Warning: FREQ is not set for the device."
fi

echo "All required environment variables have been set."
