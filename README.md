# Home Assistant Utility Bill Reader

I monitor my energy usage with Home Assistant and would like to know the cost. You can tell Home Assistant to reference a sensor value to calculate the cost of the energy usage, so this script helps parse the PDF I get from my utility and updates that sensor value.

This will need heavy modifications for your use, you'd have to mess about with the specific regexes and update the name of the sensor in `processor.py` for one. I run this on a cron every minute to look for new PDFs in a "dropbox" folder I have set up.
