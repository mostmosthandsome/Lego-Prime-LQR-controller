# Lego Prime controller
## I.Lego Hub environment configuration

If you are using a well prepared lego hub (for example, optimization course), just skip this step
Otherwise, follow the instructions on https://code.pybricks.com/ to rewrite the OS
![截图 2024-06-16 20-00-40](https://github.com/mostmosthandsome/Lego-Prime-LQR-controller/assets/121703002/e313d776-80c0-4067-847f-5be11d25e566)



## II. environment configuration
We suggest using Ubuntu
### 1.install bleak
We use bleak to connect to hub by bluetooth
```bash
pip install bleak
```
### 2.install bluetooth scanner (for Ubuntu)
We need to install blueman to help doing bluetooth scan
```bash
sudo apt update
sudo apt install blueman
sudo apt install bluez bluez-obexd
```
Then you can search for blueman in your system applications
![截图 2024-06-16 20-12-09](https://github.com/mostmosthandsome/Lego-Prime-LQR-controller/assets/121703002/0add50bd-1b27-4aa5-aa80-9e2d9599c73a)

### 3.install Chrome
Because Chrome can support bluetooth connection

## III.test
open your chrome browser and open website https://code.pybricks.com/
load "motor_test.py" in folder "hub_code"
click the bluetooth icon and you can see a device like this (be sure that you have start the lego hub)
![截图 2024-06-16 20-19-59](https://github.com/mostmosthandsome/Lego-Prime-LQR-controller/assets/121703002/7ae56292-230d-4aec-b2e4-195a72a8cea9)
run it, and you will find the motor is running


## Introduction
a project using Lego Spike Prime to do a balance car
First run the ble.py in pybricks gui in order to upload it to the hub
After that, disconnect from the hub and run the connect.py in project

