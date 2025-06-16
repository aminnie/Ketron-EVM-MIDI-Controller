# Ketron EVM Button Controller

import board, displayio
import terminalio

from adafruit_display_text import bitmap_label as label
from adafruit_displayio_layout.layouts.grid_layout import GridLayout
from adafruit_macropad import MacroPad

import usb_midi
import adafruit_midi
from adafruit_midi.control_change import ControlChange
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.system_exclusive import SystemExclusive

import time

# Preparing Midi allowing for EVM to detect while it is starting up
print("Preparing Macropad Midi")

print(usb_midi.ports)
midi = adafruit_midi.MIDI(
    midi_in=usb_midi.ports[0], in_channel=0, midi_out=usb_midi.ports[1], out_channel=1
)

# Display Product and Build Date banner (20 chars)
#display_banner = "     Ketron EVM      "
display_banner = "   AJAMSONIC HS13    "
display_sub_banner = "Pedal/Tab Controller"

version = "06-16-2025"

# Timeout before reverting back Tempo to Rotor on Encoder  
tempo_timer = 60
volume_timer = 60

# Timout for key LED bright after press
key_bright_timer = 0.20

# --- Support layout with USB Left or Right
# If USB faces left, reverse the key layout
usb_left = True

key_map = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

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
    text=display_banner,
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

# Display version number and start up banner for 2 sec
labels[3].text = display_sub_banner
labels[6].text = "Version: " + version
time.sleep(1)


# Prepare MIDI Key to MIDI Lookups
print("Preparing EVM Midi Lookups")

# List of all the Midi Pedal Events with SysEx values supported by Ketron EVM
pedal_midis = {
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
    "Clear Image": 0xC2
}

tab_midis = {
    "DIAL_DOWN": 0x0,
    "DIAL_UP": 0x1,
    "PLAYER_A": 0x2,
    "PLAYER_B": 0x3,
    "ENTER": 0x4,
    "MENU": 0x6,
    "LYRIC": 0x7,
    "LEAD": 0x8,
    "VARIATION": 0x9,
    "DRAWBARS_VIEW": 0x0a,
    "DRAWBARS": 0x10,
    "DRUMSET": 0x11,
    "TALK": 0x12,
    "VOICETRON": 0x13,
    "STYLE_BOX": 0x14,
    "VOICE1": 0x19,
    "VOICE2": 0x1a,
    "USER_VOICE": 0x1b,
    "XFADE": 0x1c,
    "INTRO1": 0x1d,
    "INTRO2": 0x1e,
    "INTRO3": 0x1f,
    "BASSIST": 0x20,
    "DRUM_MIXER": 0x22,
    "OCTAVE_UP": 0x24,
    "OCTAVE_DOWN": 0x25,
    "USER_STYLE": 0x26,
    "DSP": 0x27,
    "ADSR_FILTER": 0x28,
    "MICRO": 0x29,
    "ARRA": 0x2c,
    "ARRB": 0x2d,
    "ARRC": 0x2e,
    "ARRD": 0x2f,
    "FILL": 0x30,
    "BREAK": 0x31,
    "JUKE_BOX": 0x32,
    "STEM": 0x33,
    "PIANIST": 0x34,
    "BASS_TO_LOWEST": 0x40,
    "MANUAL_BASS": 0x41,
    "PORTAMENTO": 0x48,
    "HARMONY": 0x49,
    "PAUSE": 0x4a,
    "TEMPO_SLOW": 0x4b,
    "TEMPO_FAST": 0x4c,
    "START_STOP": 0x4d,
    "TRANSP_DOWN": 0x59,
    "TRANSP_UP": 0x5a,
    "AFTERTOUCH": 0x5e,
    "EXIT": 0x5f,
    "ROTOR_SLOW": 0x60,
    "ROTOR_FAST": 0x61,
    "PIANO_FAM": 0x62,
    "ETHNIC_FAM": 0x63,
    "ORGAN_FAM": 0x64,
    "GUITAR_FAM": 0x65,
    "BASS_FAM": 0x66,
    "STRING_FAM": 0x67,
    "BRASS_FAM": 0x68,
    "SAX_FAM": 0x69,
    "HOLD": 0x6f,
    "PAD_FAM": 0x70,
    "SYNTH_FAM": 0x71,
    "FADEOUT": 0x73,
    "BASS_TO_ROOT": 0x74,
    "GM": 0x77,
}

# Controls the mapping of MacroPad keys to Ketron EVM functions
# Default Lookup table. Prefix 0 = pedal_midis, 1 = tab_midis
macropad_key_map = [
    "0:To End",
    "0:Arr.D",
    "0:Start/Stop",
    "0:Intro/End3",
    "0:Arr.C",
    "0:Break",
    "0:Intro/End2",
    "0:Arr.B",
    "0:Fill",
    "0:Intro/End1",
    "0:Arr.A",
    "1:VARIATION",
]

# Alternate list mapping is for toggled states such as rotor fast and slow
macropad_key_map_alt = ["", "", "", "", "", "", "", "", "", "", "", ""]

C_WHITE = 0x606060
C_BLUE = 0x000020
C_GREEN = 0x002000
C_RED = 0x200000
C_ORANGE = 0x701E02
C_PURPLE = 0x800080
C_YELLOW = 0X808000

# List mapping keyboard button/pixel colors
macropad_color_map = [C_BLUE, C_BLUE, C_GREEN, C_GREEN, C_BLUE, C_GREEN, C_ORANGE, C_BLUE, C_GREEN, C_RED, C_BLUE, C_RED]

# Read Macropad MIDI keys configuration from USB Drive
key_config_error = False

# Validate the MIDI value strings against the Pedal and Tab official list
def validate_midi_string(midi_string):

    if midi_string[0:1] == "0":
        for key, value in pedal_midis.items():        
            if key == midi_string[2:]:
                print(f"Pedal matched: {midi_string}")
                return True

    if midi_string[0:1] == "1":
        for key, value in tab_midis.items():        
            if key == midi_string[2:]:
                print(f"Tab matched: {midi_string}")
                return True
        
    return False


# Validate that only supported colors was specified
def validate_color_string(color_string):    
    color_code = C_WHITE
    
    if color_string.lower() == "red":
        color_code = C_RED
    elif color_string.lower() == "green":
        color_code = C_GREEN
    elif color_string.lower() == "blue":
        color_code = C_BLUE
    elif color_string.lower() == "purple":
        color_code = C_PURPLE
    elif color_string.lower() == "yellow":
        color_code = C_YELLOW
    elif color_string.lower() == "orange":
        color_code = C_ORANGE
    else:
        color_code = C_WHITE
            
    return color_code


# Read the config from CircuitPy USB drive and validate formatting
def usb_read_keys_config():
    global key_config_error

    try:
        with open("/keysconfig.txt", "r") as f:
            content_list = f.readlines()
            
            key_index = 0
            for item in content_list:
                # Ignore and skip comment lines
                if item[0:1] == "#":     
                    print(f"Skipping: {item}")
                    continue

                # Disassemble key spec'ed line into components
                # Item example: "key02=0:Start/Stop:red" for key, pedal|tab:midistring, color
                equal_offset = item.find('=', 0)                
                midi_string_offset = item.find(':', 0)
                color_offset = item.find(':', midi_string_offset+2)
                if equal_offset != 5 or midi_string_offset == -1 or color_offset == -1:
                    key_config_error = True
                    break                    
                
                if item[0:3] == "key":
                    midi_string = item[midi_string_offset - 1:color_offset]
                    
                    # Find content midi_string in Pedal and Tab lists 
                    if validate_midi_string(midi_string) == False:
                        print(f"Invalid midi_string {midi_string}")
                        labels[9].text = "Invalid: " + midi_string
                        
                        key_config_error = True
                        break
                    
                    macropad_key_map[key_index] = midi_string
                    #print(f"Macropad: {key_index} = {macropad_key_map[key_index]}")
                    
                    # Find and assign color in key spec item
                    color_string = item[color_offset + 1:-2]
                    macropad_color_map[keys(key_index)] = validate_color_string(color_string)
                    
                    key_index = key_index + 1
                else:
                    print(f"Mapping error on: {item}")
            #print(macropad_key_map)            
                    
    except OSError as e:
        labels[9].text = "Error: keysconfig.txt"
        print(f"Error reading file: {e}")
        return False

    return True

usb_read_keys_config()


# --- Configure the MacroPad
print("MacroPad Controller Ready")

# --- Helper functions to compose and send SysEx or Note messages

# Midi Connectivity Basic Check
def test_midi():
    outchan = 2

    labels[6].text = "Audible MIDI test! "

    for x in range(4):
        print(f"Sending note: {x}")

        midi.send(NoteOn("C4", 120))
        time.sleep(0.25)

        midi.send(NoteOff("C4", 0))
        time.sleep(0.25)

    labels[6].text = ""

    return True

# Send SysEx for Pedal or Tab commands

TAB = 0x00
PEDAL = 0x00
STATUS = 0x00

ON = 0x7F
OFF = 0x00

def send_pedal_sysex(midi_value):

    # The manufacturer ID for the Ketron EVENT EVM arranger module is 45342
    manufacturer_id = bytearray([0x26, 0x79])

    # Note the 1 and 2 byte Footswitch SysEx message formats with
    # two bytes needed for values > 128

    pedal_sysex_data1 = bytearray([0x03, PEDAL, STATUS])
    pedal_sysex_data2 = bytearray([0x05, PEDAL, PEDAL, STATUS])

    # Send ON followed by OFF Message
    if midi_value < 128:
        pedal_sysex_data1[1] = midi_value
        pedal_sysex_data1[2] = ON
        sysex_message = SystemExclusive(manufacturer_id, pedal_sysex_data1)

        midi.send(sysex_message)

        pedal_sysex_data1[2] = OFF
        sysex_message = SystemExclusive(manufacturer_id, pedal_sysex_data1)

        midi.send(sysex_message)

    else:
        pedal_sysex_data2[1] = (midi_value >> 7) & 0x7F
        pedal_sysex_data2[2] = midi_value & 0x7F
        pedal_sysex_data2[3] = ON
        sysex_message = SystemExclusive(manufacturer_id, pedal_sysex_data2)

        midi.send(sysex_message)

        pedal_sysex_data2[3] = OFF
        sysex_message = SystemExclusive(manufacturer_id, pedal_sysex_data2)

        midi.send(sysex_message)

    return True


# For Tab, set status to tab = 00h – 77h, and 00h for led off, 7Fh led on
def send_tab_sysex(midi_value):

    # The manufacturer ID for the Ketron EVENT EVM arranger module is 45342
    manufacturer_id = bytearray([0x26, 0x7C])

    tab_sysex_data = bytearray([TAB, STATUS])

    tab_sysex_data[0] = midi_value
    tab_sysex_data[1] = ON
    sysex_message = SystemExclusive(manufacturer_id, tab_sysex_data)

    midi.send(sysex_message)

    tab_sysex_data[1] = OFF
    sysex_message = SystemExclusive(manufacturer_id, tab_sysex_data)

    midi.send(sysex_message)

    return True


# Send Universal SysEx Master Volume Message - not supported by Ketron. 
# Using Expression CC11 until Master Volume confirmed.
# NOTE: EVM Midi Global Channel must be set to Channel 16 to process CC11!
# General SysEx: See https://www.recordingblogs.com/wiki/midi-master-volume-message

cur_volume = 100 # Master volume maximum
def send_volume(updown):
    global cur_volume
    global volume_start_time

    # CHange up and down in 16 notches
    if updown == -1:
        cur_volume = cur_volume - 8
        if cur_volume <= 0: 
            cur_volume = 0

    else:
        cur_volume = cur_volume + 8
        if cur_volume >= 127: 
            cur_volume = 127
 
    midi.send(ControlChange(11, cur_volume), channel=15)
    
    return True


# --- Prepare and send Tempo or Rotor Up/Down SysEx messages
encoder_position = macropad.encoder
encoder_mode = 0
encoder_sign = False
labels[6].text = "Encoder: Rotor"

tempo_start_time = 0

def process_tempo(updown):
    global encoder_sign
    global tempo_start_time

    encoder_sign = not encoder_sign

    if updown == 1:
        sign = "+" if encoder_sign else ""

        midi_value = pedal_midis["Tempo Up"]
        labels[3].text = "SysEx: Tempo Up" + sign
    elif updown == -1:
        sign = "-" if encoder_sign else ""

        midi_value = pedal_midis["Tempo Down"]
        labels[3].text = "SysEx: Tempo Down" + sign
    else:
        return False

    send_pedal_sysex(midi_value)

    # Tracking encoder ticks in order to revert to Rotor after 5 secs
    tempo_start_time = time.time()
    volume_start_time = time.time()

    return True


# --- Prepare and send Tab Dial Up/DownSysEx messages
def process_dial(updown):
    global encoder_sign

    encoder_sign = not encoder_sign

    if updown == 1:
        sign = "+" if encoder_sign else ""

        midi_value = tab_midis["DIAL_UP"]
        labels[3].text = "SysEx: Dial Up" + sign
    elif updown == -1:
        sign = "-" if encoder_sign else ""

        midi_value = tab_midis["DIAL_DOWN"]
        labels[3].text = "SysEx: Dial Down" + sign
    else:
        return False

    send_tab_sysex(midi_value)

    return True


# Use Encoder dial to toggle Rotor between Fast (clockwise = True)
# and Slow (counter-clockwise = False)
# rotor_flag: 0 = off, 1 = fast, -1 = slow
rotor_flag = 0

def process_rotor(updown):
    ROTOR_SLOW = -1
    ROTOR_OFF = 0
    ROTOR_FAST = 1

    global rotor_flag, encoder_sign

    encoder_sign = not encoder_sign

    # Single shot FAST or SLOW only and ignore multiple clicks in same direction
    if updown == 1 and rotor_flag != ROTOR_FAST:

        midi_value = tab_midis["ROTOR_FAST"]
        labels[3].text = "SysEx: Rotor Fast"

        rotor_flag = ROTOR_FAST

    elif updown == -1 and rotor_flag != ROTOR_SLOW:

        midi_value = tab_midis["ROTOR_SLOW"]
        labels[3].text = "SysEx: Rotor Slow"

        rotor_flag = ROTOR_SLOW

    else:
        return False

    send_tab_sysex(midi_value)

    return True


# Change the EVM Master Volume Up or Down
def process_mastervolume(updown):
        
    # Single shot FAST or SLOW only and ignore multiple clicks in same direction
    if updown == 1:
        labels[3].text = "CC11/16: E/Volume+"

    elif updown == -1:
        labels[3].text = "CC11/16: E/Volume-"

    else:
        return False

    send_volume(updown)

    return
    

# Toggle the encoder switch: Rotor = 0, Tempo = 1, Dial = 2
ENC_ROTOR = 0
ENC_TEMPO = 1
ENC_VOLUME = 2

enc_mode = ENC_ROTOR

def process_encoder(updown):
    
    if encoder_mode == ENC_ROTOR:
        process_rotor(updown)
    elif encoder_mode == ENC_TEMPO:
        process_tempo(updown)
    elif encoder_mode == ENC_VOLUME:
        process_mastervolume(updown)
    else:
        return False
    
    return True


# --- Lookup by index and find the corresponding MIDI value
def lookup_key_midi(key_id):
    global rotor_flag

    key_id = keys(key_id)
    mapped_key_id = macropad_key_map[key_id]

    # Extract out whether to use Pedal or Tab lookup and the Midi command
    if mapped_key_id[1:2] != ":" or mapped_key_id == "":
        print(f"Invalid key lookup value {mapped_key_id}")
        labels[6].text = "Invalid! " + mapped_key_id
        return 0, mapped_key_id, 0

    try:
        lookup_key = int(mapped_key_id[0:1])
    except ValueError:
        print(f"Lookup table str to int conversion failed: {mapped_key_id[0:1]}")
        labels[6].text = "Invalid! " + mapped_key_id
        return 0, mapped_key_id, 0

    mapped_key_id = mapped_key_id[2:]

    # Get the corresponding MIDI SysEx value
    if lookup_key == 0:
        midi_value = pedal_midis[mapped_key_id]
    else:
        midi_value = tab_midis[mapped_key_id]

    #print(f"Key at index {key_id}: {mapped_key_id}, table: {lookup_key}, MIDI value: {midi_value}")

    return lookup_key, mapped_key_id, midi_value


# --- Prepare and send SysEx message for key pressed
def process_key(key_id):
    key_id = keys(key_id)

    lookup_key, midi_key, midi_value = lookup_key_midi(key_id)

    if lookup_key == 0:
        send_pedal_sysex(midi_value)
    else:
        send_tab_sysex(midi_value)

    return midi_key


# Prepare Neopixels and preset colors to key functions based on keyboard orientation (USB left/right_
lit_keys = [False] * 12
led_start_time = 0

def preset_pixels():
    global enc_mode
    global key_config_error
    
    # Step through and light each pixel
    for pixel in range(12):
        
        # Flag invalid key configuration file
        if key_config_error == True:
            macropad.pixels[pixel] = C_RED

        elif pixel == keys(11):                  # Set Variation
            if encoder_mode == ENC_TEMPO:
                macropad.pixels[pixel] = C_YELLOW
            elif encoder_mode == ENC_VOLUME:
                macropad.pixels[pixel] = C_PURPLE
            else:
                macropad.pixels[pixel] = macropad_color_map[pixel] # C_BLUE, Set Variation
        elif pixel == keys(8):
            macropad.pixels[pixel] = macropad_color_map[pixel] # C_GREEN, Set Fill
        elif pixel == keys(0) or pixel == keys(2):
            macropad.pixels[pixel] = macropad_color_map[pixel] # C_RED, Set Start/Stop and To End
        elif pixel == keys(5):
            macropad.pixels[pixel] = macropad_color_map[pixel] # C_ORANGE, Set Break
        elif pixel == keys(3) or pixel == keys(6) or pixel == keys(9):
            macropad.pixels[pixel] = macropad_color_map[pixel] # C_GREEN, Set Set Intro/End 1 to 3
        else:
            macropad.pixels[pixel] = macropad_color_map[pixel] # C_BLUE. Set Arr. A to D

        lit_keys[pixel] = False

    return


# Initialize all pixels for various functions on  startup
preset_pixels()

# --- Start: Main processing loop
while True:

    # Read MacroPad Keys and send SysEx
    key_event = macropad.keys.events.get()

    if key_event:
        if key_event.pressed:

            midi_key = process_key(keys(key_event.key_number))
            labels[3].text = "SysEx: " + midi_key

            # If Start/Step, set encoder to TEMPO mode
            if midi_key == "Start/Stop":
                encoder_mode = ENC_TEMPO
                tempo_start_time = time.time()
                labels[3].text = "SysEx: -"
                labels[6].text = "Encoder: *Tempo*"

            # Clear any recently pressed keys
            preset_pixels()

            lit_keys[keys(key_event.key_number)] = not lit_keys[
                keys(key_event.key_number)]

            led_start_time = time.time()

    # Send SysEx Tempo Up and Down SysEx messages
    if encoder_position != macropad.encoder:
        if encoder_position < macropad.encoder:
            process_encoder(+1)
        else:
            process_encoder(-1)

        encoder_position = macropad.encoder

    # Use the Encoder switch to changed between Rotor(0), Tempo(1) and Volume(2)
    # Track Tempo start time in order to revert to Rotor after 15 secs
    macropad.encoder_switch_debounced.update()
    if macropad.encoder_switch_debounced.pressed:
        encoder_mode = encoder_mode + 1
        if encoder_mode > ENC_VOLUME: encoder_mode = ENC_ROTOR

        if encoder_mode == ENC_ROTOR:
            labels[3].text = "SysEx: -"
            labels[6].text = "Encoder: Rotor"
        elif encoder_mode == ENC_TEMPO:
            labels[3].text = "SysEx: -"
            labels[6].text = "Encoder: *Tempo"
            tempo_start_time = time.time()
        elif encoder_mode == ENC_VOLUME:
            labels[3].text = "CC11/16: -"
            labels[6].text = "Encoder: *Volume"
            volume_start_time = time.time()
        else:
            labels[3].text = ""
            labels[6].text = "Encoder: Invalid!"
        
        # Set pixel 11 color to encoder mode
        preset_pixels()

    # Revert Tempo encoder back to Rotor after x secs of no encode change
    if encoder_mode == ENC_TEMPO:
        tempo_cur_time = time.time()
        
        if tempo_start_time != 0 and tempo_cur_time - tempo_start_time > tempo_timer:
            encoder_mode = ENC_ROTOR
            labels[3].text = "SysEx: -"
            labels[6].text = "Encoder: Rotor"

    # Revert Volume encoder back to Rotor after x secs of no encode change
    if encoder_mode == ENC_VOLUME:
        volume_cur_time = time.time()
        
        if volume_start_time != 0 and volume_cur_time - volume_start_time > volume_timer:
            encoder_mode = ENC_ROTOR
            labels[3].text = "SysEx: -"
            labels[6].text = "Encoder: Rotor"

    # Update MacroPad pixels based on latest status
    for pixel in range(12):
        if lit_keys[pixel]:
            macropad.pixels[keys(pixel)] = C_WHITE

    # Turn off LEDs after time period expire by resetting to inital state
    led_cur_time = time.time()
    if led_start_time != 0 and led_cur_time - led_start_time > key_bright_timer:
        preset_pixels()

# --- End: Main processing loop
