node_id=$1

sudo cat > /etc/network/interfaces <<- ENDCONF
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
    address 192.168.1.$node_id
    netmask 255.255.255.0
    gateway 192.168.1.100

auto wlan0
iface wlan0 inet6 static
     address fc01::$node_id
     netmask 64
     wireless-channel 6
     wireless-essid RCM-Mesh
     wireless-mode ad-hoc
ENDCONF

sudo apt-get update -y
sudo apt-get install python-picamera -y
sudo apt-get install zbar-tools -y
sudo apt-get install python-zbar -y

sudo ifdown lo
sudo ifup lo
sudo ifdown eth0
sudo ifup eth0
sudo ifdown wlan0
sudo ifup wlan0

sudo reboot
