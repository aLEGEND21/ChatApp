echo building image
sudo docker build -t chatapp .

echo removing old container
sudo docker rm -f chatapp

echo starting container
sudo docker run -d --name chatapp -p 2001:2001 --network=nginx-proxy --env-file ./.env chatapp