import pyaudio
from queue import Queue
import threading
import numpy as np
import time
import matplotlib.pyplot as plt

from AOADetector import *
from MICEYE import *

from SocketClient import *
from voiceDetector import *
import signal
    
class MicArray(object):

    def __init__(self, rate=48000, channels=8, chunk_size=None):
        self.pyaudio_instance = pyaudio.PyAudio()
        self.quit_event = threading.Event()
        self.channels = channels
        self.sample_rate = rate
        
        self.queue = Queue(maxsize=3)

        self.chunk_size = chunk_size if chunk_size else rate / 10

        device_index = None
        for i in range(self.pyaudio_instance.get_device_count()):
            dev = self.pyaudio_instance.get_device_info_by_index(i)
            name = dev['name'].encode('utf-8')
            print(i, name, dev['maxInputChannels'], dev['maxOutputChannels'])
            if dev['maxInputChannels'] == self.channels:
                print('Use {}'.format(name))
                device_index = i
                break

        if device_index is None:
            raise Exception('can not find input device with {} channel(s)'.format(self.channels))

        self.stream = self.pyaudio_instance.open(
            input=True,
            start=False,
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=int(self.sample_rate),
            frames_per_buffer=int(self.chunk_size),
            stream_callback=self._callback,
            input_device_index=device_index,
        )

    def _callback(self, in_data, frame_count, time_info, status):
        if self.queue.full():
            self.queue.get()
        self.queue.put(in_data)
        # print(self.queue.qsize())

        return None, pyaudio.paContinue

    def start(self):
        #self.queue.clear()
        self.stream.start_stream()


    def read_chunks(self):
        self.quit_event.clear()
        while not self.quit_event.is_set():
            frames = self.queue.get()
            if not frames:
                break

            frames = np.frombuffer(frames, dtype='int16')
            yield frames

    def stop(self):
        self.quit_event.set()
        self.stream.stop_stream()
        self.queue.put('')

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        if value:
            return False
        self.stop()


def test_AOA():
    #### estimate AOA locally
    import signal
    import time
    aoaDetector = AOADetector()

    is_quit = threading.Event()

    def signal_handler(sig, num):
        is_quit.set()
        print('Quit')
    signal.signal(signal.SIGINT, signal_handler)
    
    fig, axes = plt.subplots(1,2, figsize=(10,4))
    line1, =axes[0].plot([], [])
    line2, =axes[1].plot([], [])
    plt.ion()
    with MicArray(48000, 8, 24000) as mic:
        for chunks in mic.read_chunks():
            chunks = np.array([chunks[0::8],chunks[1::8],chunks[2::8],chunks[3::8]]) 
            chunks = chunks/32768
            line1.set_data(np.arange(len(chunks[0,:])), chunks[0,:])
            axes[0].set_xlim(0, len(chunks[0,:]))
            axes[0].set_ylim(-1,1)
            if voiceDetector(chunks[0,:]):
                AOA, aoaSpect = aoaDetector.detectAOA(chunks)
                line2.set_data(np.arange(len(aoaSpect)), aoaSpect)
                axes[1].set_xlim(0, len(aoaSpect))
                axes[1].set_ylim(-0.1,1)
                print('AOA:', AOA) 
            else:
                line2.set_data(np.arange(180), np.zeros(180))
                axes[1].set_xlim(0, 180)
                axes[1].set_ylim(-0.1,1)
                #print('\n')
            
            plt.draw()
            plt.pause(1)
            
            if is_quit.is_set():
                plt.ioff()
                plt.show()
                break


def test_POS():
    #### send data through socket
    is_quit = threading.Event()
    
    def signal_handler(sig, num):
        is_quit.set()
        print('Quit')
    signal.signal(signal.SIGINT, signal_handler)
    
    socketClient = SocketClient('172.20.10.4', 12345) ## tcp send
    with MicArray(48000, 8, 48000) as mic:
        for chunks in mic.read_chunks():
            chunks = np.array([chunks[0::8],chunks[1::8],chunks[2::8],chunks[3::8]]) # int16 [-32768, 32767]
            if voiceDetector(chunks[0,:]/32767):
                ## tcp send
                socketClient.sendData(chunks.tolist())
                
                print('Voice detected! ')
            time.sleep(2)
            
            if is_quit.is_set():
                break
                
def test_POS_local():
    #### process on raspiberry locally
    is_quit = threading.Event()
    miceye = MICEYE(d_w=0.3, mdim=3)
    def signal_handler(sig, num):
        is_quit.set()
        print('Quit')
    signal.signal(signal.SIGINT, signal_handler)
    plt.ion() ## process local
    with MicArray(48000, 8, 48000) as mic:
        for chunks in mic.read_chunks():
            chunks = np.array([chunks[0::8],chunks[1::8],chunks[2::8],chunks[3::8]]) # int16 [-32768, 32767]
            if voiceDetector(chunks[0,:]/32767):
                ## process localization
                print('Voice detected! ')
                plt.clf()
                miceye.getPosition(chunks/32767)
                plt.pause(0.001)
                
            time.sleep(1)
            
            if is_quit.is_set():
                break
if __name__ == '__main__':
    # ~ test_AOA()
    # ~ test_POS()
    test_POS_local()


