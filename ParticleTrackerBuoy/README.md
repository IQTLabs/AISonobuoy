# ParticleTrackerBuoy

## About

The Particle Tracker Buoy is an implementation of an Edge AI Detection device. It is intended to demonstrate the concept of an AI Sonobuoy. 

<img src="media/AISonobuoy.png" alt="" height="400px" title="">

## Hardware

The Particle Tracker Buoy was designed to use low-cost and easily accessible components.

- Particle.io Tracker SOM
- Myriota Dev Kit
- Adafruit nRF52840 Sense MCU
- Adafruit Featherwing Quadrupler
- Adafruit Electret MAX4466 AMP
- Adafruit lithium ion 6600mAh battery
- 4in PVC pipe components
- 3D Printed chassis ([STL Files](stl-files))

<img src="media/AISonobuoy-explode.png" alt="" height="400px" title="">

[STL Files](stl-files)

## Wiring

```
┌───────────────┐     ┌────────────┐     ┌────────────┐     ┌───────────┐     ┌────────────┐
│   [SATCOM]    │     │[C&C /TELEM]│     │  [ML MCU]  │     │[AUDIO AMP]│     │[HYDROPHONE]│
│               │     │            │     │            │     │           │     │            │
│    Myriota    │     │  Particle  │     │  nRF52840  │     │  MAX4466  │     │  Aquarian  │
│      Dev      │     │  Tracker   │     │   Sense    │     │           │     │    H2A     │
│      Kit      │     │            │     │            │     │           │     │            │
│               │     │            │     │            │     │           │     │            │
│               │     │            │     │            │     │           │     │            │
│   26/LEUART TX├─────┤UART RX     │     │          A0├─────┤VCC        │     │            │
│   28/LEUART RX├─────┤UART TX     │     │          A1├─────┤OUT────────┼─────┤RED         │
│               │     │            │     │            │     │           │     │            │
│               │     │      A0/SDA├───┬─┤A4/SDA      │     │        MIC├─────┤GREEN       │
│               │     │            │   │ │            │     │           │     │            │
│               │     │      A1/SCL├─┬─┼─┤A5/SCL      │     │        GND├─────┤BLACK       │
│               │     │            │ │ │ │            │     │           │     │            │
│               │     │            │ │ │ │            │     │           │     │            │
│ VEXT          │     │            │ 1 1 │            │     │           │     │            │
│ /3.3      GND │     │ 3.3    GND │ 0 0 │ 3.3    GND │     │      GND  │     │            │
└──┬─────────┬──┘     └──┬──────┬──┘ k k └──┬──────┬──┘     └───────┬───┘     └────────────┘
   │         │           │      │    │ │    │      │                │
   │                     │           │ │    │
   └─────────────────────┴───────────┴─┴────┘
```

## Software

- The Particle Tracker firmware and flashing instructions are located in the [aisonobuoy-particle-tracker](./aisonobuoy-particle-tracker/) submodule.

- The Myriota Modem firmware and flashing instructions are located in the [modem-myriota](./modem-myriota) submodule