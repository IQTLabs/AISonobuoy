#include <ArduinoJson.h>
#include <SleepyPi2.h>
#include <TimeLib.h>
#include <LowPower.h>
#include <PCF8523.h>
#include <Wire.h>

byte i = 0;
char cmdBuffer[64] = {};

const char sensorsCmd[] = "sensors";

DynamicJsonDocument inDoc(128);
DynamicJsonDocument outDoc(128);

void sensorDump() {
  outDoc["rpiCurrent"] = SleepyPi.rpiCurrent();
  outDoc["supplyVoltage"] = SleepyPi.supplyVoltage();
}

void setup() {
  memset(cmdBuffer, 0, sizeof(cmdBuffer));
  SleepyPi.enablePiPower(true);
  SleepyPi.rtcInit(false);
  Serial.begin(9600);
  Serial.println("Hello");
}

void loop() {
  bool gotCmd = false;
  if (Serial.available()) {
    char c = Serial.read();
    if (i == (sizeof(cmdBuffer) - 1)) {
      c = 0;
    }
    if (c == '\n') {
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
  if (gotCmd) {
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
        outDoc["error"] = "";
        if (strncmp(cmd, sensorsCmd, strlen(sensorsCmd)) == 0) {
          sensorDump();
        } else {
          outDoc["error"] = "unknown command";
        }
      } else {
        outDoc["error"] = "missing command";
      }
    }
    serializeJson(outDoc, Serial);
    Serial.println();
  }
}
