# This script is used to setup SSH for public internet requests on Ubuntu 18.04
# Port forwarding on port 22 must still be manually configured on the router

service ssh restart
sudo ufw allow ssh
systemctl status ssh