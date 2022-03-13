from multiprocessing.sharedctypes import Value
import time
import wave
import os
from collections import deque
from typing import Deque
from numpy import byte, record
from enum import Enum

import sounddevice as sound
import webrtcvad


import speech_recognition as sr 


class RecordingState(Enum):
    RECORDING = 1
    POST = 2
    READY_TO_PROCESS = 3

class SpeechDetector:
    def __init__(self) -> None:
        # Microphone stream config.
        self._CHANNELS = 1
        self._SAMPLE_RATE = 32000
        self._BLOCK_SIZE = 320
        self._FORMAT = 'int16'

        self._SILENCE_LIMIT = 0.5 # Silence limit in seconds. When this time passes the
        # recording finishes and the file is decoded

        self._PREV_AUDIO = 0.5 # Previous audio (in seconds) to prepend. This helps to prevent 
        # chopping the beginning of the phrase.
         

    def write_audio_to_file(self, data: bytearray) -> str:
        """
        Writes recorded phrase to a wav file for use in speech recognition models downstream
        """
        filename = f'/tmp/output_{str(int(time.time()))}.wav'
        wf = wave.open(f'{filename}', 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(self._SAMPLE_RATE)
        wf.writeframes(data)
        wf.close()

        return f'{filename}'

    def decode_phrase(self, wav_file: str) -> str:
        
            audio_file = sr.AudioFile(wav_file)
            r = sr.Recognizer()
            with audio_file as source:
                try:
                    audio_data = r.record(source)
                    print(r.recognize_google(audio_data))
                except sr.UnknownValueError as err:
                    print('Failed to find words in audio, skipping...')

    def run(self) -> None:
        """
        Listens to Microphone, extracts speech phrases from it and calls speech recognition model
        to decode the sound
        """
        vad = webrtcvad.Vad(3)
        audio_to_write: bytearray = bytearray()
        prev_audio: Deque[bytearray] = deque(maxlen=5)
        post_speech_audio: bytearray = bytearray()

        recording_state: RecordingState = RecordingState.RECORDING.value

        stream = sound.RawInputStream(
            samplerate=self._SAMPLE_RATE, 
            channels=self._CHANNELS, 
            dtype=self._FORMAT, 
            blocksize=self._BLOCK_SIZE
        )
        stream.start()

        while True:
            data = stream.read(self._BLOCK_SIZE)
            raw_audio_data = data[0]

            if vad.is_speech(raw_audio_data, self._SAMPLE_RATE):
                if recording_state == RecordingState.RECORDING.value:
                    audio_to_write.extend(raw_audio_data)
                elif recording_state == RecordingState.POST.value:
                    recording_state = RecordingState.RECORDING.value
                    audio_to_write.extend(post_speech_audio)
                
            elif recording_state == RecordingState.RECORDING.value and len(audio_to_write) > self._SILENCE_LIMIT * self._SAMPLE_RATE:
                recording_state = RecordingState.POST.value
            elif recording_state == RecordingState.POST.value:
                if len(post_speech_audio) < self._SILENCE_LIMIT * self._SAMPLE_RATE:
                    post_speech_audio.extend(raw_audio_data)
                else:
                    recording_state = RecordingState.READY_TO_PROCESS.value
            elif recording_state == RecordingState.READY_TO_PROCESS.value:
                print("Finished recording, writing audio file")
                output = bytearray()
                for audio_chunk in prev_audio:
                    output.extend(audio_chunk)

                output.extend(audio_to_write)
                filename = self.write_audio_to_file(output)

                self.decode_phrase(filename)

                if os.path.exists(filename):
                    os.remove(filename)
                else:
                    print(f'Failed to find file at path {filename}, skipping deletion...')

                # Reset state holders back to defaults
                audio_to_write = bytearray()
                prev_audio = deque(maxlen=5)
                post_speech_audio = bytearray()
                recording_state = RecordingState.RECORDING.value
            else:
                if len(prev_audio) > 0:
                    prev_audio.popleft()
                prev_audio.append(raw_audio_data)

                if len(audio_to_write) > 0:
                    audio_to_write = bytearray()
        
        stream.close()

if __name__ == '__main__':
    sd = SpeechDetector()
    sd.run()