set -x
sudo apt-get -y update
sudo apt-get -y install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio
sudo apt-get -y install ffmpeg 
sudo apt-get -y install python3-numpy
sudo apt-get -y install python3-pip
pip install opencv-python
echo 'export PATH="$PATH:~/bin"'>> ~/.profile
echo "You may need to login to ubuntu again for opencv to work."
