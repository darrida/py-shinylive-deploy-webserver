FROM    python:3.12-slim

# SSH
RUN     apt-get update && apt-get -y install openssh-server
RUN     mkdir -p /var/run/sshd

# RUN     echo StrictHostKeyChecking no >> /etc/ssh/ssh_config
# RUN     ssh-keygen -t rsa -b 4096 -f ssh_host_rsa_key
RUN     /usr/bin/ssh-keygen -A
RUN     mkdir -p /var/run/sshd
RUN     service ssh restart

# change password root
RUN     useradd --create-home --shell /bin/bash  shinylive
RUN     echo "shinylive:docker" | chpasswd
USER    shinylive
WORKDIR /home/shinylive
RUN     mkdir /home/shinylive/shinyapps

USER root
EXPOSE  5001
EXPOSE  22

COPY entrypoint.sh .

CMD bash ./entrypoint.sh