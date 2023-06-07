import torch
from torch import nn
import torchvision
from torch.utils.data import DataLoader

import sounddevice as sd
import speech_recognition as sr

def record_speech():
    return

while True:
    r = sr.Recognizer()
    r.recognize_google()

    with record_speech() as source:
        audio = r.record(source)

