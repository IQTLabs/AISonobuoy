// IDE configuration:
//
// * Set Tools/Board/Arduino AVR Boards/Arduino Fio
// * Set Tools/Port/ttyUSB<n>
//
// Library installation:
//
// * ArduinoJson
// * CRC32
// * LowPower_LowPowerLab (needed for Sleepy Pi 2 lib)
// * PCF8523
// * Sleepy Pi 2
// * Time

#include <CRC32.h>
#include <ArduinoJson.h>
#include <EEPROM.h>
#include <SleepyPi2.h>
#include <TimeLib.h>
#include <PCF8523.h>
#include "limits.h"

typedef struct configType {
  float shutdownVoltage;
  float startupVoltage;
  float shutdownRpiCurrent;
  unsigned int snoozeTimeout;
  bool overrideEnabled;
} configType;

typedef struct eepromConfigType {
  uint32_t crc;
  configType config;
} eepromConfigType;

const configType defaultConfig {
  12.8, // shutdownVoltage: 12V-14V
  13.0, // startupVoltage: 12V-14V, less than shutdownVoltage
  150, // shutdownRpiCurrent: 50mA-800mA
  90, // snoozeTimeout: 90s-600s
  true, // overrideEnabled
};

const char fwVersion[] = "1.0.3";
const byte bufferSize = 255;
const byte alarmPin = 0;
const byte buttonPin = 1;
const byte statusLED = 13;
const byte sampleCount = 12;
const unsigned long sampleInterval = 5;
const unsigned long overrideInterval = 120;
const time_t minSnoozeDurationMin = 2;
// RTC day alarm must be set < 24h in the future to avoid wraparound.
const time_t maxSnoozeDurationMin = (24 * 60) - minSnoozeDurationMin;
// Power cycle for this long if Pi is stuck in shutdown.
#define RESETMS (3 * 1e3)

typedef struct sampleType {
  float supplyVoltage;
  float rpiCurrent;
} sampleType;

typedef struct sampleStatsType {
  float supplyVoltage;
  float rpiCurrent;
  float mean1mSupplyVoltage;
  float mean1mRpiCurrent;
  float min1mSupplyVoltage;
  float min1mRpiCurrent;
  float max1mSupplyVoltage;
  float max1mRpiCurrent;
  bool meanValid;
} sampleStatsType;

typedef struct cmdHandler {
  const char *cmd;
  void (*cmdHandlerFunc)(void);
} cmdHandler;

const cmdHandler endOfHandlers = {
  NULL, NULL,
};

bool powerState = false;
bool powerStateOverride = false;
bool requestedPowerState = true;
bool gotAlarm = false;
bool alarmSet = false;
byte i = 0;
char cmdBuffer[bufferSize] = {};
byte currentSample = 0;
sampleType samples[sampleCount] = {};
sampleStatsType sampleStats;
eepromConfigType eepromConfig;
unsigned long lastPollTime = millis();
unsigned long powerOverrideTime = 0;
unsigned long lastButtonTime = 0;
unsigned long lastButtonCheck = 0;
unsigned long snoozeTime = 0;
unsigned long lastSetPowerTime = 0;
time_t snoozeUnixtime = 0;

DynamicJsonDocument inDoc(bufferSize);
DynamicJsonDocument outDoc(bufferSize);

void buttonISR() {
  lastButtonTime = millis();
}

void enableButton() {
  attachInterrupt(buttonPin, buttonISR, LOW);
}

void setPower() {
  lastSetPowerTime = millis();
  SleepyPi.enablePiPower(powerState);
  SleepyPi.enableExtPower(powerState);
}

void alarmISR() {
  gotAlarm = true;
}

void enableAlarm() {
  SleepyPi.enableAlarm(true);
  attachInterrupt(alarmPin, alarmISR, FALLING);
  alarmSet = true;
  gotAlarm = false;
}

void disableAlarm() {
  detachInterrupt(alarmPin);
  SleepyPi.enableAlarm(false);
  alarmSet = false;
  gotAlarm = false;
}

void initRtc() {
  SleepyPi.rtcInit(true);
  // After an init, the first alarm always triggers immediately, so configure and then cancel an alarm.
  DateTime nowTime(SleepyPi.readTime());
  DateTime alarmTime(nowTime.unixtime() + 60);
  enableAlarm();
  SleepyPi.setAlarm(alarmTime.hour(), alarmTime.minute());
  disableAlarm();
}

void readEeprom() {
  uint8_t *cp = (uint8_t*)&eepromConfig;
  for (byte j = 0; j < sizeof(eepromConfigType); ++j) {
    *(cp + j) = EEPROM.read(j);
  }
}

void writeEeprom() {
  eepromConfig.crc = calcCRC();
  uint8_t *cp = (uint8_t*)&eepromConfig;
  for (byte j = 0; j < sizeof(eepromConfigType); ++j) {
    EEPROM.write(j, *(cp + j));
  }
}

uint32_t calcCRC() {
  return CRC32::calculate((uint8_t*)&eepromConfig.config, sizeof(configType));
}

void bootmsg() {
  runCmd("getconfig");
  runCmd("sensors");
}

void writeDefaultConfig() {
  memcpy(&eepromConfig.config, &defaultConfig, sizeof(defaultConfig));
  writeEeprom();
}

void setup() {
  Serial.begin(9600);
  readEeprom();
  uint32_t crc = calcCRC();
  if (crc != eepromConfig.crc) {
    writeDefaultConfig();
  }
  pinMode(statusLED, OUTPUT);
  digitalWrite(statusLED, LOW);
  memset(cmdBuffer, 0, sizeof(cmdBuffer));
  // cppcheck-suppress memsetClassFloat
  memset(&sampleStats, 0, sizeof(sampleStatsType));
  initRtc();
  enableButton();
  bootmsg();
}

bool getCmd() {
  bool gotCmd = false;
  if (Serial.available()) {
    char c = Serial.read();
    if (i == (sizeof(cmdBuffer) - 1)) {
      c = 0;
    }
    if (c == '\n' || c == '\r') {
      c = 0;
    }
    cmdBuffer[i] = c;
    if (c == 0) {
      gotCmd = true;
      i = 0;
    } else {
      ++i;
    }
  }
  return gotCmd;
}

void handleSensors() {
  sampleType *samplePtr = samples + currentSample;
  outDoc["rpiCurrent"] = samplePtr->rpiCurrent;
  outDoc["supplyVoltage"] = samplePtr->supplyVoltage;
  outDoc["mean1mSupplyVoltage"] = sampleStats.mean1mSupplyVoltage;
  outDoc["mean1mRpiCurrent"] = sampleStats.mean1mRpiCurrent;
  outDoc["min1mSupplyVoltage"] = sampleStats.min1mSupplyVoltage;
  outDoc["min1mRpiCurrent"] = sampleStats.min1mRpiCurrent;
  outDoc["max1mSupplyVoltage"] = sampleStats.max1mSupplyVoltage;
  outDoc["max1mRpiCurrent"] = sampleStats.max1mRpiCurrent;
  outDoc["meanValid"] = sampleStats.meanValid;
  outDoc["powerState"] = powerState;
  outDoc["powerStateOverride"] = powerStateOverride;
  outDoc["version"] = fwVersion;
}

void handleGetTime() {
  DateTime nowTime = SleepyPi.readTime();
  outDoc["unixtime"] = nowTime.unixtime();
  outDoc["rtcBatteryLow"] = SleepyPi.rtcBatteryLow();
  outDoc["rtcRunning"] = SleepyPi.isrunning();
}

void handleSetTime() {
  uint32_t nowUnixtime = inDoc["unixtime"];
  if (nowUnixtime == 0) {
    outDoc["error"] = "invalid unixtime";
    return;
  }
  DateTime nowTime(nowUnixtime);
  SleepyPi.setTime(nowTime);
  handleGetTime();
}

void handleSnooze() {
  time_t duration = inDoc["duration"];
  if (duration < minSnoozeDurationMin || duration > maxSnoozeDurationMin) {
    outDoc["error"] = "invalid snooze duration";
    return;
  }
  DateTime nowTime(SleepyPi.readTime());
  DateTime alarmTime(nowTime.unixtime() + (duration * 60));
  SleepyPi.setAlarm(alarmTime.hour(), alarmTime.minute());
  enableAlarm();
  outDoc["duration"] = duration;
  outDoc["alarmhour"] = alarmTime.hour();
  outDoc["alarmminute"] = alarmTime.minute();
  outDoc["alarmunixtime"] = alarmTime.unixtime();
  outDoc["hour"] = nowTime.hour();
  outDoc["minute"] = nowTime.minute();
  outDoc["unixtime"] = nowTime.unixtime();
  requestedPowerState = false;
  snoozeTime = millis();
  snoozeUnixtime = nowTime.unixtime();
}

void handleGetConfig() {
  outDoc["shutdownVoltage"] = eepromConfig.config.shutdownVoltage;
  outDoc["startupVoltage"] = eepromConfig.config.startupVoltage;
  outDoc["shutdownRpiCurrent"] = eepromConfig.config.shutdownRpiCurrent;
  outDoc["snoozeTimeout"] = eepromConfig.config.snoozeTimeout;
  outDoc["overrideEnabled"] = eepromConfig.config.overrideEnabled;
}

bool voltageValid(float voltage) {
  if (voltage < 12) {
    return false;
  }
  if (voltage > 14) {
    return false;
  }
  return true;
}

void handleSetConfig() {
  float shutdownVoltage = inDoc["shutdownVoltage"];
  float startupVoltage = inDoc["startupVoltage"];
  float shutdownRpiCurrent = inDoc["shutdownRpiCurrent"];
  unsigned int snoozeTimeout = inDoc["snoozeTimeout"];
  bool overrideEnabled = eepromConfig.config.overrideEnabled;
  if (inDoc.containsKey("overrideEnabled")) {
    overrideEnabled = bool(inDoc["overrideEnabled"]);
  }
  if (shutdownVoltage == 0) {
    shutdownVoltage = eepromConfig.config.shutdownVoltage;
  }
  if (startupVoltage == 0) {
    startupVoltage = eepromConfig.config.startupVoltage;
  }
  if (shutdownRpiCurrent == 0) {
    shutdownRpiCurrent = eepromConfig.config.shutdownRpiCurrent;
  }
  if (snoozeTimeout == 0) {
    snoozeTimeout = eepromConfig.config.snoozeTimeout;
  }
  if (!voltageValid(shutdownVoltage)) {
    outDoc["error"] = "invalid shutdownVoltage";
    return;
  }
  if (!voltageValid(startupVoltage)) {
    outDoc["error"] = "invalid startupVoltage";
    return;
  }
  if (shutdownVoltage >= startupVoltage) {
    outDoc["error"] = "startupVoltage must be greater than shutdownVoltage";
    return;
  }
  if (shutdownRpiCurrent < 50 || shutdownRpiCurrent > 800) {
    outDoc["error"] = "invalid shutdownRpiCurrent";
    return;
  }
  if (snoozeTimeout < 90 || snoozeTimeout > 600) {
    outDoc["error"] = "invalid snoozeTimeout";
    return;
  }
  eepromConfig.config.shutdownVoltage = shutdownVoltage;
  eepromConfig.config.startupVoltage = startupVoltage;
  eepromConfig.config.shutdownRpiCurrent = shutdownRpiCurrent;
  eepromConfig.config.snoozeTimeout = snoozeTimeout;
  eepromConfig.config.overrideEnabled = overrideEnabled;
  writeEeprom();
  handleGetConfig();
}

void handleDefaultConfig() {
  writeDefaultConfig();
  handleGetConfig();
}

void handleGetLastSnooze() {
  outDoc["lastsnoozeunixtime"] = snoozeUnixtime;
  outDoc["lastsnoozeuptimems"] = snoozeTime;
}

const cmdHandler getLastSnoozeCmd = {
  "getlastsnooze", &handleGetLastSnooze,
};

const cmdHandler defaultConfigCmd = {
  "defaultconfig", &handleDefaultConfig,
};

const cmdHandler setConfigCmd = {
  "setconfig", &handleSetConfig,
};

const cmdHandler getConfigCmd = {
  "getconfig", &handleGetConfig,
};

const cmdHandler snoozeCmd = {
  "snooze", &handleSnooze,
};

const cmdHandler getTimeCmd = {
  "gettime", &handleGetTime,
};

const cmdHandler setTimeCmd = {
  "settime", &handleSetTime,
};

const cmdHandler sensorsCmd = {
  "sensors", &handleSensors,
};

const cmdHandler cmdHandlers[] = {
  defaultConfigCmd,
  setConfigCmd,
  getConfigCmd,
  snoozeCmd,
  getTimeCmd,
  setTimeCmd,
  sensorsCmd,
  getLastSnoozeCmd,
  endOfHandlers,
};

void handleCmd() {
  digitalWrite(statusLED, HIGH);
  inDoc.clear();
  DeserializationError error = deserializeJson(inDoc, cmdBuffer);
  outDoc.clear();
  outDoc["command"] = "unknown";
  if (error) {
    outDoc["error"] = error.f_str();
  } else {
    char *cmd = inDoc["command"];
    if (cmd) {
      outDoc["command"] = cmd;
      outDoc["error"] = "unknown command";
      for (byte j = 0; cmdHandlers[j].cmd; ++j) {
        const char *compareCmd = cmdHandlers[j].cmd;
        if (strncmp(cmd, compareCmd, strlen(compareCmd)) == 0) {
          outDoc["error"] = "";
          cmdHandlers[j].cmdHandlerFunc();
          break;
        }
      }
    } else {
      outDoc["error"] = "missing command";
    }
    outDoc["uptimems"] = millis();
  }
  outDoc["version"] = fwVersion;
  serializeJson(outDoc, Serial);
  Serial.println();
  memset(cmdBuffer, 0, sizeof(cmdBuffer));
  digitalWrite(statusLED, LOW);
}

void runCmd(const char *cmd) {
  sprintf(cmdBuffer, "{\"command\": \"%s\"}\n", cmd);
  handleCmd();
}

#define RUNNING_MAX(x, y) x = max(x, y)
#define RUNNING_MIN(x, y) x = min(x, y)

void pollSample() {
  digitalWrite(statusLED, HIGH);
  if (++currentSample == sampleCount) {
    currentSample = 0;
  }
  sampleType *samplePtr = samples + currentSample;
  samplePtr->supplyVoltage = SleepyPi.supplyVoltage();
  samplePtr->rpiCurrent = SleepyPi.rpiCurrent();
  sampleStats.supplyVoltage = samplePtr->supplyVoltage;
  sampleStats.rpiCurrent = samplePtr->rpiCurrent;

  sampleStats.mean1mSupplyVoltage = 0;
  sampleStats.mean1mRpiCurrent = 0;
  sampleStats.min1mSupplyVoltage = sampleStats.supplyVoltage;
  sampleStats.min1mRpiCurrent = sampleStats.rpiCurrent;
  sampleStats.max1mSupplyVoltage = sampleStats.supplyVoltage;
  sampleStats.max1mRpiCurrent = sampleStats.rpiCurrent;
  sampleStats.meanValid = false;

  byte validSamples = 0;
  for (byte j = 0; j < sampleCount; ++j) {
    samplePtr = samples + j;
    if (samplePtr->supplyVoltage == 0 && samplePtr->rpiCurrent == 0) {
      continue;
    }
    ++validSamples;
    sampleStats.mean1mSupplyVoltage += samplePtr->supplyVoltage;
    sampleStats.mean1mRpiCurrent += samplePtr->rpiCurrent;
    RUNNING_MIN(sampleStats.min1mSupplyVoltage, samplePtr->supplyVoltage);
    RUNNING_MIN(sampleStats.min1mRpiCurrent, samplePtr->rpiCurrent);
    RUNNING_MAX(sampleStats.max1mSupplyVoltage, samplePtr->supplyVoltage);
    RUNNING_MAX(sampleStats.max1mRpiCurrent, samplePtr->rpiCurrent);
  }

  sampleStats.mean1mSupplyVoltage /= validSamples;
  sampleStats.mean1mRpiCurrent /= validSamples;
  sampleStats.meanValid = (validSamples == sampleCount);
  digitalWrite(statusLED, LOW);
}

unsigned long timeDiff(unsigned long x, unsigned long nowTime) {
  if (nowTime >= x) {
    return nowTime - x;
  }
  return (ULONG_MAX - x) + nowTime;
}

bool timedOut(unsigned long x, unsigned long nowTime, unsigned long timeoutSecs) {
  return timeDiff(x, nowTime) > (timeoutSecs * 1000);
}

void loop() {
  if (getCmd()) {
    handleCmd();
  }
  if (gotAlarm) {
    requestedPowerState = true;
    disableAlarm();
    bootmsg();
  }
  unsigned long nowTime = millis();
  if (timedOut(lastPollTime, nowTime, sampleInterval)) {
    pollSample();
    lastPollTime = nowTime;
  }
  if (lastButtonCheck != lastButtonTime) {
    lastButtonCheck = lastButtonTime;
    if (eepromConfig.config.overrideEnabled) {
      powerOverrideTime = nowTime;
      powerState = !powerState;
      requestedPowerState = powerState;
      setPower();
    }
  }
  powerStateOverride = lastButtonCheck && !timedOut(powerOverrideTime, nowTime, overrideInterval);

  if (!powerStateOverride && sampleStats.meanValid) {
    if (powerState) {
      // shutdown voltage for at least 1m
      bool shutdownVoltage = sampleStats.mean1mSupplyVoltage < eepromConfig.config.shutdownVoltage;

      // shutdown on low voltage, no matter if Pi is on or off.
      if (shutdownVoltage) {
        powerState = false;
        setPower();
      } else {
        // In shutdown current for at least 1m
        bool shutdownRpiCurrent = sampleStats.mean1mRpiCurrent < eepromConfig.config.shutdownRpiCurrent;

        // Pi is on, did not request a shutdown, but is drawing only shutdown current for 1m. Reset it,
        // with at least snoozeTimeout seconds between power cycle attempts.
        if (requestedPowerState) {
          bool setPowerTimeout = timedOut(lastSetPowerTime, nowTime, eepromConfig.config.snoozeTimeout);

          if (shutdownRpiCurrent && setPowerTimeout) {
            powerState = false;
            setPower();
            delay(RESETMS);
            powerState = true;
            setPower();
          }
        // Pi is on, requested a shutdown, and is now drawing shutdown current or timed out waiting for shutdown current.
        } else {
          bool snoozeTimedOut = timedOut(snoozeTime, nowTime, eepromConfig.config.snoozeTimeout);

          if (shutdownRpiCurrent || snoozeTimedOut) {
            powerState = false;
            setPower();
          }
        }
      }
    } else {
      bool startupVoltage = sampleStats.mean1mSupplyVoltage >= eepromConfig.config.startupVoltage;

      if (startupVoltage && requestedPowerState) {
        powerState = true;
        setPower();
      }
    }
  }
}
