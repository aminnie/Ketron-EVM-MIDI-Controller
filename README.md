# Ketron EVM-Button-Controller

MIDI Button Controller for Ketron EVM

Based on the Adafruit MacroPad RP2040: 
- Learning & instructions: https://learn.adafruit.com/adafruit-macropad-rp2040. 
- Adadfruit kit: https://www.adafruit.com/product/5128
- The Starter kit can also be purchased from vendors such as Digikey: https://www.digikey.com/en/products/detail/adafruit-industries-llc/5128/14635377
- Adafruit Midi Library: https://docs.circuitpython.org/projects/midi/en/latest/api.html#adafruit_midi.system_exclusive.SystemExclusive.from_bytes
- The Starter kit is an assemble only, and requires no soldering or electronics experience.

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
- Rotor Slow/Fast
  
### Macropad Controller Encoder support:
Uses the Encoder switch to alternate between the following messages on encoder rotation.
- Tempo Up/Down
- Dial Up/Down
  





