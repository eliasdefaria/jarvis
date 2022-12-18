import time
import wave
import os
from collections import deque
from typing import Callable, Deque
from enum import Enum

from services.executor import Executor

import sounddevice as sound
import webrtcvad
import speech_recognition as sr 

class RecordingState(Enum):
    RECORDING = 1
    POST = 2
    READY_TO_PROCESS = 3

class SpeechDetector:
    _CHANNELS: int = 1
    _FORMAT: str = 'int16'

    def __init__(self, _SAMPLE_RATE: int = 32000, _SILENCE_LIMIT: float = 0.5, _PREV_AUDIO: float = 0.5) -> None:
        print('initilizing speech detector...')
        # Microphone stream config.
        self._SAMPLE_RATE = 32000
        self._BLOCK_SIZE = int(_SAMPLE_RATE * 0.01)

        self._SILENCE_LIMIT = 1.5 # Silence limit in seconds. When this time passes the
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
        """
        Takes in the wav file and uses the speeech_recognition library to convert the speech into text
        """
        audio_file = sr.AudioFile(wav_file)
        r = sr.Recognizer()
        with audio_file as source:
            try:
                audio_data = r.record(source)
                return str(r.recognize_google(audio_data))
            except sr.UnknownValueError as _:
                if os.environ['ENV'] == 'development':
                    print('Failed to find words in audio, skipping...')
                return ''

    def sanitize_text(self, text: str) -> str:
        return text.strip().lower()

    def run(self, fn_on_success: Callable) -> None:
        """
        Listens to Microphone, extracts speech phrases from it and calls speech recognition model
        to decode the sound. fn_on_success is called when the audio is successfully converted into
        a text string
        """
        vad = webrtcvad.Vad(3)
        audio_to_write: bytearray = bytearray()
        prev_audio: Deque[bytearray] = deque(maxlen=5)
        post_speech_audio: bytearray = bytearray()

        recording_state: RecordingState = RecordingState.RECORDING

        stream = sound.RawInputStream(
            samplerate=self._SAMPLE_RATE, 
            channels=self._CHANNELS, 
            dtype=self._FORMAT, 
            blocksize=self._BLOCK_SIZE
        )
        stream.start()
        while True:
            data = stream.read(self._BLOCK_SIZE)
            # NOTE: Steam.read returns this weird, self-defined `buffer` class which doesn't fit into the bytearray type. Runtime proves this wrong tho!
            raw_audio_data: bytearray = data[0] # type: ignore            
            if vad.is_speech(raw_audio_data, self._SAMPLE_RATE):
                if recording_state.value == RecordingState.RECORDING.value:
                    audio_to_write.extend(raw_audio_data)
                elif recording_state == RecordingState.POST.value:
                    recording_state = RecordingState.RECORDING
                    audio_to_write.extend(post_speech_audio)
            
            elif recording_state.value == RecordingState.RECORDING.value and len(audio_to_write) > self._SILENCE_LIMIT * self._SAMPLE_RATE:
                recording_state = RecordingState.POST
            elif recording_state.value == RecordingState.POST.value:
                if len(post_speech_audio) < self._SILENCE_LIMIT * self._SAMPLE_RATE:
                    post_speech_audio.extend(raw_audio_data)
                else:
                    recording_state = RecordingState.READY_TO_PROCESS
            elif recording_state.value == RecordingState.READY_TO_PROCESS.value:
                print("Finished recording, writing audio file")
                output = bytearray()
                for audio_chunk in prev_audio:
                    output.extend(audio_chunk)

                output.extend(audio_to_write)
                filename = self.write_audio_to_file(output)

                text = self.sanitize_text(self.decode_phrase(filename))

                if len(text) > 0:
                    if os.environ['ENV'] == 'development':
                        print('Got Speech: ', text)
                    fn_on_success(text)
                
                if os.path.exists(filename):
                    os.remove(filename)
                else:
                    print(f'Failed to find file at path {filename}, skipping deletion...')

                # Reset state holders back to defaults
                audio_to_write = bytearray()
                prev_audio = deque(maxlen=5)
                post_speech_audio = bytearray()
                recording_state = RecordingState.RECORDING
            else:
                if len(prev_audio) > 0:
                    prev_audio.popleft()
                prev_audio.append(raw_audio_data)

                if len(audio_to_write) > 0:
                    audio_to_write = bytearray()
        
        stream.close()

if __name__ == '__main__':
    sd = SpeechDetector()
    sd.run(Executor().execute_command_from_text)