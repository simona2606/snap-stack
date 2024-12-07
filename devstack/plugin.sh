#!/bin/bash

# Flask dependencies function
function install_flask_dependencies {
    echo "Installing Flask and dependencies..."
    
    # venv creation
    if [[ ! -d "$APP_DIR/venv" ]]; then
        python3 -m venv "$APP_DIR/venv"
    fi

    # venv activation
    source "$APP_DIR/venv/bin/activate"

    # install requirements
    if [[ -f "$APP_DIR/requirements.txt" ]]; then
        pip install -r "$APP_DIR/requirements.txt" || { echo "Failed to install dependencies"; exit 1; }
    else
        echo "requirements.txt not found!"
        exit 1
    fi
    
    echo "Copying configuration file..."
    sudo cp /home/ubuntu/snap-stack/app/config.yaml /opt/stack/snap-stack/app/config.yaml || {
        echo "Failed to copy configuration file"
        return 1
    }

    # venv deactivation
    deactivate
}

# Move service file function
function copy_service_file {
    echo "Moving service file to systemd directory..."
    sudo cp "$SERVICE_DIR/snap-stack.service" "$SYSTEMD_DIR" || { echo "Failed to copy service file"; exit 1; }
    sudo systemctl enable snap-stack.service || { echo "Failed to enable systemd plugin service"; exit 1; }
    sudo systemctl daemon-reload || { echo "Failed to reload systemd daemon"; exit 1; }
}

# Start the plugin
function start_snap_stack_plugin {
    echo "Starting the service..."
    sudo systemctl start snap-stack.service || { echo "Failed to start service"; exit 1; }
}

# Configure the plugin
function configure_snap_stack_plugin {
    echo "Configuring the service..."
    # Add configuration here
}

if is_service_enabled snap-stack; then

    if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
        echo_summary "No additional packages to install for the Plugin."

    elif [[ "$1" == "stack" && "$2" == "install" ]]; then
        echo_summary "Installing Flask"
        install_flask_dependencies
        copy_service_file

    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        echo_summary "Configuring the Plugin"
        configure_snap_stack_plugin

    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        echo_summary "Initializing the Plugin"
        start_snap_stack_plugin
    fi

    if [[ "$1" == "unstack" ]]; then
        echo_summary "Stopping the service..."
        sudo systemctl stop snap-stack.service || { echo "Failed to stop service"; exit 1; }
    fi

    if [[ "$1" == "clean" ]]; then
        sudo rm "$SYSTEMD_DIR/snap-stack.service"
    fi
fi
