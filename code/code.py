# Ketron EVM Button Controller

import time

import displayio
import terminalio
from adafruit_display_text import bitmap_label as label
from adafruit_displayio_layout.layouts.grid_layout import GridLayout
from adafruit_macropad import MacroPad

import usb_midi
import adafruit_midi
from adafruit_midi.system_exclusive import SystemExclusive

print("Preparing MacroPad")

macropad = MacroPad(rotation=0)

main_group = displayio.Group()
macropad.display.root_group = main_group

title = label.Label(
    y=6,
    font=terminalio.FONT,
    color=0x0,
    text="     Ketron EVM     ",
    background_color=0xFFFFFF,
)

# Configure Display Grid
layout = GridLayout(x=0, y=8, width=128, height=54, grid_size=(3, 4), cell_padding=5)

labels = []
for _ in range(12):
    labels.append(label.Label(terminalio.FONT, text=""))

for index in range(12):
    x = index % 3
    y = index // 3
    layout.add_content(labels[index], grid_position=(x, y), cell_size=(1, 1))

main_group.append(title)
main_group.append(layout)

print(f"Encode position: {macropad.encoder}")
encoder_position = macropad.encoder

# Preparing Midi
print("Preparing Midi")

print(usb_midi.ports)
midi = adafruit_midi.MIDI(
    midi_in=usb_midi.ports[0], in_channel=0, midi_out=usb_midi.ports[1], out_channel=0
)

# Convert channel numbers at the presentation layer to the ones musicians use
print("Default output channel:", midi.out_channel + 1)
print("Listening on input channel:", midi.in_channel + 1)

# List of all the Midi Pedal Events supported by Ketron EVM
key_midis = {
    "Sustain": 0x00,
    "Soft": 0x01,
    "Sostenuto": 0x02,
    "Arr.A": 0x03,
    "Arr.B": 0x04,
    "Arr.C": 0x05,
    "Arr.D": 0x06,
    "Fill1": 0x07,
    "Fill2": 0x08,
    "Fill3": 0x09,
    "Fill4": 0x0a,
    "Break1": 0x0b,
    "Break2": 0x0c,
    "Break3": 0x0d,
    "Break4": 0x0e,
    "Intro/End1": 0x0f,
    "Intro/End2": 0x10,
    "Intro/End3": 0x11,
    "Start/Stop": 0x12,
    "Tempo Up": 0x13,
    "Tempo Down": 0x14,
    "Fill": 0x15,
    "Break": 0x16,
    "To End": 0x17,
    "Bass to Lowest": 0x18,
    "Bass to Root": 0x19,
    "Live Bass": 0x1a,
    "Acc.BassToChord": 0x1b,
    "Manual Bass": 0x1c,
    "Voice Lock Bass": 0x1d,
    "Bass Mono/Poly": 0x1e,
    "Dial Down": 0x1f,
    "Dial Up": 0x20,
    "Auto Fill": 0x21,
    "Fill to Arr.": 0x22,
    "After Fill": 0x23,
    "Low. Hold Start": 0x24,
    "Low. Hold Stop": 0x25,
    "Low. Hold Break": 0x26,
    "Low. Stop Mute": 0x27,
    "Low. Mute": 0x28,
    "Low. and Bass": 0x29,
    "Low. Voice Lock": 0x2a,
    "Pianist": 0x2b,
    "Pianist Auto/Stand.": 0x2c,
    "Pianist Sustain": 0x2d,
    "Bassist": 0x2e,
    "Bassist Easy/Exp.": 0x2f,
    "Key Start": 0x30,
    "Key Stop": 0x31,
    "Enter": 0x32,
    "Exit": 0x33,
    "Registration": 0x34,
    "Fade": 0x35,
    "Harmony": 0x36,
    "Octave Up": 0x37,
    "Octave Down": 0x38,
    "RestartCount In": 0x39,
    "Micro1 On/Off": 0x3a,
    "Micro1 Down": 0x3b,
    "Micro1 Up": 0x3c,
    "Voicetr.On/Off": 0x3d,
    "Voicetr.Down": 0x3e,
    "Voicetr.Up": 0x3f,
    "Micro2 On/Off": 0x40,
    "EFX1 On/Off": 0x41,
    "EFX2 On/Off": 0x42,
    "Arabic.Set1": 0x43,
    "Arabic.Set2": 0x44,
    "Arabic.Set3": 0x45,
    "Arabic.Set4": 0x46,
    "Dry On Stop": 0x47,
    "Pdf Page Down": 0x48,
    "Pdf Page Up": 0x49,
    "Pdf Scroll Down": 0x4a,
    "Pdf Scroll Up": 0x4b,
    "Glide Down": 0x4c,
    "Lead Mute": 0x4d,
    "Expr. Left/Style": 0x4e,
    "Arabic Reset": 0x4f,
    "Hold": 0x50,
    "2nd On/Off": 0x51,
    "Pause": 0x52,
    "Talk On/Off": 0x53,
    "Manual Drum": 0x54,
    "Kick Off": 0x55,
    "Snare Off": 0x56,
    "Rimshot Off": 0x57,
    "Hit-Hat Off": 0x58,
    "Cymbal Off": 0x59,
    "Tom Off": 0x5a,
    "Latin1 Off": 0x5b,
    "Latin2 Off": 0x5c,
    "Latin3/Tamb Off": 0x5d,
    "Clap/fx Off": 0x5e,
    "Voice Down": 0x5f,
    "Voice Up": 0x60,
    "Regis Down": 0x61,
    "Regis Up": 0x62,
    "Style Voice Down": 0x63,
    "Style Voice Up": 0x64,
    "EFX1 Preset Down": 0x65,
    "EFX1 Preset Up": 0x66,
    "Multi": 0x67,
    "Page<<": 0x68,
    "Page>>": 0x69,
    "RegisVoice<<": 0x6a,
    "RegisVoice>>": 0x6b,
    "Text Page": 0x6e,
    "Text Page+": 0x6f,
    "Style Voice 1": 0x70,
    "Style Voice 2": 0x71,
    "Style Voice 3": 0x72,
    "Style Voice 4": 0x73,
    "VIEW & MODELING": 0x74,
    "Lock Bass": 0x75,
    "LockChord": 0x76,
    "Lyrics": 0x77,
    "VoiceToABCD": 0x87,
    "TAP": 0x88,
    "Autocrash": 0x89,
    "Transp Down": 0x8a,
    "Transp Up": 0x8b,
    "Text Record": 0x8c,
    "Bass & Drum": 0x8d,
    "Pdf Clear": 0x8e,
    "Record": 0x90,
    "Play": 0x91,
    "DoubleDown": 0x92,
    "DoubleUp": 0x93,
    "Arr.Off": 0x94,
    "FILL & DRUM IN": 0x95,
    "Wah to Pedal": 0x96,
    "Overdrive to Pedal": 0x98,
    "Drum Mute": 0x99,
    "Bass Mute": 0x9a,
    "Chords Mute": 0x9b,
    "Real Chords Mute": 0x9c,
    "Voice2 to Pedal": 0x9d,
    "Micro Edit": 0x9e,
    "Micro2 Edit": 0x9f,
    "HALF BAR": 0xa0,
    "Bs Sust Pedal": 0xa1,
    "Scale": 0xa2,
    "End Swap": 0xa3,
    "Set Down": 0xa4,
    "Set Up": 0xa5,
    "FswChDelay": 0xa6,
    "IntroOnArr.": 0xa7,
    "EndingOnArr.": 0xa8,
    "Arr. Down": 0xa9,
    "Arr. Up": 0xaa,
    "Ending1": 0xab,
    "Ending2": 0xac,
    "Ending3": 0xad,
    "Bass Lock": 0xae,
    "Intro Loop": 0xb0,
    "Scene Down": 0xb1,
    "Scene Up": 0xb2,
    "STEM Scene A": 0xb3,
    "STEM Scene B": 0xb4,
    "STEM Scene C": 0xb5,
    "STEM Scene D": 0xb6,
    "STEM Solo": 0xb7,
    "STEM Autoplay": 0xb8,
    "STEM A On/Off": 0xb9,
    "STEM B On/Off": 0xba,
    "STEM C On/Off": 0xbb,
    "STEM D On/Off": 0xbc,
    "STEM Lead On/Off": 0xbd,
    "Art. Toggle": 0xbe,
    "Key Tune On/Off": 0xbf,
    "Txt Clear": 0xc0,
    "Voicetr. Edit": 0xc1,
    "Clear Image": 0xc2,
    "Rotor Slow": 0xc3,
    "Rotor Fast": 0xc4
}


# Controls the mapping of MacroPad keys to Ketron EVM functions
macropad_key_map = ["To End", "Arr.D", "Start/Stop", "Intro/End3", "Arr.C", "Break", "Intro/End2", "Arr.B", "Fill", "Intro/End1", "Arr.A", "Rotor Slow", "Rotor Fast"]


# --- Helper function to send SysEx messages
def send_sysex(midi_value):

    # Note the 1 and 2 byte Sysex message formats with two bytes needed for values > 128
    manufacturer_id = bytearray([100])
    sysex_data1 = bytearray([0x26, 0x79, 0x03, 0x0B, 0x7F])
    sysex_data2 = bytearray([0x26, 0x79, 0x05, 0x01, 0x0A, 0x7F])

    if midi_value < 128:
        sysex_data1[3] = midi_value
        sysex_data1[4] = 0x7F
        sysex_message = SystemExclusive(manufacturer_id, sysex_data1)
    else:
        sysex_data2[3] = (midi_value >> 7) & 0x7F
        sysex_data2[4] = midi_value & 0x7F
        sysex_data2[5] = 0x7F
        sysex_message = SystemExclusive(manufacturer_id, sysex_data2)

    midi.send(sysex_message)

    return True


# Use single key (11) to toggle Rotor between fast and slow
rotor_flag = True

def toggle_rotor(key_id):
    global rotor_flag

    if rotor_flag is True:
        key_id = key_id + 1

    rotor_flag = not rotor_flag
    return key_id

# --- Lookup by index and fine the corresponding MIDI value
def lookup_key_midi(key_id):

    # Toggle between fast and slow rotor
    if key_id == 11:
        key_id = toggle_rotor(key_id)

    mapped_key_id = macropad_key_map[key_id]
    midi_value = key_midis[mapped_key_id]

    print(f"Key at index {key_id}: {mapped_key_id}, MIDI value: {midi_value}")

    return mapped_key_id, midi_value


# --- Prepare and send Volume or Dial Up/Down SysEx messages
encoder_mode = False
encoder_sign = False

def process_encoder(updown):

    if encoder_mode:
        process_dial(updown)
    else:
        process_tempo(updown)

def process_tempo(updown):
    global encoder_sign
    
    encoder_sign = not encoder_sign

    if updown == 1:
        sign = "+" if encoder_sign else ""

        midi_value = key_midis["Tempo Up"]
        labels[3].text = "SysEx: Tempo Up" + sign
        print(f"Tempo Up value: {updown}")
    elif updown == -1:
        sign = "-" if encoder_sign else ""

        midi_value = key_midis["Tempo Down"]
        labels[3].text = "SysEx: Tempo Down" + sign
        print(f"Tempo Down value: {updown}")
    else:
        return

    send_sysex(midi_value)

    return True

def process_dial(updown):
    global encoder_sign

    encoder_sign = not encoder_sign

    if updown == 1:
        sign = "+" if encoder_sign else ""

        midi_value = key_midis["Dial Up"]
        labels[3].text = "SysEx: Dial Up" + sign
        print(f"Dial Up value: {updown}")
    elif updown == -1:
        sign = "-" if encoder_sign else ""

        midi_value = key_midis["Dial Down"]
        labels[3].text = "SysEx: Dial Down" + sign
        print(f"Dial Down value: {updown}")
    else:
        return

    send_sysex(midi_value)

    return True


# --- Prepare and send SysEx message for key pressed
def process_key(key_id):

    midi_key, midi_value = lookup_key_midi(key_id)
    send_sysex(midi_value)

    return midi_key

# Prepare Neopixels
lit_keys = [False] * 12
led_start_time = 0

def preset_pixels():
    for pixel in range(12):

        if pixel == 8:
            macropad.pixels[pixel] = 0x004000 # Set to Green
        elif pixel == 3 or pixel == 6 or pixel == 9:
            macropad.pixels[pixel] = 0x004000 # Set to Green
        elif pixel == 0 or pixel == 2:
            macropad.pixels[pixel] = 0x400000 # Set to Red
        elif pixel == 11:
            macropad.pixels[pixel] = 0x606010 # Set to Yellow
        elif pixel == 5:
            macropad.pixels[pixel] = 0xd02e04 # Set to Orange
        else:
            macropad.pixels[pixel] = 0x000040 # Set remaining to Blue
        lit_keys[pixel] = False

# Preset all the pixels for various functions
preset_pixels()

# --- Start: Main processing loop
while True:

    # Read MacroPad Keys and send SysEx
    key_event = macropad.keys.events.get()
    if key_event:
        if key_event.pressed:
            lit_keys[key_event.key_number] = not lit_keys[key_event.key_number]
            led_start_time = time.time()

            midi_key = process_key(key_event.key_number)
            labels[3].text = "SysEx: " + midi_key

    # Send SysEx Tempo Up and Down SysEx messages
    if encoder_position != macropad.encoder:
        print(f"Changed Encoder position = {macropad.encoder}")

        if encoder_position < macropad.encoder:
            process_encoder(+1)
        else:
            process_encoder(-1)

        encoder_position = macropad.encoder

    # Use the Encoder switch to alternate between Tempo and Dial Up/Down
    if macropad.encoder_switch:
        encoder_mode = not encoder_mode

    # Update MacroPad pixes based on latest status
    for pixel in range(12):
        if lit_keys[pixel]:
            macropad.pixels[pixel] = 0x808080
        else:
            # Turn off LEDs after time period expire
            led_cur_time = time.time()
            if led_start_time != 0 and led_cur_time - led_start_time > 2:
                preset_pixels()

 # --- End: Main processing loop

