# Yamaha Genos Button Controller

# Note: The Genos does not seem to accept SysEx messages from external controllers.
# It hadles MIDI NoteOn and NoteOff only and We may remove SysEx support to clean the code up

import board, displayio
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

# Set to FALSE for no startup test
TEST_CONNECT = False

# --- Constants and Enums ---
class EncoderMode:
    TEMPO = 0
    VOLUME = 1

class MIDIType:
    NOTE = 0
    PEDAL = 1
    MACRO = 2
    
class MIDIStatus:
    OFF = 0x00
    ON = 0x7F

class ShiftKeyMode:
    OFF = 0
    PENDING = 1
    ACTIVE_SHIFT = 2
    ACTIVE_LOCK = 3

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
    TEAL = 0x004040

# Color mapping dictionary
COLOR_MAP = {
    'red': Colors.RED,
    'green': Colors.GREEN,
    'blue': Colors.BLUE,
    'purple': Colors.PURPLE,
    'yellow': Colors.YELLOW,
    'orange': Colors.ORANGE,
    'white': Colors.WHITE,
    'teal': Colors.TEAL
}

# Key used to reflect timed Eccoder mode changes on LED
VARIATION_KEY = 0

# Key used to trigger test tune
TUNE_KEY = 11

# --- Configuration Class ---
class ControllerConfig:
    def __init__(self):
        self.display_banner =     "   YAMAHA GENOS     "
        self.display_sub_banner = "Arranger Controller "
        self.version = "1.0"

        # USB port on the left side of the MacroPad
        self.usb_left = True

        # Timers for tempo, volume, and key brightness
        self.tempo_timer = 60
        self.volume_timer = 60
        self.encoder_timer = 15
        self.version_timer = 15
        self.key_bright_timer = 0.20
        self.key_hold_timer = 1
        
        # Initialize MacroPad key mappings for Genos Layout
        self.key_map = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

    def get_key(self, key):
        """Safe key mapping with bounds checking"""
        if key < 0 or key > 11:
            print("Invalid key map request: {}".format(key))
            return 0
        return self.key_map[key]

# --- MIDI Handler Class ---
class MIDIHandler:
    def __init__(self, midi_instance, key_cache):
        self.midi = midi_instance
        self.key_cache = key_cache

        self.manufacturer_id = bytearray([0x43])

        # Pre-allocate bytearrays for memory efficiency
        self.section_sysex = bytearray([0x7E, 0x00, 0x00, 0x00])
        self.startstop_sysex = bytearray([0x00, 0x00])
        self.tempo_sysex = bytearray([0x7E, 0x01, 0x00, 0x00, 0x00, 0x00])    # Tempo 1 to 4 up to value of 127

        self.cur_volume = 100
        self.cur_tempo = 90

    def send_section_sysex(self, midi_value):
        """Send SysEx from Section set of commands"""
        try:
            # Send ON followed by OFF Message
            self.section_sysex[2] = midi_value
            self.section_sysex[3] = MIDIStatus.ON
            sysex_message = SystemExclusive(self.manufacturer_id, self.section_sysex)
            self.midi.send(sysex_message)

            self.section_sysex[3] = MIDIStatus.OFF
            sysex_message = SystemExclusive(self.manufacturer_id, self.section_sysex)
            self.midi.send(sysex_message)
            return True
        except Exception as e:
            print("Error sending pedal SysEx: {}".format(e))
            return False

    def send_tempo_sysex(self, direction):
        """Send Tempo SysEx command
            To do: Update for Genos
            F0 43 7E 01 t4 t3 t2 t1 F7"""

        # Tempo max = 127 and min = 0 in increments of 1 (or more) to manage encoder turns
        if direction == 1:
            self.cur_tempo = self.cur_tempo + 1
            if self.cur_tempo > 500:
                self.cur_tempo = 500
        else:
            self.cur_tempo = self.cur_tempo - 1
            if self.cur_tempo < 0:
                self.cur_tempo = 0

        try:
            self.tempo_sysex = self.tempo_genos(self.cur_tempo)
            sysex_message = SystemExclusive(self.manufacturer_id, self.tempo_sysex)
            self.midi.send(sysex_message)
            return True

        except Exception as e:
            print("Error sending tempo SysEx: {}".format(e))
            return False

    """
    Prepare to calculate and send Yamaha Tempo
    See: https://forum.psrtutorial.com/index.php?topic=48303.0
    """

    def hex_convert(self, mynumber):
        """Convert a number to hexadecimal string with even length padding"""
        hex_string = hex(mynumber)[2:]  # Remove '0x' prefix

        if len(hex_string) % 2:
            hex_string = '0' + hex_string

        return hex_string

    def tempo_genos(self, tempo):
        """Calculate tempo PSR or Genos (Yamaha SysEx format)"""
        total_tempo = int(60000000 / tempo)

        # Extract 7-bit chunks in Yamaha order (T4, T3, T2, T1)
        x_tempo4 = (total_tempo >> 21) & 127  # 21 bit shift
        x_tempo3 = (total_tempo >> 14) & 127  # 14 bit shift
        x_tempo2 = (total_tempo >> 7) & 127   # 7 bit shift
        x_tempo1 = total_tempo & 127          # 0 bit shift

        # Build SysEx message - minus start and end which is added by Adafruit MIDI library
        sysex_parts = bytearray([
            0x01,     # Sub-status
            x_tempo4,   # Tempo byte 4
            x_tempo3,   # Tempo byte 3
            x_tempo2,   # Tempo byte 2
            x_tempo1    # Tempo byte 1
        ])

        return sysex_parts

    def send_note(self, note):
        """Send a MIDI note"""
        try:
            self.midi.send(NoteOn(note, 120))
            self.midi.send(NoteOff(note, 0))
            return True
        except Exception as e:
            print("MIDI note send failed: {}".format(e))
            return False

    def send_macro_notes(self, midi_key):
        """Send one or more macro MIDI Note(s)"""
        try:
            for macro in self.key_cache.user_macro_midis:
                for value in macro.get(midi_key, []):
                    hex_value = self.key_cache.pedal_midis.get(value, "")
                    if hex_value:
                        self.send_note(hex_value)
            return True
        except Exception as e:
            print("Error sending macros Notes: {}".format(e))
            return False

    def send_encoder_note(self, direction):
        """Send notes for encodder rotate left and right"""
        # To do: Add lookup similar to key press and consider shift state
        if direction == 1:
            self.send_note(0x31)
        else:
            self.send_note(0x30)

    def test_connectivity(self):
        """Test MIDI connectivity with audible notes"""
        try:
            # Notes for a short segment of "Ode to Joy"
            # Using MIDI note numbers (C4=60, D4=62, E4=64, F4=65, G4=67, A4=69, B4=71, C5=72)
            notes = [64, 64, 65, 67, 67, 65, 64, 62, 60, 60, 62, 64, 64, 62, 62] 
            durations = [0.4] * len(notes)       

            for note, duration in zip(notes, durations):
                self.midi.send(NoteOn(note, 120))
                time.sleep(duration)
                self.midi.send(NoteOff(note, 0))
                time.sleep(duration/4)
            return True
        except Exception as e:
            print("MIDI test failed: {}".format(e))
            return False

# --- Key Lookup Cache for Performance ---
class KeyLookupCache:
    def __init__(self, config):
        self.config = config
        self.cache = {}
        self.cache_shift = {}

        # Initialize MacroPad key & color mappings to default MIDI message values
        # USB drive keysconfig.txt file will override if present
        self.macropad_key_map = [
            "0:G#0", "0:E0", "0:C0", "0:A0",
            "0:F0", "0:C#0","0:A#0", "0:F#0",
            "0:D0", "0:B0", "0:G0", "0:D#0"
        ]
        self.macropad_color_map = [
            Colors.ORANGE, Colors.TEAL, Colors.GREEN,
            Colors.ORANGE, Colors.TEAL, Colors.GREEN,
            Colors.ORANGE, Colors.TEAL, Colors.GREEN,
            Colors.ORANGE, Colors.TEAL, Colors.GREEN
        ]

        self.macropad_key_map_shift = [
            "0:G#1", "0:E1", "0:C1", "0:A1",
            "0:F1", "0:C#1","0:A#1", "0:F#1",
            "0:D1", "0:B1", "0:G1", "0:D#1"
        ]
        self.macropad_color_map_shift = [
            Colors.ORANGE, Colors.BLUE, Colors.GREEN,
            Colors.ORANGE, Colors.BLUE, Colors.GREEN,
            Colors.ORANGE, Colors.BLUE, Colors.GREEN,
            Colors.ORANGE, Colors.BLUE, Colors.GREEN
        ]

        self.user_macro_midis = [
            {
                "PLUGGED": ["C0"],
                "UNPLUGGED": ["C0", "C0"],
                "VOICEMUTE": [ "C0", "C0", "C0"]
            }
        ]

        # Ketron Pedal and Tab MIDI lookup dictionaries
        self.note_midis = self._init_note_midis()
        self.pedal_midis = self._init_pedal_midis()

        self._build_cache()


    def _init_note_midis(self):
        """Initialize tab MIDI dictionary"""
        return {
            "C0": 0x18, "C#0": 0x19, "D0": 0x1A, "D#0": 0x1B,
            "E0": 0x1C, "F0": 0x1D, "F#0": 0x1E, "G0": 0x1F, 
            "G#0": 0x20,"A0": 0x21, "A#0": 0x22, "B0": 0x23, 
            "C1": 0x24, "C#1": 0x25, "D1": 0x26, "D#1": 0x27,
            "E1": 0x28, "F1": 0x29, "F#1": 0x2A, "G1": 0x2B, 
            "G#1": 0x2C,"A1": 0x2D, "A#1": 0x2E, "B1": 0x2F,
            "C2": 0x30, "C#2": 0x31
        }

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

    def _build_cache(self):
        """Build lookup cache at startup"""
        
        # Build Default layer cache
        for i in range(12):
            key_id = self.config.get_key(i)
            mapped_key = self.macropad_key_map[key_id]

            if mapped_key and len(mapped_key) > 2 and mapped_key[1] == ':':
                try:
                    lookup_key = int(mapped_key[0])
                    midi_key = mapped_key[2:]

                    if lookup_key == MIDIType.NOTE:
                        midi_value = self.note_midis.get(midi_key, 0)
                    else:
                        midi_value = self.pedal_midis.get(midi_key, 0)

                    self.cache[i] = (lookup_key, midi_key, midi_value)
                except (ValueError, IndexError):
                    print("Error caching key {}: {}".format(i, mapped_key))
                    self.cache[i] = (0, "", 0)
            else:
                self.cache[i] = (0, "", 0)

        # Build Shift Layer cache
        for i in range(12):
            key_id = self.config.get_key(i)
            mapped_key = self.macropad_key_map_shift[key_id]

            if mapped_key and len(mapped_key) > 2 and mapped_key[1] == ':':
                try:
                    lookup_key = int(mapped_key[0])
                    midi_key = mapped_key[2:]

                    if lookup_key == MIDIType.NOTE:
                        midi_value = self.note_midis.get(midi_key, 0)
                    else:
                        midi_value = self.pedal_midis.get(midi_key, 0)

                    self.cache_shift[i] = (lookup_key, midi_key, midi_value)
                except (ValueError, IndexError):
                    print("Error caching shift key {}: {}".format(i, mapped_key))
                    self.cache_shift[i] = (0, "", 0)
            else:
                self.cache_shift[i] = (0, "", 0)

    def get_key_midi(self, key_id, shift_mode):
        """Get cached MIDI data for key"""
        if (shift_mode == ShiftKeyMode.ACTIVE_SHIFT) or (shift_mode == ShiftKeyMode.ACTIVE_LOCK):
            return self.cache_shift.get(key_id, (0, "", 0))
        else:
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
        self.encoder_mode = EncoderMode.TEMPO
        self.encoder_position = 0
        self.encoder_sign = False
        self.rotor_flag = 0  # -1=slow, 0=off, 1=fast
        
        # Controller Shift Mode based on Variation Key
        self.shift_mode = ShiftKeyMode.OFF

        # Timing
        self.tempo_start_time = 0
        self.volume_start_time = 0
        self.version_start_time = 0
        self.led_start_time = 0

        # Preset version display to end after 15s
        self.version_start_time = time.time()
        self.encoder_start_time = time.time()

        # LED state
        self.lit_keys = [False] * 12

    def update_encoder_mode(self, new_mode):
        """Update encoder mode with timed reset"""
        self.encoder_mode = new_mode
        current_time = time.time()

        if new_mode == EncoderMode.TEMPO:
            self.tempo_start_time = current_time
        elif new_mode == EncoderMode.VOLUME:
            self.volume_start_time = current_time

    def check_timeouts(self):
        """Check and handle encoder mode timeouts"""
        current_time = time.time()

        # Revert volume to rotor after timeout
        if (self.encoder_mode == EncoderMode.VOLUME and
            self.volume_start_time != 0 and
            current_time - self.volume_start_time > self.config.volume_timer):
            self.encoder_mode = EncoderMode.ROTOR
            return "timeout_volume"

        # Clear version value after timeout
        if (self.version_start_time != 0 and
            current_time - self.version_start_time > self.config.version_timer):
            self.version_start_time = 0
            return "timeout_version"

        # Clear encoder value after timeout
        if (self.encoder_start_time != 0 and
            current_time - self.encoder_start_time > self.config.encoder_timer):
            self.encoder_start_time = 0
            return "timeout_version"

        # Check LED timeout
        if (self.led_start_time != 0 and
            current_time - self.led_start_time > self.config.key_bright_timer):
            self.led_start_time = 0
            return "timeout_led"

        return None

# --- Main Controller Class ---
class GenosController:
    def __init__(self):
        print("Initializing EVM Controller...")

        # Initialize components
        self.config = ControllerConfig()
        self.state = StateManager(self.config)

        # Initialize key cache and config
        self.key_cache = KeyLookupCache(self.config)
        # self.config_handler = ConfigFileHandler(self.key_cache, self.config)

        # Initialize MIDI
        self._init_midi(self.key_cache)

        # Initialize MacroPad
        self._init_macropad()
        
        # Load configuration
        # config_loaded = self.config_handler.load_config()

        # Initialize display
        self.display = DisplayManager(self.macropad, self.config)

        # if not config_loaded:
        #    self.display.update_text(9, "Config File Error!")

        # Initialize pixels
        self._preset_pixels()

        print("Pad Controller Ready")

    def _init_midi(self, key_cache):
        """Initialize MIDI connections"""        
        print("Preparing Macropad Midi")
        print(usb_midi.ports)

        midi = adafruit_midi.MIDI(
            midi_in=usb_midi.ports[0], in_channel=0,
            midi_out=usb_midi.ports[1], out_channel=15
        )

        self.midi_handler = MIDIHandler(midi, key_cache)

    def _init_macropad(self):
        """Initialize MacroPad hardware"""
        print("Preparing MacroPad Display")
        self.macropad = MacroPad(rotation=0)
        self.state.encoder_position = self.macropad.encoder

    def _preset_pixels(self):
        """Set pixel colors based on configuration"""
        for pixel in range(12):
            if (self.state.shift_mode == ShiftKeyMode.ACTIVE_SHIFT) or (self.state.shift_mode == ShiftKeyMode.ACTIVE_LOCK):
                self.macropad.pixels[pixel] = self.key_cache.macropad_color_map_shift[pixel]
            else:
                self.macropad.pixels[pixel] = self.key_cache.macropad_color_map[pixel]

            self.state.lit_keys[pixel] = False

    def _handle_key_press(self, key_number):
        """Handle key press events"""
        try:
            key_id = self.config.get_key(key_number)

            lookup_key, midi_key, midi_value = self.key_cache.get_key_midi(key_id, self.state.shift_mode)

            # print(f"get_key: {lookup_key}, {midi_key}, {midi_value}")

            # Send MIDI command or lookup and sebnd user macro MIDI commands
            if lookup_key == MIDIType.NOTE:
                self.midi_handler.send_note(midi_value)
                
            elif lookup_key == MIDIType.PEDAL:
                self.midi_handler.send_pedal_sysex(midi_value)
                
            elif lookup_key == MIDIType.MACRO:
                self.midi_handler.send_macro_notes(midi_key)
                
            else:
                return midi_key

            # Update display
            self.display.update_text(3, "NOTE: {}".format(midi_key))

            # Update LEDs
            self._preset_pixels()
            self.state.lit_keys[self.config.get_key(key_number)] = True
            self.state.led_start_time = time.time()

            return midi_key
            
        except Exception as e:
            print(f"Error: Sending key {key_number} ".format(e))
            return False
            
    def _process_tempo(self, direction):
        """Process tempo up/down commands"""
        sign = "+" if self.state.encoder_sign else ""
        if direction == 1:
            self.display.update_text(3, "KNOB: Tempo Up{}".format(sign))
        else:
            sign = "-" if self.state.encoder_sign else ""
            self.display.update_text(3, "KNOB: Tempo Down{}".format(sign))

        self.midi_handler.send_tempo_sysex(direction)

    def _process_master_volume(self, direction):
        """Process volume up/down commands"""
        sign = "+" if self.state.encoder_sign else ""
        if direction == 1:
            self.display.update_text(3, "KNOB: Volume Up{}".format(sign))
        else:
            self.display.update_text(3, "KNOB: Volume Down{}".format(sign))

        self.midi_handler.send_master_volume(direction)

    def _handle_encoder_change(self, direction):
        """Handle encoder rotation"""
        print(f"Encoder Change: {direction}")
        
        self.state.encoder_sign = not self.state.encoder_sign
        encoder_timer = time.time()

        if direction == 1:
            self.display.update_text(6, "ENCODER: C#2")
        else:
            self.display.update_text(6, "ENCODER: C2")

        self.midi_handler.send_encoder_note(direction)

    def _handle_encoder_switch(self):
        """Handle encoder switch"""
        if (self.state.shift_mode == ShiftKeyMode.OFF) or (self.state.shift_mode == ShiftKeyMode.PENDING) or (self.state.shift_mode == ShiftKeyMode.ACTIVE_SHIFT):
            self.state.shift_mode = ShiftKeyMode.ACTIVE_LOCK
            self.display.update_text(9, "Shift: Active")
        else:
            self.state.shift_mode = ShiftKeyMode.OFF
            self.display.update_text(9, "Shift: Off")

        version_timer = time.time()
        self._preset_pixels()
        
    def _update_display(self):
        """Update display based on timeouts"""
        timeout_type = self.state.check_timeouts()

        if timeout_type == "timeout_version":
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
        
        key_start_time = 0
        key_hold_timer = 0.25
        shift_start_time  = 0      
        shift_hold_timer = 0.25
        
        while True:
            try:
                # Handle key events, press and release
                key_event = self.macropad.keys.events.get()
                
                if key_event and key_event.pressed:                    
                    self._handle_key_press(key_event.key_number)        # Send any key MIDI message
                    key_start_time = time.time()                    
                            
                # Handle encoder rotation
                if self.state.encoder_position != self.macropad.encoder:
                    direction = 1 if self.state.encoder_position < self.macropad.encoder else -1
                    self._handle_encoder_change(direction)
                    self.state.encoder_position = self.macropad.encoder

                # Handle encoder switch
                self.macropad.encoder_switch_debounced.update()
                if self.macropad.encoder_switch_debounced.pressed:
                    self._handle_encoder_switch()

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
        controller = GenosController()
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