# AISonobuoy
Maritime Situational Awareness: An Exploration

# About
TODO

# Configurations

## PiBuoy

A buoy designed to run an 8GB Raspberry Pi4 with poower management that can do collection of audio via a hydrophone. It can be equipped with an AIS reciever and other sensors such as GPS, LTE, temperature and a 9-axis gryoscope. The form factor is designed to support 2 solar panels and a 30Ah battery.

See [PiBuoy/README.md](PiBuoy/README.md)

## FeatherBuoy

A buoy designed to support the Adafruit [FeatherWing Tripler](https://www.adafruit.com/product/3417) base board which supports Feather MCU's (Particle, Arduino M0, etc)​ and accessories. Buoy form factor is based on the [MakerBuoy](https://github.com/wjpavalko/Maker-Buoy) design.

See [FeatherBuoy/README.md](FeatherBuoy/README.md)

# Deployments

## PiBuoy

Having deployed the first buoy, PiBuoy v1 Mark I, that was designed from the ground up (several learnings were integrated from the [Maker Buoy](https://www.makerbuoy.com/)) for data collection for this project before replicating the buildout of it proved more difficult than expected. Recently, while trying to remotely replicate the Mark I, there was difficulty in making the [Sixfab 3G-4G/LTE Base HAT](https://sixfab.com/product/raspberry-pi-4g-lte-modem-kit/) (the data connection for the buoy) work with the cell network provider we had chosen despite having seemingly configured everything correctly.

<img src="/docs/img/sixfab_buoy.jpg" height="300" alt="Sixfab HAT on top of a RaspberryPi, additional wiring in the configuration for the buoy"/>

Not having a spare SIM card attached to a network provider to reproduce the setup locally proved difficult at first, until the idea of leveraging the work from [Daedalus]( https://github.com/IQTLabs/Daedalus) came to mind. With Daedalus, one can provision their own SIM card with whatever APN and settings they’d like and connect devices using a software-defined radio (SDR) to create a private 4G LTE/5G network that provides a data connection over the network connection of the machine running Daedalus. Using the [Daedalus tool]( https://github.com/IQTLabs/Daedalus/blob/main/blue/README.md), we were able to demonstrate the settings on the Sixfab and modem were configured correctly which greatly reduced the amount of remote debugging that was needed.

<img src="/docs/img/sixfab_bladerf.jpg" height="300" alt="Sixfab with SIM card on top of a RaspberryPi next to the BladeRF SDR"/>

In this case, the issue ended up being extremely poor signal inside of an office building, that once cleanly started in an environment that had a clear signal the connection worked as expected.
