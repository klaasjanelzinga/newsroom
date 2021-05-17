adduser klaasjan
usermod -aG sudo klaasjan

in /etc/ssh/sshd_config PermitRootLogin -> no

apt update
apt upgrade

apt install nginx certbot python3-certbot-nginx

reboot

sudo mkdir /usr/newsroom
sudo chown klaasjan:klaasjan /usr/newsroom

@local:
scp infra/nginx/api-newsroom.n-kj.nl.conf test.n-kj.nl:
scp infra/nginx/newsroom.n-kj.nl.conf test.n-kj.nl:

@test.n-kj.nl
sudo mv api-newsroom.n-kj.nl /etc/nginx/sites-available
sudo mv newsroom.n-kj.nl /etc/nginx/sites-available

sudo ln -s /etc/nginx/sites-available/api-newsroom.n-kj.nl.conf /etc/nginx/sites-enabled/api-newsroom.n-kj.nl.conf
sudo ln -s /etc/nginx/sites-available/newsroom.n-kj.nl.conf /etc/nginx/sites-enabled/newsroom.n-kj.nl.conf

sudo apt install docker.io docker-compose

@local
scripts/scp_to_host.sh

@test.n-kj.nl
cd /usr/newsroom
docker login ghcr.io
docker-compose -f docker-compose-live.yml --env-file etc/production.env pull
docker-compose -f docker-compose-live.yml --env-file etc/production.env up --detach

sudo certbot --nginx
