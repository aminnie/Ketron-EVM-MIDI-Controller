# Ketron EVM-Button-Controller

MIDI Button Controller for Ketron EVM

Based on the Adafruit MacroPad RP2040: 
- Learning & instructions: https://learn.adafruit.com/adafruit-macropad-rp2040. 
- Adadfruit kit: https://www.adafruit.com/product/5128
- The Starter kit can also be purchased from vendors such as Digikey: https://www.digikey.com/en/products/detail/adafruit-industries-llc/5128/14635377
- Adafruit Midi Library: https://docs.circuitpython.org/projects/midi/en/latest/api.html#adafruit_midi.system_exclusive.SystemExclusive.from_bytes
- The Starter kit is an assemble only, and requires no soldering or electronics experience.

![image](https://github.com/user-attachments/assets/19278331-ac43-4239-b7ca-eed1cd57c6f6)

See Ketron website: https://shop.ketron.it/
- Ketron EVM Midi Implementation: https://shop.ketron.it/images/ketron/manualiPdf/EventX/EVENT%20SYSEX-NRPN.pdf

USB based MIDI Controller supports the most often used Arranger buttons via SysEx messages as an alternative to the hardware Pedal interface However, button assignmeents can be changed to by modifying the values in the key mappings table.

### Macropad Controller Button support:
- Intro/End 1
- Intro/End 2
- Intro/End 3
- To End
- Arr.A
- Arr.B
- Arr.C
- Arr.D
- Fill
- Break
- Start/End
- Variation
  
### Macropad Controller Encoder support:
Uses the Encoder switch to alternate between the following messages on encoder rotation.
- Tempo Up/Down
- Dial Up/Down
  
#### NOTE: 
- The Ketron EVM expects all attached devices to be powered before you start it up. It will not detect any devices on the USB or MIDI ports that is not on, or added after EVM startup. The Macropad only has one USB port that is used to connect to the EVM, and as a result of the start up connect requirement we have to power it via a USB hub with external power. This hub is an example of what works well:  Wenter 5 Ports USB 3.0 Hub (https://www.amazon.com/gp/product/B0BMFDLRSQ/ref=ewc_pr_img_1?smid=ATSSJE5RHO7GG&psc=1)
- Optional: If you would like the key illumoination to be less distracting, then turn the key lighting off in the code, or better, consider the Adafruit MX Black Keycaps witha window - https://www.adafruit.com/product/5112 


![image](https://github.com/user-attachments/assets/f973780d-daf9-4208-98ba-5f209fdb5782)




