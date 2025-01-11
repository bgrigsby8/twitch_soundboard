from pyo import *
import mido
import mido.backends.rtmidi
import json
import os
import signal

# Hardcoded macOS-specific path for the configurations.json file
CONFIG_FILE = os.path.expanduser(
   "~/Documents/twitch-soundboard/configurations.json" #"~/Library/Containers/com.example.twitchSoundboard/Data/Documents/configurations.json"
)
print("Path:", os.getcwd())

# Ignore gui errors
import os
os.environ['PYOFXGUI'] = 'no'

# Function to get available audio devices
def get_audio_devices():
    devices = pa_get_devices_infos()
    input_devices = devices[0]  # Input devices
    output_devices = devices[1]  # Output devices
    return input_devices, output_devices

# Match device name from JSON with available devices and return device ID
def get_device_id(device_name, devices):
    for device_id, device_info in devices.items():
        if device_info["name"] == device_name:
            return device_id
    print(f"Device '{device_name}' not found.")
    return None

# Load configurations from the JSON file
def load_configurations():
    if not os.path.exists(CONFIG_FILE):
        print(f"Configuration file {CONFIG_FILE} not found.")
        return {}

    with open(CONFIG_FILE, "r") as f:
        try:
            config = json.load(f)
            print(f"Loaded configuration: {config}")
            return config
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON file: {e}")
            return {}

configurations = load_configurations()

# Get user-specified input/output device names from the JSON configuration
user_input_device = configurations.get("input_device", None)
user_output_device = configurations.get("output_device", None)

# Fetch available audio devices
input_devices, output_devices = get_audio_devices()

# Resolve device IDs based on names
input_device_id = get_device_id(user_input_device, input_devices) if user_input_device else 0
output_device_id = get_device_id(user_output_device, output_devices) if user_output_device else 1

print(f"Using input device: {input_device_id}")
print(f"Using output device: {output_device_id}")

# Initialize the server
s = Server()
s.setInputDevice(0)  # Microphone
s.setOutputDevice(1)  # Default output
s.setIchnls(1)
s.setNchnls(1)
s.deactivateMidi()
s.boot()
s.start()

# Initialize microphone input
mic = Input().out()

# Helper functions for effects
effects = {
    "reverb": Freeverb(mic, size=1.0).stop(),
    "harmonizer": Harmonizer(mic, mul=5, transpo=0).stop(),
    "freq_shift": FreqShift(mic).stop(),
    "chorus": Chorus(mic, depth=5, feedback=0.5, bal=0.0).stop(),
    "distortion": Disto(mic, drive=0.0, slope=0.5).stop(),
    "delay": Delay(mic, delay=0.5, feedback=0.5, maxdelay=1.0).stop(),
}

def update_effects(control, value):
    # Check if the control is mapped to an effect
    control_mapping = configurations.get(str(control))
    if control_mapping and "effect" in control_mapping:
        effect_name = control_mapping["effect"]
        if effect_name in effects:
            effect = effects[effect_name]
            if value <= 2 and effect.isPlaying():
                effect.stop()
            elif value > 2:
                # Dynamically adjust effect parameters based on control and value
                if effect_name == "reverb":
                    effect.setSize(value / 127.0)
                elif effect_name == "harmonizer":
                    effect.setTranspo((value / 127.0) * -14)
                elif effect_name == "freq_shift":
                    effect.setShift((value / 127.0) * 500)
                elif effect_name == "distortion":
                    effect.setDrive(value / 127.0)
                    effect.setSlope((value / 127.0) - 0.25)
                elif effect_name == "delay":
                    effect.setDelay((value / 127.0) * 5)
                effect.out()

# Function to play sound files
sounds = {}

def initialize_sounds():
    for note, config in configurations.items():
        if "sound" in config:
            sound_path = "/Users/brad.grigsby/Documents/twitch-soundboard/" + config["sound"]
            if os.path.exists(sound_path):
                sounds[int(note)] = SfPlayer(sound_path, loop=False).stop()
            else:
                print(f"Sound file {sound_path} not found for note {note}.")

initialize_sounds()

def play_sound(note):
    if note in sounds:
        sound = sounds[note]
        if sound.isPlaying():
            sound.stop()
        else:
            sound.out()

# Graceful shutdown handler
def shutdown(signum, frame):
    print("Shutting down server and MIDI...")
    s.stop()
    s.shutdown()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

try:
    # MIDI handling
    try:
        input_port_name = mido.get_input_names()[0]
    except IndexError:
        print("No MIDI input ports found.")
        sys.exit(1)
    with mido.open_input(input_port_name) as inport:
        print(f"Opened MIDI input port: {input_port_name}")
        for msg in inport:
            if msg.type == "note_on" and msg.velocity > 0:
                play_sound(msg.note)

            elif msg.type == "control_change" and msg.value > 0:
                update_effects(msg.control, msg.value)
except KeyboardInterrupt:
    shutdown(None, None)
