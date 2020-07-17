import json
import mido
import mido.backends.rtmidi
import os
import rtmidi
import time


def load_config():
    try:
        config_file = os.environ['MIDI_STABILIZER_CONFIG']
    except KeyError:
        raise Exception('Please set MIDI_STABILIZER_CONFIG environment variable to point to your config file')
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config


def detect_input_port(base_name):
    input_names = midi_in.get_ports()
    for name in input_names:
        if base_name in name:
            in_port = mido.open_input(name)
            return in_port
    return None


def detect_output_port(base_name):
    output_names = midi_out.get_ports()
    for name in output_names:
        if base_name in name:
            out_port = mido.open_output(name)
            return out_port
    return None


def connect_input_port(base_name, wait_time):
    global in_port
    print('Attempting to connect to input port')
    in_port = None
    while in_port is None:
        try:
            in_port = detect_input_port(base_name)
        except:
            pass
        time.sleep(0.1)


def connect_output_port(base_name, wait_time):
    global out_port
    print('Attempting to connect to stabilizer port')
    out_port = None
    while out_port is None:
        try:
            out_port = detect_output_port('Stabilizer')
        except:
            pass
        time.sleep(0.1)


def disconnected(msg):
    return msg.type == 'control_change' and msg.channel == 2 and msg.control == 121


if __name__ == '__main__':
    config = load_config()
    ports = config['MIDI Ports']
    times = config['Sleep Times']

    midi_in = rtmidi.MidiIn()
    midi_out = rtmidi.MidiOut()

    connect_input_port(ports['input'], times['connect'])
    connect_output_port(ports['output'], times['connect'])

    print('Connections established')

    while True:
        for msg in in_port.iter_pending():
            if disconnected(msg):
                out_port.reset()
                connect_input_port(ports['input'], times['connect'])
                print('Successfully reconnected')
            out_port.send(msg)
        time.sleep(times['main'])