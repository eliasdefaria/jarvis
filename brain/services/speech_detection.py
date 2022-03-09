from asyncore import write
from email.mime import audio
import sounddevice as sd
import webrtcvad

import math
from numpy import average, add, byte
import time
import wave
from collections import deque
from typing import Deque


_SAMPLE_RATE = 32000
_BLOCK_SIZE = 320
_FORMAT = 'int16'


vad = webrtcvad.Vad()
audio_to_write: bytearray = bytearray()
prev_audio: Deque[bytearray] = deque(maxlen=5)
is_writing = False

def write_audio_to_file(data):
    extension = '.wav'
    filename = f'output_{str(int(time.time()))}'
    # writes data to WAV file
    # data = ''.join(data)
    wf = wave.open(f'{filename}{extension}', 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(_SAMPLE_RATE)  # TODO make this value a function parameter?
    wf.writeframes(data)
    wf.close()
    return f'{filename}.wav'

stream = sd.RawInputStream(samplerate=_SAMPLE_RATE, channels=1, dtype=_FORMAT, blocksize=_BLOCK_SIZE)
stream.start()
while True:
    data = stream.read(_BLOCK_SIZE)
    
    # print(data[0].bytes)
    print(f'Contains speech {vad.is_speech(data[0], _SAMPLE_RATE)}')
    if vad.is_speech(data[0], _SAMPLE_RATE):
        audio_to_write.extend(data[0])
    elif len(audio_to_write) > 0:
        output = bytearray()
        for audio_chunk in prev_audio:
            output.extend(audio_chunk)

        output.extend(audio_to_write)
        write_audio_to_file(output)
        print(len(audio_to_write))
        exit()
    else:
        if len(prev_audio) > 0:
            prev_audio.popleft()
            prev_audio.append(data)
        


    # slid_win.append(math.sqrt(abs(audioop.avg(cur_data, 4))))

    # if sum([x > self.THRESHOLD for x in slid_win]) > 0:
    #     if started == False:
    #         print("Starting recording of phrase")
    #         started = True
    #     audio2send.append(cur_data)

    # elif started:
    #     print("Finished recording, decoding phrase")
    #     filename = self.save_speech(list(prev_audio) + audio2send, p)
    #     r = self.decode_phrase(filename)
    #     print("DETECTED: ", r)

    #     # Removes temp audio file
    #     os.remove(filename)
    #     # Reset all
    #     started = False
    #     slid_win = deque(maxlen=self.SILENCE_LIMIT * rel)
    #     prev_audio = deque(maxlen=0.5 * rel)
    #     audio2send = []
    #     print("Listening ...")

    # else:
    #     prev_audio.append(cur_data)

# import speech_recognition as sr 
# import os
# import pyd
# import wave
# import audioop
# from collections import deque
# import time
# import math

# class SpeechDetector:
#     def __init__(self):
#         # Microphone stream config.
#         self.CHUNK = 1024 # CHUNKS of bytes to read each time from mic
#         self.FORMAT = pyaudio.paInt16
#         self.CHANNELS = 1
#         self.RATE = 16000

#         self.SILENCE_LIMIT = 1 # Silence limit in seconds. The max ammount of seconds where
#         # only silence is recorded. When this time passes the
#         # recording finishes and the file is decoded

#         self.PREV_AUDIO = 0.5 # Previous audio (in seconds) to prepend. When noise
#         # is detected, how much of previously recorded audio is
#         # prepended. This helps to prevent chopping the beginning
#         # of the phrase.

#         self.THRESHOLD = 4500
#         self.num_phrases = -1

#         # These will need to be modified according to where the pocketsphinx folder is
#         MODELDIR = 'pocketsphinx/model'
#         DATADIR = 'pocketsphinx/test/data'

#         # Create a decoder with certain model
#         config = Decoder.default_config()
#         config.set_string('-hmm', os.path.join(MODELDIR, 'en-us/en-us'))
#         config.set_string('-lm', os.path.join(MODELDIR, 'en-us/en-us.lm.bin'))
#         config.set_string('-dict', os.path.join(MODELDIR, 'en-us/cmudict-en-us.dict'))

#         # Creaders decoder object for streaming data.
#         self.decoder = Decoder(config)

#     def setup_mic(self, num_samples=50):
#         """ Gets average audio intensity of your mic sound. You can use it to get
#         average intensities while you're talking and/or silent. The average
#         is the avg of the .2 of the largest intensities recorded.
#         """
#         print ('Getting intensity values from mic.')
#         p = pyaudio.PyAudio()
#         stream = p.open(format=self.FORMAT,
#         channels=self.CHANNELS,
#         rate=self.RATE,
#         input=True,
#         frames_per_buffer=self.CHUNK)

#         values = [math.sqrt(abs(audioop.avg(stream.read(self.CHUNK), 4)))
#         for x in range(num_samples)]
#         values = sorted(values, reverse=True)
#         r = sum(values[:int(num_samples * 0.2)]) / int(num_samples * 0.2)
#         print (' Finished ')
#         print (' Average audio intensity is %s ' % r)
#         stream.close()
#         p.terminate()

#         if r self.THRESHOLD for x in slid_win]) > 0:
#             if started == False:
#                 print ('Starting recording of phrase')
#                 started = True
#                 audio2send.append(cur_data)

#             elif started:
#                 print ('Finished recording, decoding phrase')
#                 filename = self.save_speech(list(prev_audio) + audio2send, p)
#                 r = self.decode_phrase(filename)
#                 print ('DETECTED: %s' % r)

#                 # Removes temp audio file
#                 os.remove(filename)
#                 # Reset all
#                 started = False
#                 slid_win = deque(maxlen=int(self.SILENCE_LIMIT * rel))
#                 prev_audio = deque(maxlen=int(0.5 * rel))
#                 audio2send = []
#                 print ('Listening …')

#             else:
#                 prev_audio.append(cur_data)

#                 print ('* Done listening')
#                 stream.close()
#                 p.terminate()

#     def save_speech(self, data, p):
#         """
#         Saves mic data to temporary WAV file. Returns filename of saved
#         file
#         """
#         filename = 'output_'+str(int(time.time()))
#         # writes data to WAV file
#         data = ''.join(data)
#         wf = wave.open(filename + '.wav', 'wb')
#         wf.setnchannels(1)
#         wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
#         wf.setframerate(16000)  # TODO make this value a function parameter?
#         wf.writeframes(data)
#         wf.close()
#         return filename + '.wav'

#     def decode_phrase(self, wav_file):
#         self.decoder.start_utt()
#         stream = open(wav_file, "rb")
#         while True:
#           buf = stream.read(1024)
#           if buf:
#             self.decoder.process_raw(buf, False, False)
#           else:
#             break
#         self.decoder.end_utt()
#         words = []
#         [words.append(seg.word) for seg in self.decoder.seg()]
#         return words

#     def run(self):
#         """
#         Listens to Microphone, extracts phrases from it and calls pocketsphinx
#         to decode the sound
#         """
#         self.setup_mic()

#         #Open stream
#         p = pyaudio.PyAudio()
#         stream = p.open(format=self.FORMAT, 
#                         channels=self.CHANNELS, 
#                         rate=self.RATE, 
#                         input=True, 
#                         frames_per_buffer=self.CHUNK)
#         print('* Mic set up and listening.')

#         audio2send = []
#         cur_data = ''  # current chunk of audio data
#         rel = self.RATE/self.CHUNK
#         slid_win = deque(maxlen=self.SILENCE_LIMIT * rel)
#         #Prepend audio from 0.5 seconds before noise was detected
#         prev_audio = deque(maxlen=self.PREV_AUDIO * rel)
#         started = False

#         while True:
#             cur_data = stream.read(self.CHUNK)
#             slid_win.append(math.sqrt(abs(audioop.avg(cur_data, 4))))

#             if sum([x > self.THRESHOLD for x in slid_win]) > 0:
#                 if started == False:
#                     print("Starting recording of phrase")
#                     started = True
#                 audio2send.append(cur_data)

#             elif started:
#                 print("Finished recording, decoding phrase")
#                 filename = self.save_speech(list(prev_audio) + audio2send, p)
#                 r = self.decode_phrase(filename)
#                 print("DETECTED: ", r)

#                 # Removes temp audio file
#                 os.remove(filename)
#                 # Reset all
#                 started = False
#                 slid_win = deque(maxlen=self.SILENCE_LIMIT * rel)
#                 prev_audio = deque(maxlen=0.5 * rel)
#                 audio2send = []
#                 print("Listening ...")

#             else:
#                 prev_audio.append(cur_data)

#         print("* Done listening")
#         stream.close()
#         p.terminate()

# if __name__ == '__main__':
#     sd = SpeechDetector()
#     sd.run()