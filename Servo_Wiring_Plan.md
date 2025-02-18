# Analog Servo Wiring Plan
## Power to Servo
* The servo will be powered by a 6V DC power supply.<br>
* The ground of the servo and the Raspberry Pi 5 will be connected to establish a common reference ground.
### Considerations 
* Make sure your 6V power supply can provide enough current (at least 1.5A - 2A) to handle the servo’s peak demand.
* DO NOT connect the 6V power directly to the Pi’s 3.3V or 5V pins, as this can damage the Pi.

## Servo to Pi (PWM Control)
* The servo’s PWM control wire will connect to GPIO 18, which is a hardware PWM-capable pin on the Raspberry Pi 5.

## Servo to MCP3008 (ADC)
* The servo’s feedback wire (0-3V analog output) will be connected to CH0 of the MCP3008.
* The Raspberry Pi will send a command via Din to select CH0 for reading.

## MCP3008 to Pi5 (SPI Communication & Powering the ADC)
### Powering the MCP3008
* VCC and VREF will be powered by 3.3V from the Raspberry Pi.
* AGND and DGND will be grounded to the Raspberry Pi.
### SPI Communication Pins (Pin/Purpose/PI5 Connection)
* CLK (Pin 13) - Clock Signal	- GPIO 11 "SPI SCLK" (SCLK, SPI Clock)
* CS/SHDN (Pin 10) - Chip Select (Enable ADC)	- GPIO 8 (SPI0_CE0) or any GPIO you manually control (Set to LOW)
* DIN (Pin 11) - Data Input (MOSI) - GPIO 10 "SPI MISO" (SPI0_MOSI, Pi → MCP3008) - This is how the Pi sends the channel selection command.
* DOUT (Pin 12)	- Data Output (MISO) - GPIO 9 "SPI MISO (SPI0_MISO, MCP3008 → Pi) - This is how the MCP3008 sends the ADC result to the Pi.

# **Final Corrected Wiring Overview**

| **Component**                      | **MCP3008 Pin**                 | **Raspberry Pi 5 Pin**               |
|------------------------------------|---------------------------------|----------------------------------|
| **Power (3.3V)**                   | VCC (Pin 16), VREF (Pin 15)     | 3.3V (Pi)                      |
| **Ground**                         | AGND (Pin 14), DGND (Pin 9)     | GND (Pi)                       |
| **Analog Input (Servo Feedback)**  | CH0 (Pin 1)                     | Servo Feedback Wire            |
| **Clock (SPI Clock Signal)**       | CLK (Pin 13)                     | GPIO 11 (SPI0_SCLK)            |
| **Chip Select (Enable MCP3008)**   | CS (Pin 10)                      | GPIO 8 (SPI0_CE0) or any GPIO   |
| **Data In (Pi → MCP3008 Command)** | DIN (Pin 11)                     | GPIO 10 (SPI0_MOSI)            |
| **Data Out (MCP3008 → Pi)**        | DOUT (Pin 12)                    | GPIO 9 (SPI0_MISO)             |

![MCP3008 Pinout]([https://your-image-url.com/image.png](https://www.google.com/imgres?q=mcp3008%20pinout&imgurl=https%3A%2F%2Ftigoe.github.io%2FPiRecipes%2Fadc-mcp-3xxx%2Fmcp-3xxx-pin-diagram.png&imgrefurl=https%3A%2F%2Ftigoe.github.io%2FPiRecipes%2Fadc-mcp-3xxx%2F&docid=27_Md3roPu5SzM&tbnid=82RNSlz7xE4nmM&vet=12ahUKEwilnfvw582LAxVgl-4BHdsTO04QM3oECBUQAA..i&w=486&h=396&hcb=2&ved=2ahUKEwilnfvw582LAxVgl-4BHdsTO04QM3oECBUQAA))


