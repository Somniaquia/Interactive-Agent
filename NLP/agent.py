import torch
from torch import nn
import torchvision
from torch.utils.data import DataLoader

import sounddevice as sd
import speech_recognition as sr

r = sr.Recognizer()

while True:
    if (r.recognize_google()):
        pass