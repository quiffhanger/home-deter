# home-deter
Automation of intruder deterrence measures.

Usage: 
1) cp config.py.sample config.py
2) pip3 install -r requirements.txt   
2) Edit config.py to add in details of your shellys (e.g. tell it which relays are lights to include)
3) Set lights_away.py to run as a cron job for the times you need it. You can tweak schedule and probabilities depending on how often you wants lights on
    * Example cronjob: "*/7 20,21,22,23,0-6 * * * /home/pi/home-deter/lights_away.py >> /home/pi/lights.log 2>&1" will run every 7mins during the night. Default config means every light has a 10% chance of being turned on for a period between 30-3600seconds.
