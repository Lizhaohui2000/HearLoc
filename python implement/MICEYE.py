import numpy as np
import math
import os
from gcc_phat import *
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import time
import copy


class MICEYE:
    def __init__(self, d_w=0.4, theta = 0, d_a=0.05, M=4, mdim=2):
        self.c = 343
        self.Fs = 48000
        self.minterp = 5
        self.d_w = d_w
        self.theta = theta
        self.d_a = d_a
        self.M = M
        self.D = (self.M-1)*self.d_a
        self.mrange = round(2*self.d_w/self.c*self.Fs+self.D/self.c*self.Fs+20)
        self.sstep = 0.1
        self.x_range = np.arange(-3, 3, self.sstep)
        self.y_range = np.arange(0, 4, self.sstep)
        self.mdim = mdim
        self.z_max = 0
        if self.mdim == 3:
            self.z_max = 1
            self.z_range = np.arange(0, self.z_max, self.sstep)
        else: self.z_range = [0]
        self.LocMap_2D = np.zeros((len(self.y_range), len(self.x_range)))
        self.LocMap_3D = np.zeros((len(self.x_range), len(self.y_range), len(self.z_range)))
        self.EstPos_2D = np.zeros(2)
        self.EstPos_3D = np.zeros(3)
        self.arr_pos = self.getArrayLocation()
        self.tau_arr, self.Ps_arr = self.generateDelayArray()
        self.topk = math.ceil(self.D*self.Fs/self.c*self.minterp*0.2)
        self.len_task = self.tau_arr.shape[0]
        self.fig = plt.figure()
        # plt.ion()

    def generateDelayArray(self):
        filename = './roomPara/dw_'+str(self.d_w)+'_theta_'+str(self.theta)+'_dim_'+str(self.mdim)+'.npz'
        if not os.path.exists(filename): # if file exists
        # if True:
            print('Delay parameters are generating...')
            comb_num = round(self.M*(self.M-1)/2*4)
            total_len = len(self.x_range)*len(self.y_range)*len(self.z_range)
            tau_arr = np.zeros((total_len, comb_num))
            Ps_arr = np.zeros((total_len, 3))
            mtag = 0
            for x in self.x_range:
                for y in self.y_range:
                    for z in self.z_range:
                        P_s = [x,y,z]
                        ktag = 0
                        for k1 in range(self.M-1):
                            for k2 in range(k1+1, self.M):
                                tau_arr[mtag, (ktag*4):(ktag*4+4)] = self.getDelays(self.arr_pos[k2,:], self.arr_pos[k1,:], P_s)
                                ktag += 1
                        Ps_arr[mtag,:] = P_s
                        mtag += 1
            np.savez(filename, tau_arr, Ps_arr)
        
        farr = np.load(filename)
        tau_arr = farr['arr_0']
        tau_arr = np.round(tau_arr*self.minterp*self.Fs + self.mrange*self.minterp).astype(int)
        Ps_arr = farr['arr_1']

        return tau_arr, Ps_arr

    def getDelays(self, P_2, P_1, P_s):
        P_1v = copy.deepcopy(P_1)
        P_2v = copy.deepcopy(P_2)
        P_1v[1] = -P_1v[1]
        P_2v[1] = -P_2v[1]
        return np.array([self.getDist(P_2, P_1, P_s),self.getDist(P_2v, P_1v, P_s),self.getDist(P_2v, P_1, P_s),self.getDist(P_2, P_1v, P_s)])/self.c
                
    def getDist(self, m1, m2, P_s):
        return np.linalg.norm(m1-P_s)-np.linalg.norm(m2-P_s)

    def getArrayLocation(self): #ULA
        dx = self.d_a*np.cos(self.theta)
        dy = self.d_a*np.sin(self.theta)
        ret_arr = np.zeros((self.M, 3))
        for m in range(self.M):
            ret_arr[m, :] = np.array([m*dx, self.d_w+m*dy, 0])
        return ret_arr
    # print(getArrayPosition(0.2, 30/180*math.pi, 0.05, 4))

    def getPosition(self, sig):
        R_num = round(self.M*(self.M-1)/2)
        R_arr = np.zeros((R_num, 2*self.mrange*self.minterp+1))
        mtag = 0
        
        ##### 0.4s for a one second speech
        time1 = time.time()
        for m in range(self.M-1):
            for n in range(m+1, self.M):
                _, R_temp = gcc_phat(sig[n,:], sig[m,:], interp=self.minterp) #[(sig.shape[1]/2+tau_range).astype(int)]
                R_arr[mtag,:] = R_temp[((sig.shape[1]-self.mrange)*self.minterp):((sig.shape[1]+self.mrange)*self.minterp+1)]
                mtag += 1
        time2 = time.time()
        print(time2-time1)
        
        LOS_AOA_range = round(self.D/self.c*self.Fs)*self.minterp
        half_len = self.mrange*self.minterp
        R_03_top_idx = np.argsort(-R_arr[2, (half_len-LOS_AOA_range):(half_len+LOS_AOA_range+1)])[:self.topk]
        R_03_top_idx = R_03_top_idx + half_len - LOS_AOA_range
        
        # print(R_03_top_idx)
        ######  0.01s
        LSE_vec = np.zeros((self.len_task, 4))
        for m in range(self.len_task):
            if self.Ps_arr[m,1]>self.d_w:
                if self.tau_arr[m,8] in R_03_top_idx:
                    for p in range(4):
                        for k in range(R_num):
                            LSE_vec[m, p] += R_arr[k, self.tau_arr[m, p+4*k]]
                            # print([k, self.tau_arr[m, p+4*k]])
                    # print(LSE_vec[m, :])
        # GCC normalization
        
        # t1 = time.time()
        max_LSE_vec = np.max(LSE_vec, axis=0)
        min_LSE_vec = np.min(LSE_vec, axis=0)
        LSE_arr_norm = (LSE_vec-min_LSE_vec)/(max_LSE_vec-min_LSE_vec)
        # obtain the optimal location
        LSE_vec = np.sum(LSE_arr_norm, axis=1)
        # t2 = time.time()
        # print(t2-t1)

        est_pos = np.zeros(self.mdim)
        # ~ top_idx = np.argsort(-LSE_vec)[0:3]
        # ~ LSE_vec = (LSE_vec-np.min(LSE_vec))/(np.max(LSE_vec)-np.min(LSE_vec))
        # ~ if self.mdim == 2:
            # ~ self.LocMap_2D = np.reshape(LSE_vec, (len(self.x_range), len(self.y_range))).T
            # ~ est_pos = self.weightedLocation(self.Ps_arr[top_idx,:], LSE_vec[top_idx])
            # ~ est_pos = np.round(est_pos, 2)
            # ~ self.EstPos_2D = est_pos
        # ~ elif self.mdim == 3:
            # ~ self.LocMap_3D = np.reshape(LSE_vec, (len(self.x_range), len(self.y_range), len(self.z_range)))
            # ~ est_pos = self.weightedLocation(self.Ps_arr[top_idx,:], LSE_vec[top_idx])
            # ~ est_pos = np.round(est_pos, 2)
            # ~ self.EstPos_3D = est_pos
        #print('Estimated Location: ', str(est_pos))
        
        # ~ if self.mdim == 2:
            # ~ self.realtimePlot2D()
        # ~ else:
            # ~ self.realtimePlot3D()
        return est_pos
        
    def weightedLocation(self, Ps_arr, weights):
        weights = weights**4
        return np.sum(Ps_arr*weights.reshape(len(weights), 1), axis=0)/np.sum(weights)

    def realtimePlot2D(self):
        ax = self.fig.add_subplot(111)
        ax.imshow(self.LocMap_2D**4, cmap='viridis') #, interpolation='bicubic'
        ax.plot([30, 30], [0, np.size(self.LocMap_2D, 0)-1], "w--", linewidth=3.0)
        ax.plot([30, 30+(self.M-1)*self.d_a/self.sstep], [round(self.d_w/self.sstep), round(self.d_w/self.sstep)], "b", linewidth=4.0)
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')

        max_index = [(self.EstPos_2D[0])/self.sstep+30, self.EstPos_2D[1]/self.sstep]
        ax.plot(max_index[0], max_index[1], "r^", markersize=8)
        ax.set_title('Estimated Location: ['+str(self.EstPos_2D[0])+', '+str(self.EstPos_2D[1])+']')
        self.fig.gca().invert_yaxis()

    def realtimePlot3D(self):
        # if tag=='zeros':
        #     self.LocMap_3D = np.zeros(self.LocMap_3D.shape)
        #     self.LocMap_3D[0,0,0]=1
        #     self.EstPos_3D = np.zeros(self.EstPos_3D.shape)
        ax = self.fig.add_subplot(111, projection='3d')
        flattened = self.LocMap_3D.flatten()
        tap_k = np.argpartition(flattened, -5)[-5:]
        indices_3d = np.unravel_index(tap_k, self.LocMap_3D.shape) # 3*5 tuple
        ax.scatter3D(indices_3d[0]*self.sstep-4, indices_3d[1]*self.sstep, indices_3d[2]*self.sstep)
        ax.plot([0, (self.M-1)*self.d_a], [round(self.d_w), round(self.d_w)], "b", linewidth=4.0)
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_xlim(-3, 3)#len(self.x_range)
        ax.set_ylim(0, len(self.y_range)*self.sstep)
        ax.set_zlim(0, len(self.z_range)*self.sstep)
        ax.set_title('Estimated Location: ['+str(self.EstPos_3D[0])+', '+str(self.EstPos_3D[1])+', '+str(self.EstPos_3D[2])+']')
        # ax.view_init(elev=15, azim=-80)
        # ax.invert_xaxis()

    def __del__(self):
        pass
        # plt.ioff()

if __name__ == '__main__':
    miceye = MICEYE(d_w=0.3, mdim=2)
    # print(miceye.getDelays(np.array([0,0.3,0]), np.array([0.1,0.3,0]), np.array([2,2,0])))
    # print(miceye.getArrayLocation())

    filename = r"a_50_3_8_s_38_23_8.txt"
    # ~ filename = r"a_50_3_8_s_66_32_8.txt"
    sig = np.loadtxt(filename)
    sig = sig.T
    sig = sig[:, 0:24000]
    
    mtime = 0
    for m in range(1):
        time1 = time.time()
        miceye.getPosition(sig)
        time2 = time.time()
        mtime += time2-time1
    print(mtime/1)
    # ~ plt.show()

    # t1 = time.time()
    # t2 = time.time()
    # print(t2-t1)


