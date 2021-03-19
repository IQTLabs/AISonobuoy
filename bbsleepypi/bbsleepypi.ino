#include <ArduinoJson.h>
#include "SleepyPi2.h"
#include <TimeLib.h>
#include <LowPower.h>
#include <PCF8523.h>
#include <Wire.h>

DynamicJsonDocument sensorDoc(128);

void sensorDump() {
  sensorDoc["response"] = "sensors";
  sensorDoc["rpiCurrent"] = SleepyPi.rpiCurrent();
  sensorDoc["supplyVoltage"] = SleepyPi.supplyVoltage();
  serializeJson(sensorDoc, Serial);
  Serial.println();
}

void setup() {
  SleepyPi.enablePiPower(true);
  SleepyPi.rtcInit(false);
  Serial.begin(115200);
}

void loop() {
  sensorDump();
  delay(1000);
}
