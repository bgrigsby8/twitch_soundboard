import mido
import numpy as np
import sounddevice as sd
import soundfile as sf
from pedalboard import (
    Chorus, Clipping, Convolution, Distortion, LadderFilter, Pedalboard,
    Resample, Reverb, PitchShift
)
from pedalboard.io import AudioStream

INPUT_DEVICE = "External Microphone"
OUTPUT_DEVICE = "External Headphones"

# MIDI note-to-sound mapping
SOUNDS = {
    40: "ImperialMarch60.wav",  # Pad 5
}

# MIDI control-to-effect mapping
KNOB_EFFECTS = {
    70: "reverb",
    71: "pitch",
    38: "distortion",
    39: "resample",
    40: "chorus",
    41: "clipping",
    42: "convolution",
    43: "ladder",
}

# Default effect values
EFFECT_VALUES = {effect: 0 for effect in KNOB_EFFECTS.values()}

# Create pedalboard and effect instances
board = Pedalboard()
reverb = Reverb()
pitch_shift = PitchShift()
distortion = Distortion()
resample = Resample(target_sample_rate=2000)
chorus = Chorus()
clipping = Clipping()
convolution = Convolution(impulse_response_filename="lyd3_000_ortf_48k.wav")
ladder = LadderFilter(mode=LadderFilter.Mode.LPF12, resonance=0.5, drive=10)

# Audio stream configuration
SAMPLE_RATE = 44100
BUFFER_SIZE = 1024

# Helper function to update effects dynamically
def update_effects(effect_name, value):
    EFFECT_VALUES[effect_name] = value
    print(f"Setting {effect_name} to {value}")

    if effect_name == "reverb":
        if value > 0.0:
            if reverb not in board:
                board.append(reverb)
            reverb.room_size = value
        elif reverb in board:
            board.remove(reverb)

    elif effect_name == "pitch":
        if value > 0.0:
            if pitch_shift not in board:
                board.append(pitch_shift)
            pitch_shift.semitones = value * 72  # Scale to +/-12 semitones
        elif pitch_shift in board:
            board.remove(pitch_shift)

    elif effect_name == "distortion":
        if value > 0.0:
            if distortion not in board:
                board.append(distortion)
            distortion.drive_db = value * 1000
        elif distortion in board:
            board.remove(distortion)

    elif effect_name == "resample":
        if value > 0.0:
            if resample not in board:
                board.append(resample)
        elif resample in board:
            board.remove(resample)

    elif effect_name == "chorus":
        if value > 0.0:
            if chorus not in board:
                board.append(chorus)
            chorus.feedback = value
        elif chorus in board:
            board.remove(chorus)

    elif effect_name == "clipping":
        if value > 0.0:
            if clipping not in board:
                board.append(clipping)
            clipping.threshold_db = value * -24
        elif clipping in board:
            board.remove(clipping)

    elif effect_name == "convolution":
        if value > 0.0:
            if convolution not in board:
                board.append(convolution)
        elif convolution in board:
            board.remove(convolution)

    elif effect_name == "ladder":
        if value > 0.0:
            if ladder not in board:
                board.append(ladder)
            ladder.drive = value * 10 + 1
        elif ladder in board:
            board.remove(ladder)

    print(f"Current effects in pedalboard: {[type(effect).__name__ for effect in board]}")

# Function to play sound using Pedalboard
def play_sound(filename, stream):
    # Read audio file
    audio, samplerate = sf.read(filename, dtype="float32")

    # Ensure it's stereo (2 channels)
    if len(audio.shape) == 1:
        audio = np.stack((audio, audio), axis=1)
    
    # Resample if necessary
    if samplerate != SAMPLE_RATE:
        print(f"Resampling audio from {samplerate} Hz to {SAMPLE_RATE} Hz")
        audio = librosa.resample(audio.T, orig_sr=samplerate, target_sr=SAMPLE_RATE).T
        samplerate = SAMPLE_RATE

    # Process the audio with the current effects chain
    processed_audio = board(audio, samplerate)

    # Write the processed audio to the stream
    stream.write(audio=processed_audio, sample_rate=samplerate)

# Main processing loop
with AudioStream(
    input_device_name=INPUT_DEVICE,
    output_device_name=OUTPUT_DEVICE,
) as stream:
    stream.plugins = board
    print("Opened audio stream with pedalboard effects.")

    input_port_name = mido.get_input_names()[0]
    with mido.open_input(input_port_name) as inport:
        print(f"Opened MIDI input port: {input_port_name}")
        try:
            for msg in inport:
                print(msg)

                if msg.type == "note_on" and msg.velocity > 0:
                    if msg.note in SOUNDS:
                        play_sound(SOUNDS[msg.note], stream)

                elif msg.type == "control_change" and msg.control in KNOB_EFFECTS:
                    effect_name = KNOB_EFFECTS[msg.control]
                    effect_value = msg.value / 127.0
                    update_effects(effect_name, effect_value)

        except KeyboardInterrupt:
            print("Streaming stopped.")
