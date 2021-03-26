#include <SPI.h>
#include <RH_RF95.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// OLED FeatherWing buttons map to different pins depending on board
// 32u4, M0, M4, nrf52840 and 328p
Adafruit_SSD1306 display = Adafruit_SSD1306(128, 32, &Wire);
#define BUTTON_A  9
#define BUTTON_B  6
#define BUTTON_C  5

/* lora for feather m0 */
#define RFM95_CS 8
#define RFM95_RST 4
#define RFM95_INT 3

#define dAISy Serial1
int esc = 27;  //ascii escape key

int16_t packetnum = 0;  // packet counter, we increment per xmission
// Change to 434.0 or other frequency, must match RX's freq!
#define RF95_FREQ 433.0
// Singleton instance of the radio driver
RH_RF95 rf95(RFM95_CS, RFM95_INT);
char radiopacket[20] = "Hello World #      ";

void setup() {
  Serial.begin(115200);
  dAISy.begin(38400);

  oled_setup();
  lora_setup();
}

void loop() {  
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'm') {
      dAISy.write(esc);
    } else {
      dAISy.write(c);
    }
  }
  boolean clear_display = false;
  int counter=0;
  while (dAISy.available()) {
    if (!clear_display) {
      display.clearDisplay();
      display.display();
      display.setCursor(0,0);
      clear_display=true;
    }
    
    char c = dAISy.read();
    display.write(c);
    Serial.write(c);
    if (counter < 20) {
    radiopacket[counter]=c;
    }
    counter++;
  }

  if (clear_display) {
        delay(10);
    rf95.send((uint8_t *)radiopacket, 20);
  
    Serial.println("Waiting for packet to complete..."); 
    delay(10);
    rf95.waitPacketSent();
  }

  if(!digitalRead(BUTTON_A)) {
    display.clearDisplay();
    display.display();
    display.setCursor(0,0);
    delay(2000);
    dAISy.write(esc);
  } else if(!digitalRead(BUTTON_B)) {
    display.clearDisplay();
    display.display();
    display.setCursor(0,0);
    delay(2000);
    dAISy.write('T');
    dAISy.write('\r');
  } else if(!digitalRead(BUTTON_C)) {
    display.clearDisplay();
    display.display();
    display.setCursor(0,0);
    radiopacket[0]='T';
    radiopacket[1]='E';
    radiopacket[2]='S';
    radiopacket[3]='T';
    itoa(packetnum++, radiopacket+13, 10);
    Serial.print("Sending "); Serial.println(radiopacket);
    display.print("Sending "); display.println(radiopacket);
    
    Serial.println("Sending...");
    delay(10);
    rf95.send((uint8_t *)radiopacket, 20);
  
    Serial.println("Waiting for packet to complete..."); 
    delay(10);
    rf95.waitPacketSent();
  }
  
  display.display();
}

void oled_setup() {
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C); // Address 0x3C for 128x32
  // Show image buffer on the display hardware.
  // Since the buffer is intialized with an Adafruit splashscreen
  // internally, this will display the splashscreen.
  display.display();
  delay(5000);
  // Clear the buffer.
  display.clearDisplay();
  display.display();

  pinMode(BUTTON_A, INPUT_PULLUP);
  pinMode(BUTTON_B, INPUT_PULLUP);
  pinMode(BUTTON_C, INPUT_PULLUP);
 
  // text display tests
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0,0);
  display.display(); // actually display all of the above
}

void lora_setup() {
  pinMode(RFM95_RST, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);

  Serial.println("Feather LoRa TX Test!");

  // manual reset
  digitalWrite(RFM95_RST, LOW);
  delay(10);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);

  while (!rf95.init()) {
    Serial.println("LoRa radio init failed");
    Serial.println("Uncomment '#define SERIAL_DEBUG' in RH_RF95.cpp for detailed debug info");
    while (1);
  }
  Serial.println("LoRa radio init OK!");
  display.println("LoRa radio init OK!");

  // Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM
  if (!rf95.setFrequency(RF95_FREQ)) {
    Serial.println("setFrequency failed");
    while (1);
  }
  Serial.print("Set Freq to: "); Serial.println(RF95_FREQ);
  display.print("Set Freq to: "); display.println(RF95_FREQ);
  // Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on

  // The default transmitter power is 13dBm, using PA_BOOST.
  // If you are using RFM95/96/97/98 modules which uses the PA_BOOST transmitter pin, then 
  // you can set transmitter powers from 5 to 23 dBm:
  rf95.setTxPower(23, false);
}
