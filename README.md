# Ketron EVM-Button-Controller

MIDI Button Controller for Ketron EVM Sound Module is based on the Adafruit MacroPad RP2040: 
- Adadfruit kit: https://www.adafruit.com/product/5128
- Learning more about the Macropad, assembly instructions, and how to download custom code into the device: https://learn.adafruit.com/adafruit-macropad-rp2040. 
- The Starter kit can also be purchased from vendors such as Digikey: https://www.digikey.com/en/products/detail/adafruit-industries-llc/5128/14635377
- Adafruit Midi Library: https://docs.circuitpython.org/projects/midi/en/latest/api.html#adafruit_midi.system_exclusive.SystemExclusive.from_bytes
- The Starter kit is an assemble only, and requires no soldering or electronics experience.

Adafruit Macropad RP2040:

![image](https://github.com/user-attachments/assets/6fd9b969-9b77-4c2a-81fc-0f7a34129f4d)

### Macropad Controller Button support:

The USB based MIDI Controller supports the most often used Arranger buttons via SysEx messages as an alternative to the hardware Pedal interface. Button assignmeents can be changed by modifying the values in the key mappings table.

The controller is currently programmed with the following EVM SysEx messages:
- Intro/End 1
- Intro/End 2
- Intro/End 3
- To End
- Arr.A
- Arr.B
- Arr.C
- Arr.D
- Variation
- Fill
- Break
- Start/End

### Macropad Controller Encoder support:
Uses the Encoder switch to alternate between the following messages on encoder rotation.
- Tempo Up/Down
- Rotor Fast/Slow

See Ketron website for more details about the EVM: https://shop.ketron.it/
- Ketron EVM Midi Implementation: https://shop.ketron.it/images/ketron/manualiPdf/EventX/EVENT%20SYSEX-NRPN.pdf

Please see the source code for additional EVM functionalities and SysEx options that can be loaded to Macropad buttons.

### Loading the customized EVM Controller code into the Macropad:
See the Adafruit learning website for detailed instructors on how to
-  Prepare the board for our custom solution in the code.py file in the code directory for this repository.
-  Download the Mu Editor to your PC. Mu will be used to connect to the board and download the code.py file into it.

### Testing the EVM Macropad Controller:
Before connecting to the EVM moodule, you may want to download and install MidiView (https://hautetechnique.com/midi/midiview/). Midi is useful to inspect and validate the output from any MIDI controller. In this case you should see the controller output the SysEx messages associated with keys or the rotary encoder.
  
### Connecting the EVM Macropad Controller to your EVM Module: 
- The Ketron EVM expects all attached devices to be powered before you start it up. It will not detect any devices on the USB or MIDI ports that is not switched on, or added after EVM startup.
- The Macropad only has one USB port that is used to connect to the EVM, and as a result of the startup connect requirement we have to power it via a USB hub with external power. This hub is an example of what works:  Wenter 5 Ports USB 3.0 Hub (https://www.amazon.com/gp/product/B0BMFDLRSQ/ref=ewc_pr_img_1?smid=ATSSJE5RHO7GG&psc=1)

### Customizing the EVM Cntroller button SysEx messages:
This requires you to lookup the exact text the required message from the either the Tabs or Pedal lookup tables and copy it onto one of the keys in the Macropad configuration lookup table. See code.py for the current configuration and how to trace entries back into the lookup tables.

#### Optional:
- If you find the key illumoination distracting, you may want to turn the key lighting down or off in the code, or consider the Adafruit MX Black Keycaps with a clear window slot - https://www.adafruit.com/product/5112
- You could also consider a 3D printed case for the Macropad: https://www.printables.com/model/138045-adafruit-macropad-case or https://www.thingiverse.com/thing:4922256/makes

My setup with the Roland AT900C, Ketron EVM, iPad EVM Controller, and the Macropad:

![image](https://github.com/user-attachments/assets/b157a384-70e0-4774-a011-49b8d7b529fb)

![evmcontroller](https://github.com/user-attachments/assets/49323e5a-62fe-4b38-81b6-59a04b765fe2)

For more information or support, please email a_minnie@hotmail.com



