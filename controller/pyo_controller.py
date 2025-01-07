from pyo import *
import mido

# Initialize the server
s = Server()
s.setInputDevice(0)  # Microphone
s.setOutputDevice(1)  # Default output
s.setIchnls(1)
s.setNchnls(1)  # Stereo output
s.deactivateMidi()
s.boot()
s.start()

# Audio input and effects chain
mic_input = Input().out()

# Define effects
reverb = Freeverb(mic_input, size=1.0).stop()
harmonizer = Harmonizer(mic_input, mul=5, transpo=0).stop()
freq_shift = FreqShift(mic_input).stop()
chorus = Chorus(mic_input, depth=5, feedback=0.5, bal=0.0).stop()
distortion = Disto(mic_input, drive=0.0, slope=0.5).stop()

# Helper function to dynamically update effects
def update_effects(control, value):
    if control == 70:
        if reverb.isPlaying() and value <= 2:
            reverb.stop()
        elif value > 2:
            reverb.setSize(value / 127.0)
            reverb.out()
    if control == 71:
        if harmonizer.isPlaying() and value <= 2:
            harmonizer.stop()
        elif value > 2:
            #harmonizer.setTranspo((value / 127.0) * -14)
            harmonizer.out()
    if control == 72:
        if freq_shift.isPlaying() and value <= 2:
            freq_shift.stop()
        elif value > 2:
            freq_shift.setShift((value / 127.0) * 500)
            freq_shift.out()
    if control == 73:
        if distortion.isPlaying() and value <= 2:
            distortion.stop()
        else:
            distortion.setDrive(value / 127.0)
            distortion.setSlope((value / 127.0) - 0.25)
            distortion.out()
    if control == 74:
        if reverb.isPlaying() and value <= 2:
            reverb.stop()
        else:
            reverb.setSize(value / 127.0)
            reverb.out()
    if control == 75:
        if reverb.isPlaying() and value <= 2:
            reverb.stop()
        else:
            reverb.setSize(value / 127.0)
            reverb.out()
    if control == 76:
        if reverb.isPlaying() and value <= 2:
            reverb.stop()
        else:
            reverb.setSize(value / 127.0)
            reverb.out()
    if control == 77:
        if reverb.isPlaying() and value <= 2:
            reverb.stop()
        else:
            reverb.setSize(value / 127.0)
            reverb.out()

# Function to play sound files
sound_36 = SfPlayer("sounds/alexis-mateo-bam.mp3", loop=False).stop()
sound_37 = SfPlayer("sounds/drag-race-shade-sound.mp3", loop=False).stop()
sound_38 = SfPlayer("sounds/hannah-montana-transition.mp3", loop=False).stop()
sound_39 = SfPlayer("sounds/icarly-cheers.mp3", loop=False).stop()
sound_40 = SfPlayer("sounds/m-e-o-w.mp3", loop=False).stop()
sound_41 = SfPlayer("sounds/meme-okay-lets-go.mp3", loop=False).stop()
sound_42 = SfPlayer("sounds/obamna_zq2fl9r.mp3", loop=False).stop()
sound_43 = SfPlayer("sounds/oh-thats-not.mp3", loop=False).stop()

def play_sound(sound_num):
    if sound_num == 36:
        if sound_36.isPlaying():
            sound_36.stop()
        else:
            sound_36.out()
    if sound_num == 37:
        if sound_37.isPlaying():
            sound_37.stop()
        else:
            sound_37.out()
    if sound_num == 38:
        if sound_38.isPlaying():
            sound_38.stop()
        else:
            sound_38.out()
    if sound_num == 39:
        if sound_39.isPlaying():
            sound_39.stop()
        else:
            sound_39.out()
    if sound_num == 40:
        if sound_40.isPlaying():
            sound_40.stop()
        else:
            sound_40.out()
    if sound_num == 41:
        if sound_41.isPlaying():
            sound_41.stop()
        else:
            sound_41.out()
    if sound_num == 42:
        if sound_42.isPlaying():
            sound_42.stop()
        else:
            sound_42.out()
    if sound_num == 43:
        if sound_43.isPlaying():
            sound_43.stop()
        else:
            sound_43.out()

# MIDI handling
input_port_name = mido.get_input_names()[0]
with mido.open_input(input_port_name) as inport:
    print(f"Opened MIDI input port: {input_port_name}")
    try:
        for msg in inport:
            if msg.type == "note_on" and msg.velocity > 0:
                play_sound(msg.note)

            elif msg.type == "control_change" and msg.value > 0:
                update_effects(msg.control, msg.value)

    except KeyboardInterrupt:
        print("Streaming stopped.")