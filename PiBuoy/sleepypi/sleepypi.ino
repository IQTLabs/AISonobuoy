// IDE configuration:
//
// * Set Tools/Board/Arduino AVR Boards/Arduino Fio
// * Set Tools/Port/ttyUSB<n>

#include <ArduinoJson.h>
#include <SleepyPi2.h>
#include <TimeLib.h>
#include <LowPower.h>
#include <PCF8523.h>
#include <Wire.h>

const byte statusLED = 13;

typedef struct cmdHandler {
  const char *cmd;
  void (*cmdHandlerFunc)(void);
} cmdHandler;

const cmdHandler endOfHandlers = {
  NULL, NULL,
};

byte i = 0;
char cmdBuffer[64] = {};
unsigned long lastOutputTime = millis();

DynamicJsonDocument inDoc(128);
DynamicJsonDocument outDoc(128);

void setup() {
  pinMode(statusLED, OUTPUT);
  digitalWrite(statusLED, LOW);
  memset(cmdBuffer, 0, sizeof(cmdBuffer));
  SleepyPi.enablePiPower(true);
  SleepyPi.enableExtPower(true);
  SleepyPi.rtcInit(true);
  Serial.begin(9600);
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
  outDoc["rpiCurrent"] = SleepyPi.rpiCurrent();
  outDoc["supplyVoltage"] = SleepyPi.supplyVoltage();
}

const cmdHandler sensorsCmd = {
  "sensors", &handleSensors,
};

const cmdHandler cmdHandlers[] = {
  sensorsCmd,
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
  }
  serializeJson(outDoc, Serial);
  Serial.println();
  memset(cmdBuffer, 0, sizeof(cmdBuffer));
  digitalWrite(statusLED, LOW);
}

void runCmd(const char *cmd) {
  sprintf(cmdBuffer, "{\"command\": \"%s\"}\n", cmd);
  handleCmd();
}

void loop() {
  if (getCmd()) {
    handleCmd();
  }
  unsigned long nowTime = millis();
  if (nowTime - lastOutputTime > 10000 || nowTime < lastOutputTime) {
    runCmd("sensors");
    lastOutputTime = nowTime;
  }
}
