# HearLoc: Locating Unknown Sources in 3D with a Small-sized Microphone Array


## Abstract

This is the code for our recent work **"HearLoc: Locating Unknown Sources in 3D with a Small-sized Microphone Array"**. Precisely determining the location of sound sources in 3D with a small-sized microphone array is usually considered difficult to achieve due to the constraint of far field effect. This work proposes to properly utilize the phenomenon of indoor multipath propagation, and builds a sound source localization system capable of localizing multiple sound sources in both 2D and 3D using a single microphone array of just tens of centimeters. Our system achieves a median error of $0.2m$ and $0.37m$ in 2D and 3D, respectively, under a latency of only $0.2s$. 

## Background and motivation

Indoor Sound Source Localization (ISSL) is under growing focus with the rapid development of smart IOT intelligence. Various scenarios benefit from this capability, including but not limited to: (I) A smart speaker can accurately identify illegal break-ins or elder falling according to the sound type and location. (II) A sweeping robot hears a command ``clean here" and can navigate to the exact location where the user stands for cleaning tasks. Compared with other localization technologies that use radio frequency or visual signals, localization directly by sound usually has advantages of **less energy consumption**, **wider field-of-view** and **less privacy concerns**. 

Our approach leverages multipath propagation, typically viewed as a challenge, to enhance the precision of indoor localization. By effectively modeling the cross-correlations between multipath signals, we can construct a large virtual cross-wall array to achieve precise localization. Specifically, for a small-sized uniform linear array (ULA) of diameter $D$, our model can expand it into a virtual 2D array of size $(2d_w, D)$, where $D$ is the array diameter and $d_w$ is the distance to the reflecting wall. Based on near-field localization theory [1], this method increases localization capability by a factor of $\frac{4d_w^2}{D^2}$. Consequently, both localization accuracy and dimensionality are significantly improved.

## System Design

We propose a novel locazation algorithm by selectively picking and summing the correlation powers at TDOAs of interest, which can be calculated by the geometry relationship between source, array and wall. Building opun this, we design our system by three main modules: array localization calibrator, ISSL module (delay picker, GCC spectrum generator, and location selector), and iterative module for multiple sources. Our system workflow can be shown in:
<div align="center">
<img src="https://github.com/Lizhaohui2000/HearLoc/blob/main/resource/architecture.png" alt="Example Image" width="500">
</div>

Furthermore, we have investigated to modele more than one ECHO signal in a room for localization. More details can be found in our paper. 

## File Structure

* **Matlab codes**: "localize_one_ECHO.m" is for 2D/3D localization with the LOS and one ECHO signals. "localize_two_ECHO.m" is for localization with the LOS and two ECHO signals. "localize_multiple_sources.m" is for multiple sources localization. Fold "utils" involves the tools in signal processing. Requirement: Matlab 2021b. 
* Folder "python implement" is the python code for sound source localization in real time. Requirements: Raspberry Pi 3B+, Seeed Respeaker 4-Mic ULA, Seeed Voice Card and its driver [2]. 
* "samples.zip" is the audio sample for localization. You can download and unzip it in this folder. 

If you have any questions, please feel free to contact my email lizhaohui@csu.edu.cn or leave an issue. 

## Reference

[1] Orfanidis S J. Electromagnetic waves and antennas[J]. 2002. MLA 

[2] https://wiki.seeedstudio.com/ReSpeaker_4-Mic_Linear_Array_Kit_for_Raspberry_Pi/

