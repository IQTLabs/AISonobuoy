import pijuice, time, os

while not os.path.exists('/dev/i2c-1'):
    time.sleep(0.1)

pj = pijuice.PiJuice(1, 0x14)

pj.config.SetBatteryProfile('PJLIPO_12000')
pj.rtcAlarm.SetWakeupEnabled(True)

# get stats and write out to file
# set config for wakeup/shutdown
