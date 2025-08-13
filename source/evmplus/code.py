# Ketron EVM Plus Button Controller with Quad Encoder

import board, displayio, digitalio
import terminalio
import time

from adafruit_display_text import bitmap_label as label
from adafruit_displayio_layout.layouts.grid_layout import GridLayout
from adafruit_macropad import MacroPad

import usb_midi
import adafruit_midi
from adafruit_midi.control_change import ControlChange
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.system_exclusive import SystemExclusive

from rainbowio import colorwheel

import adafruit_seesaw.digitalio
import adafruit_seesaw.neopixel
import adafruit_seesaw.rotaryio
import adafruit_seesaw.seesaw

# Enable or disable test tune on startup
TEST_CONNECT = False

# --- Constants and Enums ---
class EncoderMode:
    ROTOR = 0
    TEMPO = 1
    VOLUME = 2
    VALUE = 3

class MIDIType:
    PEDAL = 0
    TAB = 1

class MIDIStatus:
    OFF = 0x00
    ON = 0x7F

class EFXLevel:
    Voice1 = 0x07
    Voice2 = 0x3D
    RealChord = 0x08
    LeftGM = 0x3F

class Colors:
    WHITE = 0x606060
    BLUE = 0x000020
    GREEN = 0x002000
    RED = 0x200000
    ORANGE = 0x701E02
    PURPLE = 0x800080
    YELLOW = 0x808000

# Color mapping dictionary
COLOR_MAP = {
    'red': Colors.RED,
    'green': Colors.GREEN,
    'blue': Colors.BLUE,
    'purple': Colors.PURPLE,
    'yellow': Colors.YELLOW,
    'orange': Colors.ORANGE,
    'white': Colors.WHITE
}

# Key used to reflect timed Eccoder mode changes on LED
VARIATION_KEY = 0

# --- Configuration Class ---
class EVMConfig:
    def __init__(self):
        self.display_banner =     "     Ketron EVM      "
        self.display_sub_banner = "Arranger Controller "
        self.version = "1.1"
        #self.display_banner =     "    AJAMSONIC HS13   "
        #self.display_sub_banner = "Pad Controller   "
        #self.version = "5.1"

        # USB port on the left side of the MacroPad
        self.usb_left = True

        # Timers for tempo, volume, and key brightness
        self.tempo_timer = 60
        self.volume_timer = 60
        self.value_timer = 60
        self.version_timer = 15
        self.key_bright_timer = 0.20

        # Quad encoder variables
        self.quad_encoders = []
        self.quad_switches = []
        self.quad_pixels = []

        # Initialize MacroPad key mappings
        self.key_map = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        if not self.usb_left:
            self.key_map = [11 - i for i in range(12)]

    def get_key(self, key):
        """Safe key mapping with bounds checking"""
        
        if key < 0 or key > 11:
            print("Invalid key map request: {}".format(key))
            return 0
        return self.key_map[key]

# --- MIDI Handler Class ---
class MIDIHandler:
    def __init__(self, midi_instance):
        self.midi = midi_instance
        self.manufacturer_id_pedal = bytearray([0x26, 0x79])
        self.manufacturer_id_tab = bytearray([0x26, 0x7C])
        self.manufacturer_id_efx = bytearray([0x26, 0x7B])

        # Pre-allocate bytearrays for memory efficiency
        self.pedal_sysex_1 = bytearray([0x03, 0x00, 0x00])
        self.pedal_sysex_2 = bytearray([0x05, 0x00, 0x00, 0x00])
        self.tab_sysex = bytearray([0x00, 0x00])

        # EFX Level/Volume
        self.efx_level_sysex = bytearray([0x00, 0x05, 0x00])

        self.cur_volume = 100

    def send_pedal_sysex(self, midi_value):
        """Send SysEx for Pedal commands"""
        
        try:
            # Send ON followed by OFF Message
            if midi_value < 128:
                self.pedal_sysex_1[1] = midi_value
                self.pedal_sysex_1[2] = MIDIStatus.ON
                sysex_message = SystemExclusive(self.manufacturer_id_pedal, self.pedal_sysex_1)
                self.midi.send(sysex_message)

                self.pedal_sysex_1[2] = MIDIStatus.OFF
                sysex_message = SystemExclusive(self.manufacturer_id_pedal, self.pedal_sysex_1)
                self.midi.send(sysex_message)
            else:
                self.pedal_sysex_2[1] = (midi_value >> 7) & 0x7F
                self.pedal_sysex_2[2] = midi_value & 0x7F
                self.pedal_sysex_2[3] = MIDIStatus.ON
                sysex_message = SystemExclusive(self.manufacturer_id_pedal, self.pedal_sysex_2)
                self.midi.send(sysex_message)

                self.pedal_sysex_2[3] = MIDIStatus.OFF
                sysex_message = SystemExclusive(self.manufacturer_id_pedal, self.pedal_sysex_2)
                self.midi.send(sysex_message)
            return True
        except Exception as e:
            print("Error sending pedal SysEx: {}".format(e))
            return False

    def send_tab_sysex(self, midi_value):
        """Send SysEx for Tab commands"""
        try:
            self.tab_sysex[0] = midi_value
            self.tab_sysex[1] = MIDIStatus.ON
            sysex_message = SystemExclusive(self.manufacturer_id_tab, self.tab_sysex)
            self.midi.send(sysex_message)

            self.tab_sysex[1] = MIDIStatus.OFF
            sysex_message = SystemExclusive(self.manufacturer_id_tab, self.tab_sysex)
            self.midi.send(sysex_message)
            return True
        except Exception as e:
            print("Error sending tab SysEx: {}".format(e))
            return False

    def send_master_volume(self, updown):
        """Send volume via CC11"""
        try:
            # Change volume in 8-unit increments
            if updown == -1:
                self.cur_volume = max(0, self.cur_volume - 8)
            else:
                self.cur_volume = min(127, self.cur_volume + 8)

            self.midi.send(ControlChange(11, self.cur_volume), channel=15)
            return True
        except Exception as e:
            print("Error sending volume: {}".format(e))
            return False

    def send_quad_volume(self, midi_channel, volume):
        """Send volume CC for Quad Encoder configured channels"""
        try:
            self.midi.send(ControlChange(11, volume), midi_channel)
        except Exception as e:
            print("Error sending volume: {}".format(e))
            return False        

    def send_efxlevel_sysex(self, efxcode, volume):
        """Send SysEx EFX Level/Volume commands"""
        try:
            self.efx_level_sysex[0] = efxcode
            self.efx_level_sysex[2] = volume
            sysex_message = SystemExclusive(self.manufacturer_id_efx, self.efx_level_sysex)
            self.midi.send(sysex_message)

            return True
        except Exception as e:
            print("Error sending EFX Level SysEx: {}".format(e))
            return False

    def test_connectivity(self):
        """Test MIDI connectivity with audible notes"""
        try:
            # Define the notes for a short segment of "Ode to Joy"
            # Using MIDI note numbers (C4=60, D4=62, E4=64, F4=65, G4=67, A4=69, B4=71, C5=72)
            # The snippet is: E-E-F-G-G-F-E-D-C-C-D-E-E-D-D
            notes = [64, 64, 65, 67, 67, 65, 64, 62, 60, 60, 62, 64, 64, 62, 62] 
            durations = [0.5] * len(notes)  # Each note lasts for 0.5 seconds        
        
            for note, duration in zip(notes, durations):
                print("Sending test note: {}".format(note))
                self.midi.send(NoteOn(note, 120))
                time.sleep(duration)
                self.midi.send(NoteOff(note, 0))
            return True
        except Exception as e:
            print("MIDI test failed: {}".format(e))
            return False

# --- Key Lookup Cache for Performance ---
class KeyLookupCache:
    def __init__(self, config):
        self.config = config
        self.cache = {}

        # Initialize MacroPad key & color mappings to default MIDI message values
        # USB drive keysconfig.txt file will override if present
        self.macropad_key_map = [
            "1:VARIATION", "0:Arr.A", "0:Intro/End1", "0:Fill",
            "0:Arr.B", "0:Intro/End2","0:Break", "0:Arr.C",
            "0:Intro/End3", "0:Start/Stop", "0:Arr.D", "0:To End"
        ]
        self.macropad_color_map = [
            Colors.BLUE, Colors.BLUE, Colors.GREEN, Colors.GREEN,
            Colors.BLUE, Colors.GREEN, Colors.ORANGE, Colors.BLUE,
            Colors.GREEN, Colors.RED, Colors.BLUE, Colors.RED
        ]

        # Ketron Pedal and Tab MIDI lookup dictionaries
        self.pedal_midis = self._init_pedal_midis()
        self.tab_midis = self._init_tab_midis()

        self._build_cache()

    def _init_pedal_midis(self):
        """Initialize pedal MIDI dictionary"""
        return {
            "Sustain": 0x00, "Soft": 0x01, "Sostenuto": 0x02, "Arr.A": 0x03,
            "Arr.B": 0x04, "Arr.C": 0x05, "Arr.D": 0x06, "Fill1": 0x07,
            "Fill2": 0x08, "Fill3": 0x09, "Fill4": 0x0A, "Break1": 0x0B,
            "Break2": 0x0C, "Break3": 0x0D, "Break4": 0x0E, "Intro/End1": 0x0F,
            "Intro/End2": 0x10, "Intro/End3": 0x11, "Start/Stop": 0x12,
            "Tempo Up": 0x13, "Tempo Down": 0x14, "Fill": 0x15, "Break": 0x16,
            "To End": 0x17, "Bass to Lowest": 0x18, "Bass to Root": 0x19,
            "Live Bass": 0x1A, "Acc.BassToChord": 0x1B, "Manual Bass": 0x1C,
            "Voice Lock Bass": 0x1D, "Bass Mono/Poly": 0x1E, "Dial Down": 0x1F,
            "Dial Up": 0x20, "Auto Fill": 0x21, "Fill to Arr.": 0x22,
            "After Fill": 0x23, "Low. Hold Start": 0x24, "Low. Hold Stop": 0x25,
            "Low. Hold Break": 0x26, "Low. Stop Mute": 0x27, "Low. Mute": 0x28,
            "Low. and Bass": 0x29, "Low. Voice Lock": 0x2A, "Pianist": 0x2B,
            "Pianist Auto/Stand.": 0x2C, "Pianist Sustain": 0x2D, "Bassist": 0x2E,
            "Bassist Easy/Exp.": 0x2F, "Key Start": 0x30, "Key Stop": 0x31,
            "Enter": 0x32, "Exit": 0x33, "Registration": 0x34, "Fade": 0x35,
            "Harmony": 0x36, "Octave Up": 0x37, "Octave Down": 0x38,
            "RestartCount In": 0x39, "Micro1 On/Off": 0x3A, "Micro1 Down": 0x3B,
            "Micro1 Up": 0x3C, "Voicetr.On/Off": 0x3D, "Voicetr.Down": 0x3E,
            "Voicetr.Up": 0x3F, "Micro2 On/Off": 0x40, "EFX1 On/Off": 0x41,
            "EFX2 On/Off": 0x42, "Arabic.Set1": 0x43, "Arabic.Set2": 0x44,
            "Arabic.Set3": 0x45, "Arabic.Set4": 0x46, "Dry On Stop": 0x47,
            "Pdf Page Down": 0x48, "Pdf Page Up": 0x49, "Pdf Scroll Down": 0x4A,
            "Pdf Scroll Up": 0x4B, "Glide Down": 0x4C, "Lead Mute": 0x4D,
            "Expr. Left/Style": 0x4E, "Arabic Reset": 0x4F, "Hold": 0x50,
            "2nd On/Off": 0x51, "Pause": 0x52, "Talk On/Off": 0x53,
            "Manual Drum": 0x54, "Kick Off": 0x55, "Snare Off": 0x56,
            "Rimshot Off": 0x57, "Hit-Hat Off": 0x58, "Cymbal Off": 0x59,
            "Tom Off": 0x5A, "Latin1 Off": 0x5B, "Latin2 Off": 0x5C,
            "Latin3/Tamb Off": 0x5D, "Clap/fx Off": 0x5E, "Voice Down": 0x5F,
            "Voice Up": 0x60, "Regis Down": 0x61, "Regis Up": 0x62,
            "Style Voice Down": 0x63, "Style Voice Up": 0x64, "EFX1 Preset Down": 0x65,
            "EFX1 Preset Up": 0x66, "Multi": 0x67, "Page<<": 0x68, "Page>>": 0x69,
            "RegisVoice<<": 0x6A, "RegisVoice>>": 0x6B, "Text Page": 0x6E,
            "Text Page+": 0x6F, "Style Voice 1": 0x70, "Style Voice 2": 0x71,
            "Style Voice 3": 0x72, "Style Voice 4": 0x73, "VIEW & MODELING": 0x74,
            "Lock Bass": 0x75, "LockChord": 0x76, "Lyrics": 0x77,
            "VoiceToABCD": 0x87, "TAP": 0x88, "Autocrash": 0x89,
            "Transp Down": 0x8A, "Transp Up": 0x8B, "Text Record": 0x8C,
            "Bass & Drum": 0x8D, "Pdf Clear": 0x8E, "Record": 0x90, "Play": 0x91,
            "DoubleDown": 0x92, "DoubleUp": 0x93, "Arr.Off": 0x94,
            "FILL & DRUM IN": 0x95, "Wah to Pedal": 0x96, "Overdrive to Pedal": 0x98,
            "Drum Mute": 0x99, "Bass Mute": 0x9A, "Chords Mute": 0x9B,
            "Real Chords Mute": 0x9C, "Voice2 to Pedal": 0x9D, "Micro Edit": 0x9E,
            "Micro2 Edit": 0x9F, "HALF BAR": 0xA0, "Bs Sust Pedal": 0xA1,
            "Scale": 0xA2, "End Swap": 0xA3, "Set Down": 0xA4, "Set Up": 0xA5,
            "FswChDelay": 0xA6, "IntroOnArr.": 0xA7, "EndingOnArr.": 0xA8,
            "Arr. Down": 0xA9, "Arr. Up": 0xAA, "Ending1": 0xAB, "Ending2": 0xAC,
            "Ending3": 0xAD, "Bass Lock": 0xAE, "Intro Loop": 0xB0,
            "Scene Down": 0xB1, "Scene Up": 0xB2, "STEM Scene A": 0xB3,
            "STEM Scene B": 0xB4, "STEM Scene C": 0xB5, "STEM Scene D": 0xB6,
            "STEM Solo": 0xB7, "STEM Autoplay": 0xB8, "STEM A On/Off": 0xB9,
            "STEM B On/Off": 0xBA, "STEM C On/Off": 0xBB, "STEM D On/Off": 0xBC,
            "STEM Lead On/Off": 0xBD, "Art. Toggle": 0xBE, "Key Tune On/Off": 0xBF,
            "Txt Clear": 0xC0, "Voicetr. Edit": 0xC1, "Clear Image": 0xC2
        }

    def _init_tab_midis(self):
        """Initialize tab MIDI dictionary"""
        return {
            "DIAL_DOWN": 0x0, "DIAL_UP": 0x1, "PLAYER_A": 0x2, "PLAYER_B": 0x3,
            "ENTER": 0x4, "MENU": 0x6, "LYRIC": 0x7, "LEAD": 0x8, "VARIATION": 0x9,
            "DRAWBARS_VIEW": 0x0a, "DRAWBARS": 0x10, "DRUMSET": 0x11, "TALK": 0x12,
            "VOICETRON": 0x13, "STYLE_BOX": 0x14, "VOICE1": 0x19, "VOICE2": 0x1a,
            "USER_VOICE": 0x1b, "XFADE": 0x1c, "INTRO1": 0x1d, "INTRO2": 0x1e,
            "INTRO3": 0x1f, "BASSIST": 0x20, "DRUM_MIXER": 0x22, "OCTAVE_UP": 0x24,
            "OCTAVE_DOWN": 0x25, "USER_STYLE": 0x26, "DSP": 0x27, "ADSR_FILTER": 0x28,
            "MICRO": 0x29, "ARRA": 0x2c, "ARRB": 0x2d, "ARRC": 0x2e, "ARRD": 0x2f,
            "FILL": 0x30, "BREAK": 0x31, "JUKE_BOX": 0x32, "STEM": 0x33,
            "PIANIST": 0x34, "BASS_TO_LOWEST": 0x40, "MANUAL_BASS": 0x41,
            "PORTAMENTO": 0x48, "HARMONY": 0x49, "PAUSE": 0x4a, "TEMPO_SLOW": 0x4b,
            "TEMPO_FAST": 0x4c, "START_STOP": 0x4d, "TRANSP_DOWN": 0x59,
            "TRANSP_UP": 0x5a, "AFTERTOUCH": 0x5e, "EXIT": 0x5f, "ROTOR_SLOW": 0x60,
            "ROTOR_FAST": 0x61, "PIANO_FAM": 0x62, "ETHNIC_FAM": 0x63,
            "ORGAN_FAM": 0x64, "GUITAR_FAM": 0x65, "BASS_FAM": 0x66,
            "STRING_FAM": 0x67, "BRASS_FAM": 0x68, "SAX_FAM": 0x69, "HOLD": 0x6f,
            "PAD_FAM": 0x70, "SYNTH_FAM": 0x71, "FADEOUT": 0x73, "BASS_TO_ROOT": 0x74,
            "GM": 0x77
        }

    def _build_cache(self):
        """Build lookup cache at startup"""
        
        for i in range(12):
            key_id = self.config.get_key(i)
            mapped_key = self.macropad_key_map[key_id]

            if mapped_key and len(mapped_key) > 2 and mapped_key[1] == ':':
                try:
                    lookup_key = int(mapped_key[0])
                    midi_key = mapped_key[2:]

                    if lookup_key == MIDIType.PEDAL:
                        midi_value = self.pedal_midis.get(midi_key, 0)
                    else:
                        midi_value = self.tab_midis.get(midi_key, 0)

                    self.cache[i] = (lookup_key, midi_key, midi_value)
                except (ValueError, IndexError):
                    print("Error caching key {}: {}".format(i, mapped_key))
                    self.cache[i] = (0, "", 0)
            else:
                self.cache[i] = (0, "", 0)

    def get_key_midi(self, key_id):
        """Get cached MIDI data for key"""
        return self.cache.get(key_id, (0, "", 0))

    def validate_color_string(self, color_string):
        """Validate and return color code"""
        return COLOR_MAP.get(color_string.lower(), Colors.WHITE)

# --- Configuration File Handler ---
class ConfigFileHandler:
    def __init__(self, key_cache, config):
        self.key_cache = key_cache
        self.config = config
        self.config_error = False

    def safe_file_read(self, filename):
        """Safely read file with error handling"""
        
        try:
            with open(filename, "r") as f:
                return f.readlines()
        except (OSError, IOError) as e:
            print("Error reading {}: {}".format(filename, e))
            return []

    def parse_config_line(self, line):
        """Parse a single config line with validation"""
        
        try:
            line = line.strip()
            if line.startswith('#') or not line:
                return None

            if '=' not in line or line.count(':') < 2:
                raise ValueError("Invalid format")

            parts = line.split('=', 1)
            if len(parts) != 2 or not parts[0].startswith('key'):
                raise ValueError("Invalid key format")

            value_parts = parts[1].split(':')
            if len(value_parts) != 3:
                raise ValueError("Invalid value format")

            return {
                'key': parts[0],
                'type': int(value_parts[0]),
                'command': value_parts[1],
                'color': value_parts[2]
            }
        except (ValueError, IndexError) as e:
            print("Error parsing line '{}': {}".format(line, e))
            return None

    def validate_midi_string(self, midi_type, command):
        """Validate MIDI command against known commands"""
        
        if midi_type == MIDIType.PEDAL:
            return command in self.key_cache.pedal_midis
        else:
            return command in self.key_cache.tab_midis

    def load_config(self):
        """Load and validate configuration file"""
        
        key_index = 0
        config_errors = []

        try:
            lines = self.safe_file_read("/keysconfig.txt")
            if not lines:
                self.config_error = True
                print("Using default Config")
                return False
        except Exception as e:
            print("Config file missing")
            return False

        for line_num, line in enumerate(lines, 1):
            parsed = self.parse_config_line(line)
            if parsed is None:
                continue

            try:
                # Validate MIDI command
                if not self.validate_midi_string(parsed['type'], parsed['command']):
                    raise ValueError("Invalid MIDI command: {}".format(parsed['command']))

                mapped_key_index = self.config.get_key(key_index)

                # Apply configuration
                midi_string = "{}:{}".format(parsed['type'], parsed['command'])
                self.key_cache.macropad_key_map[mapped_key_index] = midi_string

                # Set color
                color_code = self.key_cache.validate_color_string(parsed['color'])
                self.key_cache.macropad_color_map[mapped_key_index] = color_code

                key_index += 1
                if key_index >= 12:
                    break

            except Exception as e:
                config_errors.append("Line {}: {}".format(line_num, e))

        if config_errors:
            print("Configuration errors:")
            for error in config_errors[:5]:  # Limit error display
                print("  {}".format(error))
            self.config_error = True
            return False

        # Rebuild cache with new configuration
        self.key_cache._build_cache()
        return True

# --- Display Manager ---
class DisplayManager:
    def __init__(self, macropad, config):
        self.macropad = macropad
        self.config = config
        self.labels = []
        self._init_display()

    def _init_display(self):
        """Initialize display layout"""
        
        main_group = displayio.Group()
        self.macropad.display.root_group = main_group

        title = label.Label(
            y=6,
            font=terminalio.FONT,
            color=0x0,
            text=self.config.display_banner,
            background_color=0xFFFFFF,
        )

        # Configure Display Grid
        layout = GridLayout(x=0, y=8, width=128, height=54, grid_size=(3, 4), cell_padding=5)

        for _ in range(12):
            self.labels.append(label.Label(terminalio.FONT, text=""))

        for index in range(12):
            x = index % 3
            y = index // 3
            layout.add_content(self.labels[index], grid_position=(x, y), cell_size=(1, 1))

        main_group.append(title)
        main_group.append(layout)

        # Display startup info
        self.show_startup_info()

    def show_startup_info(self):
        """Display startup information"""
        
        self.labels[3].text = self.config.display_sub_banner
        self.labels[6].text = "KNOB MODE: Rotor"
        # self.labels[9].text = "Version: {}".format(self.config.version)
        self.labels[9].text = "OS: {}".format(self.config.version)

    def update_text(self, index, text):
        """Update label text safely"""
        
        if 0 <= index < len(self.labels):
            self.labels[index].text = text

# --- State Manager ---
class StateManager:
    def __init__(self, config):
        self.config = config
        self.encoder_mode = EncoderMode.ROTOR
        self.encoder_position = 0
        self.encoder_sign = False
        self.rotor_flag = 0  # -1=slow, 0=off, 1=fast

        # Timing
        self.tempo_start_time = 0
        self.volume_start_time = 0
        self.value_start_time = 0
        self.version_start_time = 0
        self.led_start_time = 0

        # Preset version display to end after 15s
        self.version_start_time = time.time()

        # LED state
        self.lit_keys = [False] * 12
        
        # Tracks if I2C devices is attached.
        self.is_quadencoder = False
        
        self.quad_volumes = [0, 0, 0, 0]

        # NIDI Channel - 1
        # To do: Make configurable in config file
        self.chan_volume = 15
        self.chan_lower = 2
        self.chan_upper1 = 3
        self.chan_upper2 = 3
        self.chan_drawbar = 3

    def update_encoder_mode(self, new_mode):
        """Update encoder mode with timed reset"""
        
        self.encoder_mode = new_mode
        current_time = time.time()

        if new_mode == EncoderMode.TEMPO:
            self.tempo_start_time = current_time
        elif new_mode == EncoderMode.VOLUME:
            self.volume_start_time = current_time
        elif new_mode == EncoderMode.VALUE:
            self.value_start_time = current_time

    def check_timeouts(self):
        """Check and handle encoder mode timeouts"""
        current_time = time.time()

        # Revert tempo to rotor after timeout
        if (self.encoder_mode == EncoderMode.TEMPO and
            self.tempo_start_time != 0 and
            current_time - self.tempo_start_time > self.config.tempo_timer):
            self.encoder_mode = EncoderMode.ROTOR
            return "timeout_tempo"

        # Revert volume to rotor after timeout
        if (self.encoder_mode == EncoderMode.VOLUME and
            self.volume_start_time != 0 and
            current_time - self.volume_start_time > self.config.volume_timer):
            self.encoder_mode = EncoderMode.ROTOR
            return "timeout_volume"

        # Revert value to rotor after timeout
        if (self.encoder_mode == EncoderMode.VALUE and
            self.value_start_time != 0 and
            current_time - self.value_start_time > self.config.value_timer):
            self.encoder_mode = EncoderMode.ROTOR
            return "timeout_value"

        # Clear version value after timeout
        if (self.version_start_time != 0 and
            current_time - self.version_start_time > self.config.version_timer):
            self.version_start_time = 0
            return "timeout_version"

        # Check LED timeout
        if (self.led_start_time != 0 and
            current_time - self.led_start_time > self.config.key_bright_timer):
            self.led_start_time = 0
            return "timeout_led"

        return None

# --- Main Controller Class ---
class EVMController:
    def __init__(self):
        print("Initializing EVM Controller...")

        # Initialize components
        self.config = EVMConfig()
        self.state = StateManager(self.config)

        # Initialize MIDI
        self._init_midi()

        # Initialize MacroPad
        self._init_macropad()

        # Initialize key cache and config
        self.key_cache = KeyLookupCache(self.config)
        self.config_handler = ConfigFileHandler(self.key_cache, self.config)

        # Load configuration
        config_loaded = self.config_handler.load_config()

        # Initialize display
        self.display = DisplayManager(self.macropad, self.config)

        if not config_loaded:
            self.display.update_text(9, "Config File Error!")

        # Initialize pixels
        self._preset_pixels()

        # Initialize the Adafruit Quad Encoder
        self.state.is_quadencoder = self._init_quadencoder()
        #if self.state.is_quadencoder:
        #    print(self.quad_encoders)
        #    print(self.quad_switches)
        #    print(self.quad_last_positions)
        #    print(self.quad_pixels)

        print("Pad Controller Ready")

    def _init_midi(self):
        """Initialize MIDI connections"""
        
        print("Preparing Macropad Midi")
        print(usb_midi.ports)

        midi = adafruit_midi.MIDI(
            midi_in=usb_midi.ports[0], in_channel=0,
            midi_out=usb_midi.ports[1], out_channel=1
        )

        self.midi_handler = MIDIHandler(midi)

    def _init_macropad(self):
        """Initialize MacroPad hardware"""
        
        print("Preparing MacroPad Display")
        self.macropad = MacroPad(rotation=0)
        self.state.encoder_position = self.macropad.encoder

    def _init_quadencoder(self):
        """Initialize the Adafruit Quad Encoder"""
        try:
            # For boards/chips that don't handle clock-stretching well, try running I2C at 50KHz
            # import busio
            # i2c = busio.I2C(board.SCL, board.SDA, frequency=50000)
            # For using the built-in STEMMA QT connector on a microcontroller
            i2c = board.STEMMA_I2C()
            seesaw = adafruit_seesaw.seesaw.Seesaw(i2c, 0x49)

            self.quad_encoders = [adafruit_seesaw.rotaryio.IncrementalEncoder(seesaw, n) for n in range(4)]
            self.quad_switches = [adafruit_seesaw.digitalio.DigitalIO(seesaw, pin) for pin in (9, 17, 14, 12)]

            for switch in self.quad_switches:
                #switch.switch_to_input(adafruit_seesaw.digitalio.Pull.UP)  # input & pullup! Adafruit bug in sample code?
                switch.switch_to_input(pull=digitalio.Pull.UP)

            # four neopixels per PCB
            self.quad_pixels = adafruit_seesaw.neopixel.NeoPixel(seesaw, 18, 4)
            self.quad_pixels.brightness = 0.5

            self.quad_last_positions = [-1, -1, -1, -1]
            self.quad_colors = [0, 0, 0, 0]  # Start at red (muted)
            
            # Re-initialize the encoder last position tracked by reading the current state
            # No MIDI message sent since we do not know if the EVM is online yet
            positions = [encoder.position for encoder in self.quad_encoders]
            for n, rotary_pos in enumerate(positions):
                self.quad_last_positions[n] = rotary_pos

            print("Quad Encoders configured")
            return True
            
        except Exception as e:
            print("Error: Quad Encoder: {}".format(e))
            return False

    def _preset_pixels(self):
        """Set pixel colors based on configuration"""
        for pixel in range(12):
            if self.config_handler.config_error:
                self.macropad.pixels[pixel] = Colors.RED
            elif pixel == self.config.get_key(VARIATION_KEY):  # Variation key
                if self.state.encoder_mode == EncoderMode.TEMPO:
                    self.macropad.pixels[pixel] = Colors.YELLOW
                elif self.state.encoder_mode == EncoderMode.VOLUME:
                    self.macropad.pixels[pixel] = Colors.PURPLE
                elif self.state.encoder_mode == EncoderMode.VALUE:
                    self.macropad.pixels[pixel] = Colors.WHITE
                else:
                    self.macropad.pixels[pixel] = self.key_cache.macropad_color_map[pixel]
            else:
                self.macropad.pixels[pixel] = self.key_cache.macropad_color_map[pixel]

            self.state.lit_keys[pixel] = False

    def _handle_key_press(self, key_number):
        """Handle key press events"""
        key_id = self.config.get_key(key_number)
        lookup_key, midi_key, midi_value = self.key_cache.get_key_midi(key_id)

        # Send MIDI command
        if lookup_key == MIDIType.PEDAL:
            self.midi_handler.send_pedal_sysex(midi_value)
        else:
            self.midi_handler.send_tab_sysex(midi_value)

        # Update display
        self.display.update_text(3, "BUTTON: {}".format(midi_key))

        # Handle special cases
        if midi_key == "Start/Stop":
            self.state.update_encoder_mode(EncoderMode.TEMPO)
            self.display.update_text(6, "KNOB MODE: *Tempo")

        # Update LEDs
        self._preset_pixels()
        self.state.lit_keys[self.config.get_key(key_number)] = True
        self.state.led_start_time = time.time()

        return midi_key

    def _handle_encoder_change(self, direction):
        """Handle encoder rotation"""
        self.state.encoder_sign = not self.state.encoder_sign
        current_time = time.time()

        if self.state.encoder_mode == EncoderMode.ROTOR:
            self._process_rotor(direction)
        elif self.state.encoder_mode == EncoderMode.TEMPO:
            self._process_tempo(direction)
            self.state.tempo_start_time = current_time
        elif self.state.encoder_mode == EncoderMode.VOLUME:
            self._process_master_volume(direction)
            self.state.volume_start_time = current_time
        elif self.state.encoder_mode == EncoderMode.VALUE:
            self._process_value(direction)
            self.state.value_start_time = current_time

    def _process_rotor(self, direction):
        """Process rotor fast/slow commands"""
        if direction == 1 and self.state.rotor_flag != 1:
            midi_value = self.key_cache.tab_midis["ROTOR_FAST"]
            self.display.update_text(3, "KNOB: Rotor Fast")
            self.state.rotor_flag = 1
            self.midi_handler.send_tab_sysex(midi_value)
        elif direction == -1 and self.state.rotor_flag != -1:
            midi_value = self.key_cache.tab_midis["ROTOR_SLOW"]
            self.display.update_text(3, "KNOB: Rotor Slow")
            self.state.rotor_flag = -1
            self.midi_handler.send_tab_sysex(midi_value)

    def _process_tempo(self, direction):
        """Process tempo up/down commands"""
        sign = "+" if self.state.encoder_sign else ""
        if direction == 1:
            midi_value = self.key_cache.pedal_midis["Tempo Up"]
            self.display.update_text(3, "KNOB: Tempo Up{}".format(sign))
        else:
            sign = "-" if self.state.encoder_sign else ""
            midi_value = self.key_cache.pedal_midis["Tempo Down"]
            self.display.update_text(3, "KNOB: Tempo Down{}".format(sign))

        self.midi_handler.send_pedal_sysex(midi_value)

    def _process_master_volume(self, direction):
        """Process volume up/down commands"""
        sign = "+" if self.state.encoder_sign else ""
        if direction == 1:
            self.display.update_text(3, "KNOB: Volume Up{}".format(sign))
        else:
            self.display.update_text(3, "KNOB: Volume Down{}".format(sign))

        self.midi_handler.send_master_volume(direction)

    def _process_quad_volume(self, encoder_number, volume):
        """Process Quad Encoder Volumes"""
        # Lookup channel for the quad encoder number before sending
        #midi_channel = 0
        #if encoder_number == 0:            
        #    midi_channel = self.state.chan_drawbar
        #    self.display.update_text(9, f"QUAD Drawbar Vol:{volume}")
        #    self.midi_handler.send_quad_volume(midi_channel, volume)

        if encoder_number == 0:
            self.display.update_text(9, f"QUAD Upper1 Vol:{volume}")
            self.midi_handler.send_efxlevel_sysex(EFXLevel.Voice1, volume)
        elif encoder_number == 1:
            self.display.update_text(9, f"QUAD Upper2 Vol:{volume}")
            self.midi_handler.send_efxlevel_sysex(EFXLevel.Voice2, volume)
        elif encoder_number == 2:
            self.display.update_text(9, f"QUAD R/Chord Vol:{volume}")
            self.midi_handler.send_efxlevel_sysex(EFXLevel.RealChord, volume)
        elif encoder_number == 3:
            self.display.update_text(9, f"QUAD Left/GM Vol:{volume}")
            self.midi_handler.send_efxlevel_sysex(EFXLevel.LeftGM, volume)

    def _process_value(self, direction):
        """Process value (DIAL) up/down commands"""
        sign = "+" if self.state.encoder_sign else ""
        if direction == 1:
            midi_value = self.key_cache.tab_midis["DIAL_UP"]
            self.display.update_text(3, "KNOB: Dial Up{}".format(sign))
        else:
            sign = "-" if self.state.encoder_sign else ""
            midi_value = self.key_cache.tab_midis["DIAL_DOWN"]
            self.display.update_text(3, "KNOB: Dial Down{}".format(sign))

        self.midi_handler.send_tab_sysex(midi_value)

    def _handle_encoder_switch(self):        
        """Handle encoder switch press. Modes 0:Rotor, 1:Tempo, 2:Volume, 3:Dial (disabled)"""
        
        self.state.encoder_mode = self.state.encoder_mode + 1
        if self.state.encoder_mode > 2: self.state.encoder_mode = 0
        current_time = time.time()

        if self.state.encoder_mode == EncoderMode.ROTOR:
            self.display.update_text(3, "KNOB: -")
            self.display.update_text(6, "KNOB MODE: Rotor")
        elif self.state.encoder_mode == EncoderMode.TEMPO:
            self.display.update_text(3, "KNOB: -")
            self.display.update_text(6, "KNOB MODE: *Tempo")
            self.state.tempo_start_time = current_time
        elif self.state.encoder_mode == EncoderMode.VOLUME:
            self.display.update_text(3, "KNOB: -")
            self.display.update_text(6, "KNOB MODE: *Volume")
            self.state.volume_start_time = current_time
        elif self.state.encoder_mode == EncoderMode.VALUE:
            self.display.update_text(3, "KNOB: -")
            self.display.update_text(6, "KNOB MODE: *Dial")
            self.state.value_start_time = current_time

        self._preset_pixels()

    def _handle_quadencoder(self):
        """Handle quad encoder rotary encoders and switchs press."""
        
        # Negate the position to make clockwise rotation positive
        positions = [encoder.position for encoder in self.quad_encoders]

        for n, rotary_pos in enumerate(positions):
            if rotary_pos != self.quad_last_positions[n]:
                
                # If switch not pressed, update volume for encoders 
                if self.quad_switches[n].value:  
                    # Update channel volume with new encoder position 
                    if rotary_pos > self.quad_last_positions[n]: 
                        self.state.quad_volumes[n] += 8        # Advance forward
                        if self.state.quad_volumes[n] >= 127: self.state.quad_volumes[n] = 127
                        self._process_quad_volume(n, self.state.quad_volumes[n])
                    elif rotary_pos < self.quad_last_positions[n]:
                        self.state.quad_volumes[n] -= 8        # Advance backward
                        if self.state.quad_volumes[n] <= 0: self.state.quad_volumes[n] = 0
                        self._process_quad_volume(n, self.state.quad_volumes[n])
                    #print(f"Encoder {n} value {self.state.quad_volumes[n]}")
                                        
                    # Change the LED colors
                    # if rotary_pos > self.quad_last_positions[n]:  # Advance forward through the colorwheel.
                    #    self.quad_colors[n] += 8
                    # else:
                    #    self.quad_colors[n] -= 8  # Advance backward through the colorwheel.
                    #self.quad_colors[n] = (self.quad_colors[n] + 256) % 256  # wrap around to 0-256
                                
                # Set last position to current position after evaluating
                self.quad_last_positions[n] = rotary_pos

            # if switch is pressed, light up white, otherwise use the stored color
            #if not self.quad_switches[n].value:
            #    self.quad_pixels[n] = 0xFFFFFF
            #else:
            #    self.quad_pixels[n] = colorwheel(self.quad_colors[n])

    def _update_display(self):
        """Update display based on timeouts"""
        timeout_type = self.state.check_timeouts()

        if timeout_type == "timeout_tempo" or timeout_type == "timeout_volume":
            self.display.update_text(3, "KNOB: -")
            self.display.update_text(6, "KNOB MODE: Rotor")
            self._preset_pixels()
        elif timeout_type == "timeout_version":
            self.display.update_text(9, "")
        elif timeout_type == "timeout_led":
            self._preset_pixels()

    def _update_pixels(self):
        """Update pixel colors for lit keys"""
        for pixel in range(12):
            if self.state.lit_keys[pixel]:
                self.macropad.pixels[self.config.get_key(pixel)] = Colors.WHITE

    def run(self):
        """Main controller loop"""
        
        # Run initial MIDI test
        if TEST_CONNECT == True:
            self.midi_handler.test_connectivity()
        
        while True:
            try:
                # Handle key events
                key_event = self.macropad.keys.events.get()
                if key_event and key_event.pressed:
                    self._handle_key_press(key_event.key_number)

                # Handle encoder rotation
                if self.state.encoder_position != self.macropad.encoder:
                    direction = 1 if self.state.encoder_position < self.macropad.encoder else -1
                    self._handle_encoder_change(direction)
                    self.state.encoder_position = self.macropad.encoder

                # Handle encoder switch
                self.macropad.encoder_switch_debounced.update()
                if self.macropad.encoder_switch_debounced.pressed:
                    self._handle_encoder_switch()

                # Handle quad encoder board
                if self.state.is_quadencoder:
                    self._handle_quadencoder()

                # Update display and handle timeouts
                self._update_display()

                # Update pixels
                self._update_pixels()

            except Exception as e:
                print("Error in main loop: {}".format(e))
                time.sleep(0.1)  # Brief delay on error

# --- Main Execution ---
if __name__ == "__main__":
    try:
        controller = EVMController()
        controller.run()
    except Exception as e:
        print("Fatal error: {}".format(e))
        # Try to display error if possible
        try:
            macropad = MacroPad(rotation=0)
            # Simple error display
            for i in range(12):
                macropad.pixels[i] = Colors.RED
        except:
            pass
