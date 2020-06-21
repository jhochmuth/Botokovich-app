from fastai.text import *

from fastapi import Body, FastAPI

import music21

import numpy as np

from starlette.middleware.cors import CORSMiddleware


app = FastAPI()


learner = load_learner(path='../data/', file='models/model.pkl')


# TODO: Change origin to real domain to reject Ajax requests from elsewhere
app.add_middleware(CORSMiddleware, allow_origins=['*'])


@app.post('/generate')
def generate_music(xml: str = Body(...)):
    seq = extract_note_encoding(xml)
    generated_seq = generate(learner, seq, 100)
    generated_xml = convert_seq_to_xml(generated_seq)
    return {'data': generated_xml}


def extract_chord_encodingv2(xml, steps_per_quarter=12):
    """Uses music21 library to extract chords at each timestep."""
    stream = music21.converter.parse(xml, format='musicxml')
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
def extract_note_encoding(xml):
    """Function to extract notewise encoding. This version specifies when notes are stopped."""
    chord_sequence = extract_chord_encodingv2(xml)
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


def generate(learner, start, beats_length):
    if not start.startswith('xxbox'):
        start = "xxbos " + start
    np.random.seed()
    return learner.predict(start, n_words=beats_length * 12)


def create_note(pitch, offset, duration):
    duration = music21.duration.Duration(duration)
    note = music21.note.Note(pitch, duration=duration)
    note.offset = offset
    return note


# Sometimes words like 'stop41stop41stop41' are generated.
def convert_seq_to_xml(sequence, step_size=(1/4), max_length=2):
    sequence = sequence.split(" ")
    notes = list()
    current_notes = list()
    steps = 0

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

    piano = music21.instrument.fromString("Piano")
    notes.insert(0, piano)
    stream = music21.stream.Stream(notes)
    """
    import pygame
    stream.write(fmt="midi", fp="blah.mid")
    pygame.init()
    pygame.mixer.music.load("blah.mid")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.wait(1)
    """
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
    generated = generated[:part_index] + part_tags + generated[part_index:]

    return generated
