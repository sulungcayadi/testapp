#!/bin/sh
# Start the Copilot Agent Builder training app.
cd "$(dirname "$0")"
exec python3 app.py "$@"
