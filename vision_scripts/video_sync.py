import os, subprocess
from glob import glob

clip_list = glob('*mp3')
ref_clip_index = 0
ref_clip = clip_list[ref_clip_index]
clip_list.pop(ref_clip_index)

results = []
results.append((ref_clip, 0))

for clip in clip_list:
    command = "Praat crosscorrelate.praat ref.mp3 {}".format(clip)
    result = subprocess.check_output(command, shell = True)
    results.append((clip, result.split("\n")[0]))
    
