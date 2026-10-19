#!/bin/bash

# Workspace permissions initialization script
WORKSPACE_PATH="${DOCKER_VOLUME_PATH:-/deepx/workspace}"
TARGET_USER="${TARGET_USER:-deepx}"
HOST_UID="${HOST_UID:-1000}"
HOST_GID="${HOST_GID:-1000}"

echo "Initializing workspace permissions..."
echo "Workspace path: $WORKSPACE_PATH"
echo "Target user: $TARGET_USER"
echo "Host UID:GID = $HOST_UID:$HOST_GID"

# Create workspace directory if it doesn't exist
if [ ! -d "$WORKSPACE_PATH" ]; then
    echo "Creating workspace directory: $WORKSPACE_PATH"
    mkdir -p "$WORKSPACE_PATH"
fi

# Fix ownership/permissions only when the workspace is not already owned by the host
# user: the mount may be a host checkout, and a recursive chmod 775 would rewrite the
# mode of every file in it.
if [ "$(stat -c %u "$WORKSPACE_PATH")" != "$HOST_UID" ]; then
    # Change ownership to the target user
    echo "Setting ownership to $HOST_UID:$HOST_GID"
    sudo chown -R "$HOST_UID:$HOST_GID" "$WORKSPACE_PATH"

    # Set proper permissions (rwxrwxr-x)
    echo "Setting permissions to 775"
    sudo chmod -R 775 "$WORKSPACE_PATH"
else
    echo "Workspace already owned by UID $HOST_UID; skipping chown/chmod"
fi

echo "Workspace permissions initialized successfully"

# Execute the original entrypoint command
exec "$@"
