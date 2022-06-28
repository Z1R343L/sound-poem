import pygame as pg
import numpy as np
import math

pg.init()
pg.mixer.init()

def synth(frequency, duration=1.5, sampling_rate=44100, square=False):
	frames = int(duration*sampling_rate)
	arr = np.cos(2*np.pi*frequency*np.linspace(0,duration, frames))
	arr = arr + np.cos(4*np.pi*frequency*np.linspace(0,duration, frames))
	arr = arr - np.cos(6*np.pi*frequency*np.linspace(0,duration, frames))
	if square:
		arr = np.clip(arr*10, -1, 1)
	arr = arr/max(np.abs(arr))
	sound = np.asarray([32767*arr,32767*arr]).T.astype(np.int16)
	sound = pg.sndarray.make_sound(sound.copy())
	return sound

scaleList = {
	"a major": ["A", "B", "C#", "D", "E", "F#", "G#"],
	"a minor": ["A", "B", "C", "D", "E", "F", "G"],
	"b major": ["B", "C#", "D#", "E", "F#", "G#", "A#"],
	"b minor": ["B", "C#", "D", "E", "F#", "G", "A"],
	"b# major": ["C#", "D#", "F", "F#", "G#", "A#", "C"],
	"c major": ["C", "D", "E", "F", "G", "A", "B"],
	"c major 7": ["C", "E", "G", "B"],
	"c minor": ["C", "D", "D#", "F", "G", "G#", "A#"],
        "c# minor": ["C#", "D#", "E", "F#", "G#", "A", "B"],
	"d major 7": ["D", "F#", "A", "C#"],
        "d minor": ["D", "E", "F", "G", "A", "C#", "C"],
	"e major": ["E", "F#", "G#", "A", "B", "C#", "D#"],
	"e minor": ["E", "F#", "G", "A", "B", "C", "D"],
	"e minor 7": ["E", "G", "B", "D"],
	"f# major": ["F#", "G", "B", "D"],
	"g major 7": ["G", "B", "D", "F#"],
	"chromatic": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
	}
keylist = ".,' abcdefghijklmnopqrstuvwxyz"#ABCDEFGHIJKLMNOPQRSTUVWXYZ"

print("ADMITTED CHARACTERS: ", keylist)
print("Enter your text: ", end="")
text = input().lower()
if text == "":
	text = "your text goes here."
print("Enter the BPM: ", end="")
try:
	bpm = float(input())
except:
	bpm = 60
if bpm == "":
	bpm = 60
tempo = 60/bpm
print("Enter the scale range [1-3]: ", end="")
try:
	scaleRange = float(input())
except:
	scaleRange = 1
if scaleRange == "":
	scaleRange = 1
print("Enter scale/chord [e.g. C# Major, E Minor 7, C Major]: ", end="")
scaleKey = input().lower()
try:
	scale = scaleList[scaleKey]
except:
	print("(Invalid or non-added scale, picking chromatic by default)")
	scale = scaleList["chromatic"]

print(f"Enter ending grade [1-{len(scale)}]: ", end="")
try:
	endingGrade = int(input())
except:
	endingGrade = 0
if endingGrade < 1 or endingGrade > 12:
		print("(Ending grade set to 0 by default. It will not be added)")
		endingGrade = 0

print("Enter pitch [1-7]: ", end="")
try:
	pitch = int(input())
except:
	pitch = 2
if pitch < 1 or pitch > 7:
	print("(Pitch set to 2 by default)")
	pitch = 2

print("Loop [y/n]: ", end="")
loopQuery = input()
loop = loopQuery == "y"
print(text)

with open("noteslist.txt") as notes_file:
	file_contents = notes_file.read()
noteslist = file_contents.splitlines()

notesNum = {}
grade = 1
for i in range(len(keylist)):
	key = keylist[i] 
	notesNum[key] = [grade, i]
	if grade < scaleRange*12:
		grade += 1
	else:
		grade = 1

textNum = []
duration = int(tempo*500)
for i in range(len(text)):
	waiting = int(tempo*1000)
	if text[i] in [" ", ","]:
		waiting *= 1
	if text[i] == "'":
		waiting = 100
	textNum.append([notesNum[text[i]][0], duration, waiting])

melodyNotes = []

for item in textNum:
	item[0] = round(item[0] * (len(scale)/12))
	mod = 0
	j = item[0] - textNum[0][0]
	mod += math.floor(j/len(scale))
	if j >= 0:
		while abs(j) >= len(scale):
			j = len(scale)-abs(j)
	else:
		while j < 0:
			j = len(scale)+j
	melodyNotes.append([scale[abs(j)], mod, item[1], item[2]])

letterNotes = {}
freq = 16.3516
for i in range(len(noteslist)):
    mod = int(i/12)
    key = noteslist[i]
    sample = synth(freq)
    letterNotes[key] = [sample, mod, freq]
    letterNotes[key][0].set_volume(0.33)
    freq = freq * 2 ** (1/12)

def playNote(note, mod):
	print(note[0]+str(note[1]+pitch), end=" ")
	key = note[0]+str(note[1]+mod)
	letterNotes[key][0].play()
	letterNotes[key][0].fadeout(note[2])
	pg.time.wait(note[3])

def playMelody(melody, mod, signature):
	pulse = 1
	for i in range(len(melody)):
		if pulse == 1:
			melody[i][2] = int(tempo*1000)
		playNote(melody[i], mod)
		if pulse < signature:
			pulse += 1
		else:
			pulse = 1
	if endingGrade > 0 or not loop:
		endingNote = melody[0]
		endingNote[0] = scale[endingGrade-1]
		endingNote[2] *= 3
		endingNote[3] *= 4
		playNote(endingNote, mod)

if loop == False:
	playMelody(melodyNotes, pitch+2, 2)

loopCount = 0
while loop == True:
	playMelody(melodyNotes, pitch+2, 2)
	loopCount+=1
	print(loopCount)

pg.mixer.quit()
pg.quit()
