# HearLoc: Locating Unknown Sources in 3D with a Small-sized Microphone Array

## Abstract

This is the code for our work "HearLoc: Locating Unknown Sources in 3D with a Small-sized Microphone Array". We propose an indoor sound source localization system that can precisely localize multiple sound sources in both 2D and 3D with a single tens-cm microphone array. Our system achieves a median error of $0.2m$ and $0.34m$ in 2D and 3D, respectively, under a latency of only $0.2s$. 



Our approach leverages multipath propagation, typically viewed as a challenge, to enhance indoor localization precision. By effectively modeling the cross-correlations between multipath signals, we can construct a large virtual cross-wall array for localization. Specifically, for a uniform linear array (ULA) of diameter $D$, our model can expand it into a virtual 2D array of size $(2d_w, D)$, where $D$ is the array diameter and $d_w$ is the distance to the reflecting wall. Based on near-field localization theory [1], this method increases localization capability by a factor of $\frac{4d_w^2}{D^2}$. Consequently, both localization accuracy and dimensionality are significantly improved.

## System Design

Our system is consisted of three main modules: array localization calibrator, ISSL module (delay picker, GCC spectrum generator, and location selector), and iterative module for multiple sources. Our system workflow can be shown in:
<div align="center">
<img src="https://github.com/Lizhaohui2000/HearLoc/blob/main/resource/architecture.png" alt="Example Image" width="500">
</div>

Furthermore, we have investigated to modele more than one ECHO signal in a room for localization. More details can be found in our paper. 

## File Structure:

* **Matlab codes**: "localize_one_ECHO.m" is for 2D/3D localization with the LOS and one ECHO signals. "localize_two_ECHO.m" is for localization with the LOS and two ECHO signals. "localize_multiple_sources.m" is for multiple sources localization. Fold "utils" involves the tools in signal processing. Requirement: Matlab 2021b. 
* Folder "python implement" is the python code for sound source localization in real time. Requirements: Raspberry Pi 3B+, Seeed Respeaker 4-Mic ULA, Seeed Voice Card and its driver [2]. 
* "samples.zip" is the audio sample for localization. You can download and unzip it in this folder. 



If you have any questions, please feel free to contact my email lizhaohui@csu.edu.cn or leave an issue. 

## Reference

[1] Orfanidis S J. Electromagnetic waves and antennas[J]. 2002. MLA 

[2] https://wiki.seeedstudio.com/ReSpeaker_4-Mic_Linear_Array_Kit_for_Raspberry_Pi/

