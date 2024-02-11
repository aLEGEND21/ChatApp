# This should only be run directly and located one directory above the project
echo y | docker image prune
rm -rf chatapp
git clone https://github.com/aLEGEND21/ChatApp.git
cd ChatApp
bash run.sh