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
// * Time 1.6.1

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
const byte bufferSize = 192;
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
  const char *(*cmdHandlerFunc)(void);
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

DynamicJsonDocument doc(bufferSize);

void buttonISR() {
  lastButtonTime = millis();
}

void enableButton() {
  attachInterrupt(buttonPin, buttonISR, FALLING);
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

void validateEeprom() {
  uint32_t crc = calcCRC();
  if (crc != eepromConfig.crc) {
    writeDefaultConfig();
  }
}

void setup() {
  Serial.begin(9600);
  readEeprom();
  validateEeprom();
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
      i = 0;
      return true;
    } else {
      ++i;
    }
  }
  return false;
}

const char *handleSensors() {
  sampleType *samplePtr = samples + currentSample;
  doc["rpiCurrent"] = samplePtr->rpiCurrent;
  doc["supplyVoltage"] = samplePtr->supplyVoltage;
  doc["mean1mSupplyVoltage"] = sampleStats.mean1mSupplyVoltage;
  doc["mean1mRpiCurrent"] = sampleStats.mean1mRpiCurrent;
  doc["min1mSupplyVoltage"] = sampleStats.min1mSupplyVoltage;
  doc["min1mRpiCurrent"] = sampleStats.min1mRpiCurrent;
  doc["max1mSupplyVoltage"] = sampleStats.max1mSupplyVoltage;
  doc["max1mRpiCurrent"] = sampleStats.max1mRpiCurrent;
  doc["meanValid"] = sampleStats.meanValid;
  doc["powerState"] = powerState;
  doc["powerStateOverride"] = powerStateOverride;
  return "";
}

const char *handleGetTime() {
  DateTime nowTime = SleepyPi.readTime();
  doc["unixtime"] = nowTime.unixtime();
  doc["rtcBatteryLow"] = SleepyPi.rtcBatteryLow();
  doc["rtcRunning"] = SleepyPi.isrunning();
  return "";
}

const char *handleSetTime() {
  uint32_t nowUnixtime = doc["unixtime"];
  if (nowUnixtime == 0) {
    return "invalid unixtime";
  }
  DateTime nowTime(nowUnixtime);
  SleepyPi.setTime(nowTime);
  handleGetTime();
  return "";
}

const char *handleSnooze() {
  time_t duration = doc["duration"];
  if (duration < minSnoozeDurationMin || duration > maxSnoozeDurationMin) {
    return "invalid snooze duration";
  }
  DateTime nowTime(SleepyPi.readTime());
  DateTime alarmTime(nowTime.unixtime() + (duration * 60));
  SleepyPi.setAlarm(alarmTime.hour(), alarmTime.minute());
  enableAlarm();
  doc["duration"] = duration;
  doc["alarmhour"] = alarmTime.hour();
  doc["alarmminute"] = alarmTime.minute();
  doc["alarmunixtime"] = alarmTime.unixtime();
  doc["hour"] = nowTime.hour();
  doc["minute"] = nowTime.minute();
  doc["unixtime"] = nowTime.unixtime();
  requestedPowerState = false;
  snoozeTime = millis();
  snoozeUnixtime = nowTime.unixtime();
  return "";
}

const char *handleGetConfig() {
  doc["shutdownVoltage"] = eepromConfig.config.shutdownVoltage;
  doc["startupVoltage"] = eepromConfig.config.startupVoltage;
  doc["shutdownRpiCurrent"] = eepromConfig.config.shutdownRpiCurrent;
  doc["snoozeTimeout"] = eepromConfig.config.snoozeTimeout;
  doc["overrideEnabled"] = eepromConfig.config.overrideEnabled;
  return "";
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

const char *handleSetConfig() {
  float shutdownVoltage = doc["shutdownVoltage"];
  float startupVoltage = doc["startupVoltage"];
  float shutdownRpiCurrent = doc["shutdownRpiCurrent"];
  unsigned int snoozeTimeout = doc["snoozeTimeout"];
  bool overrideEnabled = eepromConfig.config.overrideEnabled;
  if (doc.containsKey("overrideEnabled")) {
    overrideEnabled = bool(doc["overrideEnabled"]);
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
    return "invalid shutdownVoltage";
   }
  if (!voltageValid(startupVoltage)) {
    return "invalid startupVoltage";
  }
  if (shutdownVoltage >= startupVoltage) {
    return "startupVoltage must be greater than shutdownVoltage";
  }
  if (shutdownRpiCurrent < 50 || shutdownRpiCurrent > 800) {
    return "invalid shutdownRpiCurrent";
  }
  if (snoozeTimeout < 90 || snoozeTimeout > 600) {
    return "invalid snoozeTimeout";
  }
  eepromConfig.config.shutdownVoltage = shutdownVoltage;
  eepromConfig.config.startupVoltage = startupVoltage;
  eepromConfig.config.shutdownRpiCurrent = shutdownRpiCurrent;
  eepromConfig.config.snoozeTimeout = snoozeTimeout;
  eepromConfig.config.overrideEnabled = overrideEnabled;
  writeEeprom();
  return handleGetConfig();
}

const char *handleDefaultConfig() {
  writeDefaultConfig();
  return handleGetConfig();
}

const char *handleGetLastSnooze() {
  doc["lastsnoozeunixtime"] = snoozeUnixtime;
  doc["lastsnoozeuptimems"] = snoozeTime;
  return "";
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
  doc.clear();
  DeserializationError error = deserializeJson(doc, cmdBuffer);
  const char *errPtr = NULL;
  if (error) {
    doc.clear();
  } else {
    char *cmd = doc["command"];
    errPtr = "unknown command";
    if (cmd) {
      for (byte j = 0; cmdHandlers[j].cmd; ++j) {
        const char *compareCmd = cmdHandlers[j].cmd;
        if (strncmp(cmd, compareCmd, strlen(compareCmd)) == 0) {
          errPtr = cmdHandlers[j].cmdHandlerFunc();
          break;
        }
      }
    } else {
      errPtr = "missing command";
    }
  }
  if (errPtr == NULL) {
    doc["error"] = error.f_str();
  } else {
    doc["error"] = errPtr;
  }
  doc["uptimems"] = millis();
  doc["version"] = fwVersion;
  serializeJson(doc, Serial);
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
