from pathlib import PurePath
import os
import speech_recognition as sr

segments = ['segment1','segment2']
segment_path = 'segments/'

pathed_segments = [segment_path + segments for segments in segments]

# print all in the list separated by newline
print("Debug: I am in segments and I have:")
print(*pathed_segments, sep = "\n")

def speech_to_text(pathed_segments):
    # initialize the recognizer
    r = sr.Recognizer()

    # print all in the list separated by newline
    print("Debug: I am in stt function and I have")
    print(*pathed_segments, sep = "\n")

    # assign sum_result
    sum_result = []
    text = ""

    # loop the process for all segmented files
    for i in pathed_segments:
        text = text + i
        sum_result.append(text)
        text = ""

    sum_result = ' '.join(sum_result)
    print("Debug: I am in stt function and sum result is " + str(sum_result))

    return sum_result

sum_result = speech_to_text(pathed_segments)
print(str(sum_result))
