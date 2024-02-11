echo building image
sudo docker build -t chatapp .

echo removing old container
sudo docker rm -f chatapp

echo starting container
sudo docker run -d --name chatapp -p 5000:5000 --network=nginx-proxy --env-file=. chatapp