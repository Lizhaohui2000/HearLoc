"""
 Estimate time delay using GCC-PHAT with interpolation
 Copyright (c) 2024 Zhaohui Li

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

import numpy as np
import matplotlib.pyplot as plt

def gcc_phat(sig, refsig, fs=1, max_tau=None, interp=1):
    '''
    This function computes the offset between the signal sig and the reference signal refsig
    using the Generalized Cross Correlation - Phase Transform (GCC-PHAT)method.
    '''
    len_sig = len(sig)
    len_refsig = len(refsig)

    max_len = max(len_sig, len_refsig)
    sig = np.concatenate([sig, np.zeros(max_len-len_sig)])
    refsig = np.concatenate([refsig, np.zeros(max_len-len_refsig)])

    n = 2*max_len

    SIG = np.fft.fft(sig, n=n)
    REFSIG = np.fft.fft(refsig, n=n)
    R = SIG * np.conj(REFSIG)/ np.abs(SIG * np.conj(REFSIG))

    zeros_pad = np.zeros(round((interp-1)*n/2))
    R_pad = np.fft.fftshift(np.concatenate([zeros_pad, np.fft.fftshift(R), zeros_pad]))

    cc = np.real(np.fft.ifft(R_pad))

    max_shift = int(interp * n / 2)
    if max_tau:
        max_shift = np.minimum(int(interp * fs * max_tau), max_shift)

    cc = np.concatenate((cc[-max_shift:], cc[:max_shift+1]))
    shift = np.argmax(np.abs(cc)) - max_shift

    tau = shift / float(interp * fs)
    
    return tau, cc
    
def main():
    sig = np.array([1,2,3,1,2,3,1,2])
    refsig = np.array([2, 1,2,3,1,2,3,1])
    _, cc = gcc_phat(sig, refsig, interp=1)
    plt.plot(cc)
    plt.show()

if __name__ == "__main__":
    main()
