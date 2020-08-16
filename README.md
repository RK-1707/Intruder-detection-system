# Intruder-detection-system
- Accessing the Live stream from your phone and delivering it to the program. This can be done by sending the video over a local server, for which the IP address can be found using an app called "IP WEBCAM" which is available on Google appstore.

- While using the app everytime a new IP address will be generated this is because the device in charge of allocating the IPs is your WiFi router. The IP allocation ("lease") is given for some time and can change after it's expired. This might make IP Webcam inaccessible by the previous address.To prevent this from happening, you need to enter the router's web interface and allocate your device a static IP. Search for menu items similar to "DHCP clients", "Static leases" or "IP/MAC binding", and add an MAC binding here to the desired or current IP.MAC address of your phone can be found in Settings->About Phone->Status->WiFi MAC address.

- Once this is done put the IP address obtained in the code for it to work.

- To send an alert to mobile device we make use of the "Twilio API", and therefore we need to install the twilio library first. After installation we need to get the acc. no. and the acc. token from the website and put this in the credentials.txt, and also change the mobile number.
