#!/usr/bin/bash

sudo apt-get remove docker docker-engine docker.io containerd runc
sudo apt-get update -y
sudo apt-get upgrade -y

sudo apt-get install  -y   ca-certificates     curl     gnupg   lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo   "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian   $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update

sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

curl -SL https://github.com/docker/compose/releases/download/v2.6.0/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose


cat > ~/docker-compose.yml <<EOF
version: '3.7'

services:

  recursor:
    image: pschiffe/pdns-recursor
    ports:
      - 53535:53/udp
      - 53535:53/tcp
    environment:
      PDNS_local_address: 0.0.0.0
      PDNS_allow_from: 0.0.0.0/0
      # PDNS_dnssec: validate
EOF

/usr/sbin/iptables -A INPUT -p udp --dport 53535 -s 130.149.230.75 -j ACCEPT
/usr/sbin/iptables -A INPUT -p udp --dport 53535  -j REJECT

sudo apt-get install -y nginx-light
rm /var/www/html/index.nginx-debian.html

cat > /var/www/html/index.txt <<EOF
This is a research server at the chair of security in telecommunication at TU Berlin, Germany.
=============================================================================================

If you came here because of traffic to your network, you're likely subject to our good-will, well-intentioned research activities (i.e. internet measurements).

In case you would like not to be scanned by us again, please reach out with a list of subnets to neef [-a.tt ] tu-berlin D0T de, so we can include you in our block list.
Feel also free to contact us if you have any inquiries, questions or feedback for us.

Thanks
Sebastian N.
EOF

sed -e 's/index index.html index.htm index.nginx-debian.html/index index.html index.htm index.nginx-debian.html index.txt/g' -i /etc/nginx/sites-available/default

systemctl restart nginx
