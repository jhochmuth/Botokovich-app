import music21

import py_midicsv as midi


KEY_TRANSPOSITION_VALUES = {0: 0,
                            1: 5,
                            2: -2,
                            3: 3,
                            4: -4,
                            5: 1,
                            6: -6,
                            -1: -5,
                            -2: 2,
                            -3: -3,
                            -4: 4,
                            -5: -1,
                            -6: -3}


def midi_command_formatting(command):
    """Converts a string containing a midi command to an array."""
    command = command.strip("\n")
    command = command.split(", ")
    return command


def midi_to_csv(filename):
    """Extracts all commands from a midi file and converts them to array format."""
    csv = midi.midi_to_csv(filename)
    return [midi_command_formatting(command) for command in csv]


def get_transposition_value(midi_command_list):
    transposition_value = None

    for command in midi_command_list:
        if command[2] == "Key_signature":
            transposition_value = KEY_TRANSPOSITION_VALUES[int(command[3])]
            break

    if not transposition_value:
        transposition_value = 0

    return transposition_value


def extract_note_values(midi_command_list):
    transposition_value = get_transposition_value(midi_command_list)
    return [int(command[4]) + transposition_value for command in midi_command_list
            if command[2] == "Note_on_c" and int(command[5]) > 0 and int(command[3]) == 0]


def extract_notes_from_file(filename):
    midi_command_list = midi_to_csv(filename)
    return extract_note_values(midi_command_list)


def extract_chord_encodingv2(midi, steps_per_quarter=12):
    """Uses music21 library to extract chords at each timestep."""
    converter = music21.converter.Converter()
    stream = converter.parseData(midi)
    time_steps = [list() for _ in range(int(stream.duration.quarterLength * steps_per_quarter))]

    for element in stream.recurse(classFilter=('Chord', 'Note')):
        time = int(element.offset * steps_per_quarter)
        duration_steps = int(element.duration.quarterLength * steps_per_quarter)

        if isinstance(element, music21.note.Note):
            for duration in range(duration_steps):
                if time + duration > len(time_steps) - 1:
                    break
                elif element.pitch.ps < 36 or element.pitch.ps > 96:
                    continue
                elif duration == 0:
                    time_steps[time + duration].append((int(element.pitch.ps), 1))
                else:
                    time_steps[time + duration].append((int(element.pitch.ps), 2))

        elif isinstance(element, music21.chord.Chord):
            for duration in range(duration_steps):
                if time + duration > len(time_steps) - 1:
                    break
                for note in element.pitches:
                    if note.ps < 36 or note.ps > 96:
                        continue
                    elif duration == 0:
                        time_steps[time + duration].append((int(note.ps), 1))
                    else:
                        time_steps[time + duration].append((int(note.ps), 2))

    chord_sequence = list()
    for step in time_steps:
        chord = ["0" for _ in range(61)]
        for note in step:
            chord[note[0] - 36] = str(note[1])
        chord_sequence.append("".join(chord))
    chord_sequence = " ".join(chord_sequence)
    return chord_sequence


# TODO: Check the effects of repeated notes. Important for ensemble pieces.
def extract_note_encoding(midi):
    """Function to extract notewise encoding. This version specifies when notes are stopped."""
    chord_sequence = extract_chord_encodingv2(midi)
    chord_sequence = chord_sequence.split(" ")
    note_sequence = ""

    current_notes = set()
    for chord in chord_sequence:
        stopped_notes = set()
        for note_index in current_notes:
            if chord[note_index] == "0":
                stopped_notes.add(note_index)
                note_sequence = "{} stop{}".format(note_sequence, str(note_index))
        for note_index in stopped_notes:
            current_notes.remove(note_index)
        for i, char in enumerate(chord):
            if char == "1":
                note_sequence = "{} {}".format(note_sequence, str(i))
                current_notes.add(i)
        note_sequence = "{} step".format(note_sequence)

    return note_sequence
