# This should only be run directly and located one directory above the project
echo y | docker image prune
mv ChatApp/.env .env
rm -rf ChatApp
git clone https://github.com/aLEGEND21/ChatApp.git
mv .env ChatApp/.env
cd ChatApp
bash run.sh