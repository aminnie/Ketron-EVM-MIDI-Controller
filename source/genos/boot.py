import supervisor

import board
import digitalio
import storage

# Turn off the status bar if you haven’t already
supervisor.status_bar.display = False

# Then blank the entire display
supervisor.runtime.display.root_group = None

# Disable the USB Drive of Genos keyboards
# Set up a button connected to the specified pin (e.g., GP0)
# Disable the USB drive unless the button is pressed on boot
button = digitalio.DigitalInOut(board.KEY1)
button.pull = digitalio.Pull.UP
if button.value:
    storage.disable_usb_drive()
    
