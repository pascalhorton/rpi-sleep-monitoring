# Raspberry Pi sleep monitoring

A collection of sensors to monitor sleep and its environment.

## Sensors

In addition to the Raspberry Pi and the Grove Base Hat for Raspberry Pi:

* Grove - Loudness Sensor
* PIR Infrared Motion Sensor (HC-SR501)	
* Grove - 80cm Infrared Proximity Sensor
* Grove - Button
* Grove - Light Sensor v1.2	
* Grove - Temperature & Humidity Sensor Pro
* Grove - Multi Color Flash LED (5mm)


## Getting started

Install Python 3:
```
sudo apt update
sudo apt install python3 idle3
```

Install Grove basis:
```
git clone https://github.com/Seeed-Studio/grove.py
cd grove.py
pip3 install .
```

Install Grove - Temperature&Humidity Sensor:
```
pip3 install seeed-python-dht
```

Install other dependencies:
```
pip3 install matplotlib pandas
```

Clone the repo:
```
git clone https://github.com/pascalhorton/rpi-sleep-monitoring
```

Create some dirs:
```
mkdir ~/monitoring
mkdir ~/monitoring-plots
```


## Automate

Set the monitoring to automatically start after boot:
* sudo nano /etc/rc.local
* Add the following line after the header: 
```
python3 /home/pi/rpi-sleep-monitoring/sleep_monitoring.py /home/pi/monitoring
```

Set the creation of the (10 last) plots every 5 minutes:
* crontab -e
* Add the following line: 
```
*/5 * * * * python3 /home/pi/rpi-sleep-monitoring/update_plots.py /home/pi/monitoring /home/pi/monitoring-plots 10
```


## Optional

* Mount (/etc/fstab) a directory from a server (e.g. NAS) in /home/pi/monitoring-plots 
```
[IP address]:/path/to/shared/folder/on/NAS /home/pi/monitoring-plots/  nfs  nofail,user,x-systemd.automount,x-systemd.requires=network-online.target,x-systemd.device-timeout=10  0  0
```
* If not mounting the share automatically, add the following to ~/.bashrc (end):
```
mount /home/pi/monitoring-plots/
```
