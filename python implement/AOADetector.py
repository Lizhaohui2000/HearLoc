import numpy as np
from gcc_phat import *
import matplotlib.pyplot as plt

class AOADetector:
	def detectAOA(self, y_arr):
		d_a = 0.05
		c = 343
		D = 4
		Fs = 48000
		R_arr = np.zeros((D-1, 2*y_arr.shape[1]+1))
		for k in range(D-1):
			_, R_arr[k,:] = gcc_phat(y_arr[k+1,:], y_arr[0,:])
	
		theta_power_arr = np.zeros(180-1)
		for k in range(len(theta_power_arr)):
			for m in range(D-1):
				shift_temp = (m+1)*d_a*np.cos(k/180*np.pi)/c*Fs
				theta_power_arr[k] += R_arr[m, y_arr.shape[1]+round(shift_temp)]
		
		theta_est = np.argmax(theta_power_arr)
		theta_power_arr = (theta_power_arr-min(theta_power_arr))/(max(theta_power_arr)-min(theta_power_arr))
		return theta_est, theta_power_arr

if __name__ == '__main__':
	filename = "a_50_3_8_s_38_23_8.txt"
	sig = np.loadtxt(filename)
	sig = sig.T
	aoaDetector = AOADetector()
	theta_est, theta_power_arr = aoaDetector.detectAOA(sig)
	plt.plot(theta_power_arr)
	plt.show()
