import time
import wave
from collections import deque
from typing import Deque
from typing_extensions import Self

import sounddevice as sd
import webrtcvad

# import speech_recognition as sr 
# import os
# import pyd
# import audioop

class SpeechDetector:
    def __init__(self: Self) -> None:
        # Microphone stream config.
        self._CHANNELS = 1
        self._SAMPLE_RATE = 32000
        self._BLOCK_SIZE = 320
        self._FORMAT = 'int16'

        self._SILENCE_LIMIT = 1 # Silence limit in seconds. When this time passes the
        # recording finishes and the file is decoded

        self._PREV_AUDIO = 0.5 # Previous audio (in seconds) to prepend. This helps to prevent 
        # chopping the beginning of the phrase.
         

    def write_audio_to_file(self: Self, data: bytearray) -> str:
        """
        Writes recorded phrase to a wav file for use in speech recognition models downstream
        """
        extension = '.wav'
        filename = f'/tmp/output_{str(int(time.time()))}'
        wf = wave.open(f'{filename}{extension}', 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(self._SAMPLE_RATE)
        wf.writeframes(data)
        wf.close()

        return f'{filename}{extension}'

    # def decode_phrase(self, wav_file):
    #     self.decoder.start_utt()
    #     stream = open(wav_file, "rb")
    #     while True:
    #       buf = stream.read(1024)
    #       if buf:
    #         self.decoder.process_raw(buf, False, False)
    #       else:
    #         break
    #     self.decoder.end_utt()
    #     words = []
    #     [words.append(seg.word) for seg in self.decoder.seg()]
    #     return words

    def run(self: Self) -> None:
        """
        Listens to Microphone, extracts speech phrases from it and calls speech recognition model
        to decode the sound
        """
        vad = webrtcvad.Vad()
        audio_to_write: bytearray = bytearray()
        prev_audio: Deque[bytearray] = deque(maxlen=5)

        stream = sd.RawInputStream(
            samplerate=self._SAMPLE_RATE, 
            channels=self._CHANNELS, 
            dtype=self._FORMAT, 
            blocksize=self._BLOCK_SIZE
        )
        stream.start()
        # TODO: Implement silence limit
        while True:
            data = stream.read(self._BLOCK_SIZE)
            raw_audio_data = data[0]

            if vad.is_speech(raw_audio_data, self._SAMPLE_RATE):
                print("Recording phrase")
                audio_to_write.extend(raw_audio_data)
            elif len(audio_to_write) > 0:
                print("Finished recording, writing audio file")
                output = bytearray()
                for audio_chunk in prev_audio:
                    output.extend(audio_chunk)

                output.extend(audio_to_write)
                filename = self.write_audio_to_file(output)

                # TODO: Read audio data from file and feed to speech recognition library
                print(len(audio_to_write))
                exit()
            else:
                if len(prev_audio) > 0:
                    prev_audio.popleft()
                    prev_audio.append(raw_audio_data)
        
        stream.close()

        #Open stream
        # p = pyaudio.PyAudio()
        # stream = p.open(format=self.FORMAT, 
        #                 channels=self.CHANNELS, 
        #                 rate=self.RATE, 
        #                 input=True, 
        #                 frames_per_buffer=self.CHUNK)
        # print('* Mic set up and listening.')

        # audio2send = []
        # cur_data = ''  # current chunk of audio data
        # rel = self.RATE/self.CHUNK
        # slid_win = deque(maxlen=self.SILENCE_LIMIT * rel)
        # #Prepend audio from 0.5 seconds before noise was detected
        # prev_audio = deque(maxlen=self.PREV_AUDIO * rel)
        # started = False

        # while True:
        #     cur_data = stream.read(self.CHUNK)
        #     slid_win.append(math.sqrt(abs(audioop.avg(cur_data, 4))))

        #     if sum([x > self.THRESHOLD for x in slid_win]) > 0:
        #         if started == False:
        #             print("Starting recording of phrase")
        #             started = True
        #         audio2send.append(cur_data)

        #     elif started:
        #         print("Finished recording, decoding phrase")
        #         filename = self.save_speech(list(prev_audio) + audio2send, p)
        #         r = self.decode_phrase(filename)
        #         print("DETECTED: ", r)

        #         # Removes temp audio file
        #         os.remove(filename)
        #         # Reset all
        #         started = False
        #         slid_win = deque(maxlen=self.SILENCE_LIMIT * rel)
        #         prev_audio = deque(maxlen=0.5 * rel)
        #         audio2send = []
        #         print("Listening ...")

        #     else:
        #         prev_audio.append(cur_data)

        # print("* Done listening")
        # stream.close()
        # p.terminate()

if __name__ == '__main__':
    sd = SpeechDetector()
    sd.run()