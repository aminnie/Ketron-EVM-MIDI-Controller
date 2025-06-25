# Ketron EVM-Button-Controller

This MIDI Button Controller for Ketron EVM Sound Module is based on the Adafruit MacroPad RP2040: 
- Adadfruit kit: https://www.adafruit.com/product/5128
- Learning more about the Macropad, assembly instructions, and how to download custom code into the device: https://learn.adafruit.com/adafruit-macropad-rp2040. 
- The Starter kit can also be purchased from vendors such as Digikey: https://www.digikey.com/en/products/detail/adafruit-industries-llc/5128/14635377
- Adafruit Midi Library: https://docs.circuitpython.org/projects/midi/en/latest/api.html#adafruit_midi.system_exclusive.SystemExclusive.from_bytes
- The Starter kit is an assemble only, and requires no soldering or electronics experience.

Adafruit Macropad RP2040:

![image](https://github.com/user-attachments/assets/6fd9b969-9b77-4c2a-81fc-0f7a34129f4d)

Why use Macropad RP2040 to control the Ketron: The Macropad has plain old PC USB HID keyboard drivers - just like the countless cheap keypads you fill find on Amazon. However, none of these cheap devices and even some dedicated MIDI controllers support sending SysEx messages and or customization. Ketron exposes a hardware MIDI pedal interface on the EVM, but also has generously provided a MIDI over USB implmenetation. This controller is coded to send MIDI CC and SysEX messages using the Adafruit Circuit Python library.

### Macropad Controller Button support:

The USB based MIDI Controller supports the most often used Arranger buttons via SysEx messages as an alternative to the hardware Pedal interface. Button assignmeents can be changed by modifying the values in the key mappings table.

The controller is currently configured to the following EVM SysEx messages:

Row 1:
- Intro/End 1 (green)
- Intro/End 2 (green)
- Intro/End 3 (green)
- To End (red)

Row 2:
- Arr.A (blue)
- Arr.B (blue)
- Arr.C (blue)
- Arr.D (blue)

Row 3:
- Variation (blue)
- Fill (green)
- Break (orange)
- Start/End (red)

### Macropad Controller Encoder support:
Uses the Encoder switch to alternate between the following messages on encoder rotation.
- Tempo Up/Down
- Rotor Fast/Slow
- Volume Up/DOwn

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
- The Ketron EVM expects all attached devices to be powered up before you start it up. It will not detect any devices on the USB or MIDI ports that is not switched on, or added after EVM startup.
- The Macropad only has one USB port that is used to connect to the EVM, and as a result of the startup connect requirement we have to power it via a USB hub with external power. This hub is an example of what works:  Wenter 5 Ports USB 3.0 Hub (https://www.amazon.com/gp/product/B0BMFDLRSQ/ref=ewc_pr_img_1?smid=ATSSJE5RHO7GG&psc=1)

### Customizing the EVM Cntroller button SysEx messages:
Keys are configured by updating the provided keysconfig.txt file. Tt requires you to lookup the exact text for the required SysEWx MIDI message from either the Tabs (pedal_midis) or Pedal (tab_midis) lookup tables in the Ketron MIDI documentation, and copy it onto one of the keys of the keys. See the config file for the current configuration. Please be careful with the configuration. It is validating and if an error is enountered during startup, all keys will turn red. The unit continues to function though based on the coded defaults. 
Note: The rotary encoder SysEx output for is fixed to tempo up/down,  rotary fast/slow or volume up/down on successive encoder button presses. It is note configurable at the moment.

#### Extra:
- Please let me know you need a 3D case for your solution
  - The 3D case .scad and .stl files are available in the case directory if you would like to print it yourself. Please note that it consists of three files: The main case, the top cover, and loose fitting filler that goes in between the PCB and the top cover to keep thetop cover flush with the case top.
  - I switched to using low profile key switches and caps you see in the picture. It feels and looks much better. Contact me if I can help.
  - If you are going to print a case and use low profile key switches, then I would recommend you buy the Adafruit Macropad bare bones board only.
  - If you have a need to tinker with the code, and try qwiic add-ons, then print the dev 3D case which has a larger slot that accepts a qwiic connector.

My setup with the Roland AT900C, Ketron EVM, iPad EVM Controller, and the original Macropad:

![image](https://github.com/user-attachments/assets/b157a384-70e0-4774-a011-49b8d7b529fb)

The latest version of the Macropad controller:

![EVMPad](resources/AMEVMPad.jpg)

For more information, support, or a completed unit please email me at a_minnie@hotmail.com.



