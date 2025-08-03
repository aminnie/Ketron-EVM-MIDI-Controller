
# Yamaha Genos Arranger Controller
# https://usa.yamaha.com/products/musical_instruments/keyboards/arranger_workstations/genos2/downloads.html


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

# --- Constants and Enums ---
class EncoderMode:
    ROTOR = 0
    TEMPO = 1
    VOLUME = 2
    VALUE = 3

class MIDIType:
    PRI = 0
    SEC = 1

class MIDIStatus:
    OFF = 0x00
    ON = 0x7F

class Colors:
    WHITE = 0x606060
    BLUE = 0x33717a # 0x66D3FA
    GREEN = 0x002000
    RED = 0x200000
    ORANGE = 0x701E02
    PURPLE = 0x200020
    YELLOW = 0x202000

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
        self.display_banner =     "   YAMAHA GENOS     "
        self.display_sub_banner = "Arranger Controller "
        self.version = "1.0"

        # USB port on the left side of the MacroPad
        self.usb_left = True

        # Timers for tempo, volume, and key brightness
        self.tempo_timer = 60
        self.volume_timer = 60
        self.value_timer = 60
        self.version_timer = 15
        self.key_bright_timer = 0.20

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

    def send_startstop_sysex(self, midi_value):
        """Send Start Stop toggling SysEx command
            Start: F0 04 43 60 7A F7
            Stop:  F0 04 43 60 7D F7"""

        # Override the section messages manufacturer id. 
        # To do: Verify that this id is correct
        manufacturer_id = bytearray([0x43, 0x04])  # Yamaha manufacturer ID and Device ID

        midi_byte = 0x7A
        if midi_value == True:
            midi_byte = 0x7D
        
        try:
            # Send ON followed by OFF Message
            self.startstop_sysex[0] = 0x60
            self.startstop_sysex[1] = midi_byte
            sysex_message = SystemExclusive(manufacturer_id, self.startstop_sysex)
            self.midi.send(sysex_message)

            return True
        except Exception as e:
            print("Error sending start/stop SysEx: {}".format(e))
            return False
               
    def send_master_volume(self, updown):
        """Send Master volume control via CC11"""
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

    def test_connectivity(self):
        """Test MIDI connectivity with audible notes"""
        try:
            for x in range(4):
                print("Sending test note: {}".format(x))
                self.midi.send(NoteOn("C4", 120))
                time.sleep(0.25)
                self.midi.send(NoteOff("C4", 0))
                time.sleep(0.25)
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
        # USB drive keysconfig.txt file will override if present. BHowever, not supported for the Genos yet
        self.macropad_key_map = [
            "0:Ending 1", "0:Main A", "0:Intro 1", 
            "0:Ending 2", "0:Main B", "0:Intro 2",
            "0:Ending 3", "0:Main C", "0:Intro 3", 
            "0:Start/Stop", "0:Main D", "0:Break"
        ]
        self.macropad_color_map = [
            Colors.ORANGE, Colors.BLUE, Colors.GREEN, 
            Colors.ORANGE, Colors.BLUE, Colors.GREEN, 
            Colors.ORANGE, Colors.BLUE, Colors.GREEN, 
            Colors.RED, Colors.BLUE, Colors.ORANGE
        ]

        # Ketron Section and Tempo MIDI lookup dictionaries
        self.section_midis = self._init_section_midis()
        self.tempo_midis = self._init_tempo_midis()

        self._build_cache()

    def _init_section_midis(self):
        """Initialize Section MIDI dictionary"""
        return {
            "Intro 1": 0x00,
            "Intro 2": 0x01,
            "Intro 3": 0x02,
            "Intro 4": 0x03,
            "Main A": 0x08,
            "Main B": 0x09,
            "Main C": 0x0A,
            "Main D": 0x0B,
            "Fill In A": 0x10,
            "Fill In B": 0x11,
            "Fill In C": 0x12,
            "Fill In D": 0x13,
            "Break": 0x18,
            "Ending 1": 0x20,
            "Ending 2": 0x21,
            "Ending 3": 0x22,
            "Ending 4": 0x23,
            "Start/Stop" : 0x00     # Special case coded to toggle between to messages 
        }

    def _init_tempo_midis(self):
        """Initialize Tempo MIDI dictionary"""
        return {
            "Tempo Up": 0x00,
            "Tempo Down": 0x01,
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

                    midi_value = self.section_midis.get(midi_key, 0)

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
#     Note: Not used in the Genos yet
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
        """Validate MIDI command against known commands.
           To do: Rework since one one midi table unlike EVM Tab and Pedals"""
        if midi_type == MIDIType.PRI:
            return command in self.key_cache.section_midis
        else:
            return command in self.key_cache.section_midis

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
        self.labels[6].text = "KNOB MODE: TEMPO"
        self.labels[9].text = "Version: {}".format(self.config.version)

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
        self.tempo_flag = 0

        self.startstop = False

        self.rotor_flag = 0  # -1=slow, 0=off, 1=fast

        # Timing
        self.tempo_start_time = 0
        self.rotor_start_time = 0
        self.volume_start_time = 0
        self.version_start_time = 0
        self.led_start_time = 0

        # Preset version display to end after 15s
        self.version_start_time = time.time()

        # LED state
        self.lit_keys = [False] * 12

    def update_encoder_mode(self, new_mode):
        """Update encoder mode with timed reset"""
        self.encoder_mode = new_mode
        current_time = time.time()

        if new_mode == EncoderMode.ROTOR:
            self.rotor_start_time = current_time
        elif new_mode == EncoderMode.VOLUME:
            self.volume_start_time = current_time
        elif new_mode == EncoderMode.VALUE:
            self.value_start_time = current_time

    def check_timeouts(self):
        """Check and handle encoder mode timeouts"""
        current_time = time.time()

        # Revert rotor to tempo after timeout
        if (self.encoder_mode == EncoderMode.ROTOR and
            self.rotor_start_time != 0 and
            current_time - self.rotor_start_time > self.config.rotor_timer):
            self.encoder_mode = EncoderMode.TEMPO
            return "timeout_rotor"

        # Revert volume to rotor after timeout
        if (self.encoder_mode == EncoderMode.VOLUME and
            self.volume_start_time != 0 and
            current_time - self.volume_start_time > self.config.volume_timer):
            self.encoder_mode = EncoderMode.TEMPO
            return "timeout_volume"

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

        # Load configuration: 
        # To do: Skip in GENOS for now and adjust when needed
        #config_loaded = self.config_handler.load_config()

        #if not config_loaded:
        #    self.display.update_text(9, "Config File Error!")

        # Initialize display
        self.display = DisplayManager(self.macropad, self.config)

        # Initialize pixels
        self._preset_pixels()

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

    def _preset_pixels(self):
        """Set pixel colors based on configuration"""
        for pixel in range(12):
            if self.config_handler.config_error:
                self.macropad.pixels[pixel] = Colors.RED
            # elif pixel == self.config.get_key(VARIATION_KEY):  # Variation key
            #    if self.state.encoder_mode == EncoderMode.TEMPO:
            #        self.macropad.pixels[pixel] = Colors.YELLOW
            #    elif self.state.encoder_mode == EncoderMode.VOLUME:
            #        self.macropad.pixels[pixel] = Colors.PURPLE
            #    elif self.state.encoder_mode == EncoderMode.VALUE:
            #        self.macropad.pixels[pixel] = Colors.WHITE
            #    else:
            #        self.macropad.pixels[pixel] = self.key_cache.macropad_color_map[pixel]
            else:
                self.macropad.pixels[pixel] = self.key_cache.macropad_color_map[pixel]

            self.state.lit_keys[pixel] = False

    def _handle_key_press(self, key_number):
        """Handle key press events"""
        key_id = self.config.get_key(key_number)
        lookup_key, midi_key, midi_value = self.key_cache.get_key_midi(key_id)

        # Send MIDI command
        # Handle GENOS Start/Stop special case
        if midi_key == "Start/Stop":
            self.state.startstop = not self.state.startstop
            self.midi_handler.send_startstop_sysex(self.state.startstop)
 
        # To do: rework as no secondary table avilable as on the EVM
        elif lookup_key == MIDIType.PRI:
            self.midi_handler.send_section_sysex(midi_value)
        else:
            self.midi_handler.send_section_sysex(midi_value)

        # Update display
        self.display.update_text(3, "BUTTON: {}".format(midi_key))

        # Update LEDs
        self._preset_pixels()
        self.state.lit_keys[self.config.get_key(key_number)] = True
        self.state.led_start_time = time.time()

        return midi_key

    def _handle_encoder_change(self, direction):
        """Handle encoder rotation"""        
        self.state.encoder_sign = not self.state.encoder_sign
        current_time = time.time()

        if self.state.encoder_mode == EncoderMode.TEMPO:
            self._process_tempo(direction)
        # elif self.state.encoder_mode == EncoderMode.ROTOR:
        #     self._process_rotor(direction)
        #     self.state.rotor_start_time = current_time
        # elif self.state.encoder_mode == EncoderMode.VOLUME:
        #     self._process_volume(direction)
        #     self.state.volume_start_time = current_time

    def _process_rotor(self, direction):
        """Process rotor fast/slow commands"""
        if direction == 1 and self.state.rotor_flag != 1:
            midi_value = self.key_cache.tempo_midis["ROTOR_FAST"]
            self.display.update_text(3, "KNOB: Rotor Fast")
            self.state.rotor_flag = 1
            self.midi_handler.send_sec_sysex(midi_value)
        elif direction == -1 and self.state.rotor_flag != -1:
            midi_value = self.key_cache.tempo_midis["ROTOR_SLOW"]
            self.display.update_text(3, "KNOB: Rotor Slow")
            self.state.rotor_flag = -1
            self.midi_handler.send_sec_sysex(midi_value)

    def _process_tempo(self, direction):
        """Process tempo up/down commands"""
        sign = "+" if self.state.encoder_sign else ""
        if direction == 1:
            self.display.update_text(3, "KNOB: Tempo Up{}".format(sign))
        else:
            sign = "-" if self.state.encoder_sign else ""
            self.display.update_text(3, "KNOB: Tempo Down{}".format(sign))

        self.midi_handler.send_tempo_sysex(direction)

    def _process_volume(self, direction):
        """Process volume up/down commands"""
        sign = "+" if self.state.encoder_sign else ""
        if direction == 1:
            self.display.update_text(3, "KNOB: Volume Up{}".format(sign))
        else:
            self.display.update_text(3, "KNOB: Volume Down{}".format(sign))

        self.midi_handler.send_master_volume(direction)

    def _handle_encoder_switch(self):        
        """Handle encoder switch press. Modes 0:Rotor, 1:Tempo, 2:Volume, 3:Dial (disabled). 
           For now only Tempo supported.
           To do: Cleanup or add more modes on encoder."""
        no_modes_supported = 0
        self.state.encoder_mode = self.state.encoder_mode + 1
        if self.state.encoder_mode > no_modes_supported: 
            self.state.encoder_mode =  EncoderMode.TEMPO
        current_time = time.time()

        if self.state.encoder_mode == EncoderMode.TEMPO:
            self.display.update_text(3, "KNOB: -")
            self.display.update_text(6, "KNOB MODE: Tempo")
        # elif self.state.encoder_mode == EncoderMode.ROTOR:
        #     self.display.update_text(3, "KNOB: -")
        #     self.display.update_text(6, "KNOB MODE: *Rotor")
        #     self.state.rotot_start_time = current_time
        # elif self.state.encoder_mode == EncoderMode.VOLUME:
        #     self.display.update_text(3, "KNOB: -")
        #     self.display.update_text(6, "KNOB MODE: *Volume")
        #     self.state.volume_start_time = current_time

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
                # self.macropad.encoder_switch_debounced.update()
                # if self.macropad.encoder_switch_debounced.pressed:
                #     self._handle_encoder_switch()

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

