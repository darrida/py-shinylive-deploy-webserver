#!/bin/bash

# Start the first process
echo "Starting SSH and python webserver..."
# service ssh restart &
/usr/sbin/sshd &

# Start the second process
# echo "Starting webserver..."
python3 -m http.server --directory shinyapps 5001

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?