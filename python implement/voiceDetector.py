import numpy as np

def voiceDetector(sig):
    thresd = 0.03
    meng = np.sum(np.abs(sig))/len(sig)
    print('Signal strength:', meng)
    if meng > thresd:
        return True
    return False

#print(voiceDetector(0.5*np.random.rand(100)))
