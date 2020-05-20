from flask import Flask, render_template, url_for, flash, redirect
from pytube import YouTube
from input import URLForm
import os
import time
import speech_recognition as sr
from pathlib import PurePath
from pydub import AudioSegment
import numpy
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import re
from collections import Counter
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'c35b23b2f61c6c6818caebe9bec6e1e9'

#
# TODO:
#    unittesting: https://www.youtube.com/watch?v=6tNS--WetLI&t=1036s
#    tempfiles: https://docs.python.org/3/library/tempfile.html
#    add option to result page to remove (subjects, adjectives or) custom words separated by comma
#

@app.route("/", methods=['GET', 'POST'])
def main_input():
    url = URLForm()
    if url.validate_on_submit():
        url_data = url.url.data # fetch input data
        print("submitted " + url_data)

        # download file to tmp/ and rename
        filename = download_and_rename(url_data)

        # convert from .mp4 to .wav so google understands
        new_filename = convert(filename)

        # slice in to 10s segments so google limit is overcome
        all_segments = split(new_filename)

        # speech to text
        sum_result = speech_to_text(all_segments)

        # create word cloud
        output_file = wordcloud(sum_result)

        return result(sum_result, output_file)
    return render_template('index.html', url=url)


def download_and_rename(url_data):
    yt = YouTube(url_data)
    print('I am downloading: ' + yt.title)
    os.system('pytube3 ' + url_data + ' -a -t tmp/')
    # check if tmp folder is empty or not and set path
    if len(os.listdir('tmp/')) != 0:
        print('Download successful.')

        # fetch the original filename
        orig_filename = os.listdir('tmp/')
        orig_filename = ''.join(orig_filename[0])
        print('File name is: ' + orig_filename)

        # rename file for easy life
        os.rename('tmp/' + orig_filename,'tmp/tmp.mp4')

        # set new filename to variable
        filename = os.listdir('tmp/')
        filename = ''.join(filename[0])
        print('New filename is: ' + filename)

        # set filepath
        data_folder = PurePath('tmp/')
        filepath = data_folder / filename
        filename = filepath
        print("Full path: " + str(filename))

    else:
        print('Something went wrong while downloading.')

    return filename

def convert(filename):
    # open audio file
    # print("Debug: I am in convert and I have " + str(filename))
    audio = AudioSegment.from_file(str(filename), "mp4")

    # make conversion
    audio.export("tmp/tmp.wav", format="wav")
    new_filename = "tmp.wav"

    # set filepath
    data_folder = PurePath('tmp/')
    filepath = data_folder / new_filename
    new_filename = filepath

    return new_filename

def split(new_filename):

    # set segment path
    segment_path = 'segments/'

     # since google recognize will only recognize 10 seconds we will split audio to 10s segments
    os.system('ffmpeg -i ' + str(new_filename) + ' -f segment -segment_time 10 -c copy ' + segment_path + 'segment%03d.wav')
    segments = os.listdir(segment_path)

    # set filepath for segments
    all_segments = [segment_path + segments for segments in segments]
    # print("Debug: I am in segments and I have:")

    # # print all in the list separated by newline
    # print(*all_segments, sep = "\n")

    return all_segments

def speech_to_text(all_segments):
    # initialize the recognizer
    r = sr.Recognizer()

    # print all in the list separated by newline
    # print("Debug: I am in stt function and I have")
    # print(*all_segments, sep = "\n")

    # assign sum_result
    sum_text = []
    text = ""

    # loop the process for all segmented files
    for i in all_segments:

        # open the file
        print("Starting segment " + i + " ...")
        with sr.AudioFile(i) as source:

            # listen for the data (load audio to memory)
            audio_data = r.record(source)

            try:
                # recognize (convert from speech to text)
                text = r.recognize_google(audio_data)
                sum_text.append(text)
                print("Segment " + i + " ready..")
            except sr.UnknownValueError:
                print("Google couldn't understand anything from segment " + i)
            except sr.RequestError as e:
                print("Could not request results from Google Cloud Speech service: {0}".format(e))

    print("All segments processed.")

    # create the massive text file for analysis
    sum_result = ' '.join(sum_text)
    f= open("tmp/wordcloud.txt","w+")
    f.write(sum_result)
    f.close()

    # print("Debug: I am in stt function and sum result is " + sum_result)

    return sum_result

def wordcloud(sum_result):

    words = ""
    words_counter = ""

    # initialize WordCloud
    print("Creating wordcloud ...")

    # create custom mask from vector image
    custom_mask = np.array(Image.open("static/ball.png"))

    # define wordcloud variables
    wc = WordCloud(background_color="white", mask=custom_mask, max_words=9999, width=2560, height=1700)

    # read words from a file
    words = re.findall(r'\w+', open('tmp/wordcloud.txt', encoding='utf-8').read().lower())

    # count word frequency
    words_counter = Counter(words)

    # create the wordcloud from frequency
    wc.generate_from_frequencies(words_counter)

    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.show()

    output_file = randomString(16)
    output_file = output_file + ".png"

    # output the result as image
    wc.to_file('static/' + output_file)

    return output_file

def randomString(stringLength=16):
    # generate random string for output file
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range (stringLength))

def result(sum_result, output_file):
    # cleanup
    print("Here is tmp directory:")
    print(os.listdir('tmp/'))
    print("Here are segments:")
    print(os.listdir('segments/'))
    os.system("rm tmp/* && rm segments/*")
    print('Cleaning up ...')

    if len(os.listdir('tmp/')) == 0 and len(os.listdir('segments/')) == 0:
        print('Cleanup successful.')
    else:
        print('something went wrong while cleaning up.')

    return render_template('result.html', sum_result=sum_result, output_file=output_file)

if __name__ == '__main__':
    app.run(debug=True)
