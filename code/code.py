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

# --- Support layout with USB Left or Right
# If USB faces left, reverse the key layout
key_map = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

usb_left = False

if usb_left is True:
    for index in range(12):
        key_map[index] = 11 - index


def keys(key):

    if key < 0 or key > 11:
        print(f"Invalid key map request: {key}")
        key = 0
    return key_map[key]


# --- Configure the MacroPad
print("Preparing MacroPad Display")

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

# Preparing Midi
print("Preparing Midi")

print(usb_midi.ports)
midi = adafruit_midi.MIDI(
    midi_in=usb_midi.ports[0], in_channel=0, midi_out=usb_midi.ports[1], out_channel=0
)

# Convert channel numbers at the presentation layer to the ones musicians use
print("Default output channel:", midi.out_channel + 1)
print("Listening on input channel:", midi.in_channel + 1)

# List of all the Midi Pedal Events with SysEx values supported by Ketron EVM
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
    "Fill4": 0x0A,
    "Break1": 0x0B,
    "Break2": 0x0C,
    "Break3": 0x0D,
    "Break4": 0x0E,
    "Intro/End1": 0x0F,
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
    "Live Bass": 0x1A,
    "Acc.BassToChord": 0x1B,
    "Manual Bass": 0x1C,
    "Voice Lock Bass": 0x1D,
    "Bass Mono/Poly": 0x1E,
    "Dial Down": 0x1F,
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
    "Low. Voice Lock": 0x2A,
    "Pianist": 0x2B,
    "Pianist Auto/Stand.": 0x2C,
    "Pianist Sustain": 0x2D,
    "Bassist": 0x2E,
    "Bassist Easy/Exp.": 0x2F,
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
    "Micro1 On/Off": 0x3A,
    "Micro1 Down": 0x3B,
    "Micro1 Up": 0x3C,
    "Voicetr.On/Off": 0x3D,
    "Voicetr.Down": 0x3E,
    "Voicetr.Up": 0x3F,
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
    "Pdf Scroll Down": 0x4A,
    "Pdf Scroll Up": 0x4B,
    "Glide Down": 0x4C,
    "Lead Mute": 0x4D,
    "Expr. Left/Style": 0x4E,
    "Arabic Reset": 0x4F,
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
    "Tom Off": 0x5A,
    "Latin1 Off": 0x5B,
    "Latin2 Off": 0x5C,
    "Latin3/Tamb Off": 0x5D,
    "Clap/fx Off": 0x5E,
    "Voice Down": 0x5F,
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
    "RegisVoice<<": 0x6A,
    "RegisVoice>>": 0x6B,
    "Text Page": 0x6E,
    "Text Page+": 0x6F,
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
    "Transp Down": 0x8A,
    "Transp Up": 0x8B,
    "Text Record": 0x8C,
    "Bass & Drum": 0x8D,
    "Pdf Clear": 0x8E,
    "Record": 0x90,
    "Play": 0x91,
    "DoubleDown": 0x92,
    "DoubleUp": 0x93,
    "Arr.Off": 0x94,
    "FILL & DRUM IN": 0x95,
    "Wah to Pedal": 0x96,
    "Overdrive to Pedal": 0x98,
    "Drum Mute": 0x99,
    "Bass Mute": 0x9A,
    "Chords Mute": 0x9B,
    "Real Chords Mute": 0x9C,
    "Voice2 to Pedal": 0x9D,
    "Micro Edit": 0x9E,
    "Micro2 Edit": 0x9F,
    "HALF BAR": 0xA0,
    "Bs Sust Pedal": 0xA1,
    "Scale": 0xA2,
    "End Swap": 0xA3,
    "Set Down": 0xA4,
    "Set Up": 0xA5,
    "FswChDelay": 0xA6,
    "IntroOnArr.": 0xA7,
    "EndingOnArr.": 0xA8,
    "Arr. Down": 0xA9,
    "Arr. Up": 0xAA,
    "Ending1": 0xAB,
    "Ending2": 0xAC,
    "Ending3": 0xAD,
    "Bass Lock": 0xAE,
    "Intro Loop": 0xB0,
    "Scene Down": 0xB1,
    "Scene Up": 0xB2,
    "STEM Scene A": 0xB3,
    "STEM Scene B": 0xB4,
    "STEM Scene C": 0xB5,
    "STEM Scene D": 0xB6,
    "STEM Solo": 0xB7,
    "STEM Autoplay": 0xB8,
    "STEM A On/Off": 0xB9,
    "STEM B On/Off": 0xBA,
    "STEM C On/Off": 0xBB,
    "STEM D On/Off": 0xBC,
    "STEM Lead On/Off": 0xBD,
    "Art. Toggle": 0xBE,
    "Key Tune On/Off": 0xBF,
    "Txt Clear": 0xC0,
    "Voicetr. Edit": 0xC1,
    "Clear Image": 0xC2,
    "Rotor Slow": 0xC3,
    "Rotor Fast": 0xC4,
}


# Controls the mapping of MacroPad keys to Ketron EVM functions
macropad_key_map = [
    "To End",
    "Arr.D",
    "Start/Stop",
    "Intro/End3",
    "Arr.C",
    "Break",
    "Intro/End2",
    "Arr.B",
    "Fill",
    "Intro/End1",
    "Arr.A",
    "Rotor Slow",
]
# Alternate list mapping is for toggled states such as rotor fast and slow
macropad_key_map_alt = ["", "", "", "", "", "", "", "", "", "", "", "Rotor Fast"]


# --- Helper function to compose and send SysEx messages
def send_sysex(midi_value):

    # Note the 1 and 2 byte Footswitch SysEx message formats with two bytes needed for values > 128
    manufacturer_id = bytearray([100])
    footswitch_sysex_data1 = bytearray([0x26, 0x79, 0x03, 0x0B, 0x7F])
    footswitch_sysex_data2 = bytearray([0x26, 0x79, 0x05, 0x01, 0x0A, 0x7F])

    if midi_value < 128:
        footswitch_sysex_data1[3] = midi_value
        footswitch_sysex_data1[4] = 0x7F
        sysex_message = SystemExclusive(manufacturer_id, footswitch_sysex_data1)
    else:
        footswitch_sysex_data2[3] = (midi_value >> 7) & 0x7F
        footswitch_sysex_data2[4] = midi_value & 0x7F
        footswitch_sysex_data2[5] = 0x7F
        sysex_message = SystemExclusive(manufacturer_id, footswitch_sysex_data2)

    midi.send(sysex_message)

    return True


# --- Prepare and send Volume or Dial Up/Down SysEx messages
encoder_position = macropad.encoder
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
    elif updown == -1:
        sign = "-" if encoder_sign else ""

        midi_value = key_midis["Tempo Down"]
        labels[3].text = "SysEx: Tempo Down" + sign
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
    elif updown == -1:
        sign = "-" if encoder_sign else ""

        midi_value = key_midis["Dial Down"]
        labels[3].text = "SysEx: Dial Down" + sign
    else:
        return
    send_sysex(midi_value)

    return True


# Use single key (11) to toggle Rotor between fast and slow
rotor_flag = False

# --- Lookup by index and find the corresponding MIDI value
def lookup_key_midi(key_id):
    global rotor_flag

    key_id = keys(key_id)

    # Lookup and toggle between fast and slow rotor
    if key_id == 11:
        if rotor_flag is True:
            mapped_key_id = macropad_key_map_alt[
                11
            ]  # Rotor fast first entry in alternate map
        else:
            mapped_key_id = macropad_key_map[key_id]
        rotor_flag = not rotor_flag
    # Continue to lookup all other keys
    else:
        mapped_key_id = macropad_key_map[key_id]
    # Get the corresponding MIDI SysEx value
    midi_value = key_midis[mapped_key_id]

    # print(f"Key at index {key_id}: {mapped_key_id}, MIDI value: {midi_value}")

    return mapped_key_id, midi_value


# --- Prepare and send SysEx message for key pressed
def process_key(key_id):

    key_id = keys(key_id)

    midi_key, midi_value = lookup_key_midi(key_id)
    send_sysex(midi_value)

    return midi_key


# Prepare Neopixels and preset colors to key functions
# Lit represents most recent press
lit_keys = [False] * 12
led_start_time = 0

def preset_pixels():
    for pixel in range(12):

        if pixel == keys(8):
            macropad.pixels[pixel] = 0x004000  # Set Intro/End 1-3 to Green
        elif pixel == keys(3) or pixel == keys(6) or pixel == keys(9):
            macropad.pixels[pixel] = 0x004000  # Set Break to Green
        elif pixel == keys(0) or pixel == keys(2):
            macropad.pixels[pixel] = 0x400000  # Set Start/Stop to Red
        elif pixel == keys(11):
            macropad.pixels[pixel] = 0x606010  # Set Rotor to Yellow
        elif pixel == keys(5):
            macropad.pixels[pixel] = 0xD02E04  # Set Break to Orange
        else:
            macropad.pixels[pixel] = 0x000040  # Set remaining Arr. A to D to Blue
        lit_keys[pixel] = False


# Initialize all pixels for various functions
preset_pixels()

# --- Start: Main processing loop
while True:

    # Read MacroPad Keys and send SysEx
    key_event = macropad.keys.events.get()

    if key_event:
        if key_event.pressed:
            lit_keys[keys(key_event.key_number)] = not lit_keys[
                keys(key_event.key_number)
            ]
            led_start_time = time.time()

            midi_key = process_key(keys(key_event.key_number))
            labels[3].text = "SysEx: " + midi_key

    # Send SysEx Tempo Up and Down SysEx messages
    if encoder_position != macropad.encoder:
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
            macropad.pixels[keys(pixel)] = 0x808080

    # Turn off LEDs after time period expire by resetting to inital state
    led_cur_time = time.time()
    if led_start_time != 0 and led_cur_time - led_start_time > 1:
        preset_pixels()

# --- End: Main processing loop
