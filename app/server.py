from fastai.text import *

from fastapi import Body, FastAPI

import flat_api
from flat_api.rest import ApiException

import music21

import numpy as np

from starlette.middleware.cors import CORSMiddleware

# Code for authentication in Flat API if needed later.
"""
flat_config = flat_api.Configuration()
flat_config.access_token = None
flat_api_client = flat_api.ApiClient(flat_config)
#flat_api_instance = flat_api.AccountApi(flat_api_client)
score_api_instance = flat_api.ScoreApi(flat_api_client)
"""

# Code for creating a new score in Flat API if needed later.
"""
privacy = flat_api.ScorePrivacy()
score_creation = flat_api.ScoreCreation(privacy='public',
data=generated_mus)
score_creation.title = 'New Generated Piece'

try:
api_response = score_api_instance.create_score(score_creation)
print(api_response)
except ApiException as e:
print("Exception when calling ScoreApi->create_score: %s\n" % e)
"""


app = FastAPI()


learner = load_learner(path='../data/', file='models/model.pkl')


# TODO: Change origin to real domain to reject Ajax requests from elsewhere
app.add_middleware(CORSMiddleware, allow_origins=['*'])


@app.post('/generate')
def generate_music(xml: str = Body(...), length: int = Body(...)):
    """Does all work to generate music using user input.
       Converts musicxml-based user input to a notewise encoding.
       Then uses this to seed the trained neural network.
       Finally converts the generated sequence to musicxml and sends this to the client."""
    seq = extract_note_encoding(xml)
    generated_seq = generate(learner, seq, length)
    generated_mus = convert_seq_to_xml(generated_seq)
    return {'data': generated_mus}


def extract_chord_encodingv2(xml, steps_per_quarter=12):
    """Uses music21 library to extract chords at each timestep."""
    stream = music21.converter.parse(xml, format='musicxml')
    
    # First create the list of timesteps which contains information about every note that is playing at that moment.
    time_steps = [list() for _ in range(int(stream.duration.quarterLength * steps_per_quarter))]
    
    # Iterate over all chords and notes.
    for element in stream.recurse(classFilter=('Chord', 'Note')):
        time = int(element.offset * steps_per_quarter)
        duration_steps = int(element.duration.quarterLength * steps_per_quarter)
        
        # Notes and chords must be treated differently.
        if isinstance(element, music21.note.Note):
            for duration in range(duration_steps):
                # Stop if we have gone over the total number of time steps.
                if time + duration > len(time_steps) - 1:
                    break
                # Do nothing if this note is out of range.
                elif element.pitch.ps < 36 or element.pitch.ps > 96:
                    continue
                # If the duration of this note is 0, the note is ending
                elif duration == 0:
                    time_steps[time + duration].append((int(element.pitch.ps), 1))
                else:
                    time_steps[time + duration].append((int(element.pitch.ps), 2))

        elif isinstance(element, music21.chord.Chord):
            # If there is a chord, we must individually iterate over all notes in that chord.
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

    # We can now generate the list of chord sequences at every timesteps.
    # Every timestep will be comprised of 61 digits. Each digit represents a note between C3 and C8.

    chord_sequence = list()
    for step in time_steps:
        chord = ["0" for _ in range(61)]
        for note in step:
            chord[note[0] - 36] = str(note[1])
        chord_sequence.append("".join(chord))
    return chord_sequence


# TODO: Check the effects of repeated notes. Important for ensemble pieces.
# TODO: Adjust algorithm to use lists instead of strings because string concatenation is O(n).
def extract_note_encoding(xml):
    """Function to extract notewise encoding. This version specifies when notes are stopped.
       An example of a notewise sequences is '12 24 step step step stop12 stop24'."""
    # First extract chordwise sequence.
    chord_sequence = extract_chord_encodingv2(xml)
    note_sequence = ""
    
    # Use chordwise sequences to generate notewise sequence.
    # Use a set to keep track of all notes that are currently sounding.
    current_notes = set()
    for chord in chord_sequence:
        stopped_notes = set()
        for note_index in current_notes:
            # If a note that was previously sounding is now a 0, it has stopped playing.
            # Append a command that signifies this note has stopped playing.
            if chord[note_index] == "0":
                stopped_notes.add(note_index)
                note_sequence = "{} stop{}".format(note_sequence, str(note_index))
        # Remove all stopped notes from currently sounding notes.
        for note_index in stopped_notes:
            current_notes.remove(note_index)
        # For all notes that are have just started sounding at this timestep, append a command that signifies that the note has started playing.
        for i, char in enumerate(chord):
            if char == "1":
                note_sequence = "{} {}".format(note_sequence, str(i))
                current_notes.add(i)
        note_sequence = "{} step".format(note_sequence)

    return note_sequence


def generate(learner, start, measure_length):
    if not start.startswith('xxbox'):
        start = "xxbos " + start
    np.random.seed()
    return learner.predict(start, n_words=measure_length * 48 - 12)


def create_note(pitch, offset, duration):
    duration = music21.duration.Duration(duration)
    note = music21.note.Note(pitch, duration=duration)
    note.offset = offset
    return note


def notes_to_midi(notes):
    piano = music21.instrument.fromString("Piano")
    notes.insert(0, piano)
    stream = music21.stream.Stream(notes)
    stream.write(fmt="midi", fp="blah.mid")
    midiFileObj = music21.midi.translate.streamToMidiFile(stream)
    midi = midiFileObj.writestr()
    midi = str(midi)
    return midi


def notes_to_mxml(part1, part2):
    piano = music21.instrument.fromString("Piano")
    part1.insert(0, piano)
    part1 = music21.stream.Part(part1)
    part2 = music21.stream.Part(part2)
    stream = music21.stream.Stream()
    stream.insert(0, part1)
    stream.insert(0, part2)
    stream.write(fmt="midi", fp="/Users/juliushochmuth/Downloads/test.mid")

    exporter = music21.musicxml.m21ToXml.GeneralObjectExporter(stream)
    generated = exporter.parse(stream)
    generated = generated.decode('utf-8')

    part_index = generated.index('</score-part>')
    part_tags = """
    <score-instrument id="1234567890">
        <instrument-name>Piano</instrument-name>
        <instrument-sound>Piano</instrument-sound>
    </score-instrument>
    """
    part_tags2 = """
    <score-instrument id="1234567">
        <instrument-name>Piano</instrument-name>
        <instrument-sound>Piano</instrument-sound>
    </score-instrument>
    """
    generated = generated[:part_index] + part_tags + generated[part_index:]
    part_index2 = generated.rindex('</score-part>')
    generated = generated[:part_index2] + part_tags2 + generated[part_index2:]

    return generated


# Sometimes words like 'stop41stop41stop41' are generated.
def convert_seq_to_xml(sequence, step_size=(1/8), max_length=2):
    """This function is does the exact opposite of the function extract_note_encoding.
       It is used to convert the generated sequence to musicxml format."""
    sequence = sequence.split(" ")
    notes = list()
    current_notes = list()
    steps = 0

    part1 = list()
    part2 = list()

    for element in sequence:
        if element == "xxbos" or element == "":
            continue

        elif element == "step":
            steps += 1
            delete_notes = list()
            for i, note in enumerate(current_notes):
                note[2] += 1
                if note[2] >= max_length / step_size:
                    new_note = create_note(note[0] + 36, note[1] * step_size, note[2] * step_size)
                    notes.append(new_note)

                    if new_note.pitches[0] <= music21.pitch.Pitch('C4'):
                        part2.append(new_note)
                    else:
                        part1.append(new_note)

                    delete_notes.append(note)
            for note in delete_notes:
                current_notes.remove(note)

        elif "stop" in element:
            try:
                pitch = int(element[4:])
                current_pitches = [n[0] for n in current_notes]
                if pitch in current_pitches:
                    index = current_pitches.index(pitch)
                    note = current_notes[index]
                    new_note = create_note(note[0] + 36, note[1] * step_size, note[2] * step_size)
                    notes.append(new_note)

                    if new_note.pitches[0] <= music21.pitch.Pitch('C4'):
                        part2.append(new_note)
                    else:
                        part1.append(new_note)

                    del current_notes[index]
            except:
                continue
        else:
            try:
                pitch = int(element)
                offset_steps = steps
                current_notes.append([pitch, offset_steps, 0])
            except:
                continue

    for note in current_notes:
        new_note = create_note(note[0] + 36, note[1] * step_size, note[2] * step_size)
        notes.append(new_note)

        if new_note.pitches[0] >= music21.pitch.Pitch('C4'):
            part1.append(new_note)
        else:
            part2.append(new_note)

    return notes_to_mxml(part1, part2)
    #return notes_to_midi(notes)
