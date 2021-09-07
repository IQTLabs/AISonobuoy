# Flashing the firmward onto the SleepyPi

1. Install the programming board onto the SleepyPi like pictured [here](https://spellfoundry.com/product/sleepy-pi-external-programming-adapter-console/) (not attached to a Pi though)
2. Plug in USB-C into the SleepyPi for power
3. Plug in Micro-USB into the programming board for the serial console and into the computer you're flashing from
4. Open up [sleepypi.ino](sleepypi.ino) in the [Arduino IDE](https://www.arduino.cc/en/software)
5. In the IDE, go under Tools -> Board, select "Arduino Fio"
6. In the IDE, go under Sketch -> Include Library -> Manage Libraries, and install all of the libraries specifically named in the comments at the top of the `sleepypi.ino` file you opened
7. In the IDE, under Tools, open "Serial Monitor"
8. In the IDE, on the opened `sleepypi.ino` file, first "Verify" (check mark icon), and assuming that succeeds, proceed to "Upload" (right arrow icon)
9. You should see JSON info coming in on the serial monitor and the board should start blinking
10. Pull USB cables, remove programming board, and deploy your freshly flashed SleepyPi
