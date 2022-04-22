# for mathematical calculation
import math
import numpy as np
from scipy import interpolate

# from logging import root
import sys

# for GUI
import tkinter
from tkinter import (StringVar, filedialog,ttk)

# for graph drawing
from matplotlib import pyplot as plt
from matplotlib import gridspec
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk)

'''
This is phasing code for data of 2DIR spectra

1. Open M file to read all data of single 2DIR experiment. M file contains the path and Tw (waiting time) data
2. Perform FFT for each row of each data (time domain -> w1 frequency domain)
3. If you want to check how FFT is done, set Tw and w_m values and Plot pre(non-rephasing) or post(rephasing) data.
   This will plot the real part of pre, post data.
   This check can only performed after FFT and before interpolation
4. To interpolate the data, set wm and w1 frequency ranges, and resln (resolution of interpolation)
   Two ranges will be assigned after loading M file. Be careful not to set the range out of loaded ranges.
   After interpolation, 2D spectrum of real part of sum of pre and post data will be plotted

--- Problems ---
1. 2DIR w_m projection : Maybe I misunderstood the structure of data box..
'''

# data container
raw_data = []

# option menu container
loaded_tw = ("0.0")
loaded_freq = ("1767")

# interpolation flag.  Only when interpolation is finished, it becomes True.
# working flag : If phasing is in progress, it becomes True
interp_flag = False
work_flag = False
pp_flag = False

# data box class in container
class data_box():
    def __init__(self,Tw,pre=[],post=[],fft_pre=[],fft_post=[]):
        self.Tw = Tw
        self.pre = pre
        self.post = post
        self.fft_pre = fft_pre
        self.fft_post = fft_post
    
    def swap(self,target):
        if target == "pre":
            temp_list = [list(x) for x in zip(*self.pre)]
            self.pre = temp_list
        elif target == "post":
            temp_list = [list(x) for x in zip(*self.post)]
            self.post = temp_list
        
        elif target == "FFT_pre":
            try:
                temp_list = [list(x) for x in zip(*self.fft_pre)]
                self.fft_pre = temp_list
            except:
                print("FFT failed. FFT data container is empty")

        elif target == "FFT_post":
            try:
                temp_list = [list(x) for x in zip(*self.fft_post)]
                self.fft_post = temp_list
            except:
                print("FFT failed. FFT data container is empty")

### open M file : M file loading and put data on containers
### raw_data : pre, post data container, M_box : Tw container
def openMfile():
    # non-rephasing, rephasing data container
    # i-th component is i-th Tw data file (pre + post)
    global raw_data

    # wm range for averaging
    global wm_freq

    # Getting Tw, wm freq for FFT plot
    global loaded_tw
    global loaded_freq

    # load M file and modify filenames in M file
    filename = filedialog.askopenfilename(title="Select file")
    Mfile = open(filename,'rt',encoding='utf-8')

    M_box = []
    for row in Mfile:
        M_box.append(row.split("\t"))

    uppername = filename.split("/")
    uppertext = ""

    for i in range(len(uppername)-1):
        uppertext += uppername[i]
        uppertext += "/"
    
    for i in range(len(M_box)):
        M_box[i][0] = M_box[i][0].split("\\")[-1]
        M_box[i][0] = uppertext + M_box[i][0]

        M_box[i][2] = M_box[i][2].split("\n")[0]        # eliminate \n in wavenumber term

    Mfile.close()

    # label change code
    label_M['text'] = filename

    # load data whose filename is in M file
    # data container generation
    raw_data = []

    # data load
    for i in range(int(len(M_box)/2)):
        # pre file data collecting
        pre_file = open(M_box[2*i][0],'rt',encoding='utf-8')
        temp_pre = []
        for row in pre_file:
            temp_pre.append(row)
        
        for j in range(len(temp_pre)):
            temp_pre[j] = temp_pre[j].split('\t')
            temp_pre[j][-1] = temp_pre[j][-1].split('\n')[0]
        
        for j in range(len(temp_pre)):
            for k in range(len(temp_pre[0])):
                temp_pre[j][k] = float(temp_pre[j][k])

        pre_file.close()
        
        # post file data collecting
        post_file = open(M_box[2*i+1][0],'rt',encoding='utf-8')
        temp_post = []
        for row in post_file:
            temp_post.append(row)
        
        for j in range(len(temp_post)):
            temp_post[j] = temp_post[j].split('\t')
            temp_post[j][-1] = temp_post[j][-1].split('\n')[0]
        
        for j in range(len(temp_post)):
            for k in range(len(temp_post[0])):
                temp_post[j][k] = float(temp_post[j][k])

        post_file.close()

        # appending data boxes to raw_data
        raw_data.append(data_box(M_box[2*i][1],temp_pre,temp_post,[],[]))
    
    # get w_m, w_1 range
    entry_wm_lb.delete(0,'end')
    entry_wm_ub.delete(0,'end')
    entry_w1_lb.delete(0,'end')
    entry_w1_ub.delete(0,'end')
    
    entry_wm_lb.insert(0,str(round(min(raw_data[0].pre[0][1:]))))
    entry_wm_ub.insert(0,str(round(max(raw_data[0].pre[0][1:]))))
    entry_w1_lb.insert(0,str(round(min(raw_data[0].pre[0][1:]))))
    entry_w1_ub.insert(0,str(round(max(raw_data[0].pre[0][1:]))))

    # wm_freq setting. on 2D data of SPE sample (C=O mode), 1797 ~ 1665.
    wm_freq = raw_data[0].pre[0][1:]

    # option Tw, freq update
    temp_tw_box = []
    for i in range(len(raw_data)):
        temp_tw_box.append(raw_data[i].Tw)
    
    menu_tw = op_menu_tw['menu']        # Tw data for FFT plot
    menu_tw.delete(0,'end')

    menu_phasing_tw = op_menu_phasing_tw['menu']        # Tw data for phasing
    menu_phasing_tw.delete(0,'end')

    for name in temp_tw_box:
        menu_tw.add_command(label=name, command=lambda name=name: var_tw.set(name))
        menu_phasing_tw.add_command(label=name, command=lambda name=name: var_tw.set(name))

    menu_freq = op_menu_freq['menu']
    menu_freq.delete(0,'end')

    for name in wm_freq:
        menu_freq.add_command(label=name, command=lambda name=name: var_freq.set(name))

    # swap data to make optimal array with FFT
    # pre, post array have 64 rows and each row has 811 elements
    for i in range(len(raw_data)):
        raw_data[i].swap("pre")
        raw_data[i].swap("post")

    # baseline correction for all pre, post set.
    for i in range(len(raw_data)):
        for j in range(1,len(raw_data[i].pre)):
            baseline = sum(raw_data[i].pre[j][1:])/len(raw_data[i].pre[j][1:])
            for k in range(1,len(raw_data[i].pre[j])):
                raw_data[i].pre[j][k] -= baseline
            
            baseline2 = sum(raw_data[i].post[j][1:])/len(raw_data[i].post[j][1:])
            for k in range(1,len(raw_data[i].post[j])):
                raw_data[i].post[j][k] -= baseline2

    print("--------- data loading complete --------")

# open pump-probe data file for phasing
def open_pp():
    global pp_data
    global pp_flag

    global wm_range
    global interp_flag

    if interp_flag:
        filename = filedialog.askopenfilename(title="Select Pump-Probe data")
        f = open(filename,'rt',encoding='utf-8')

        pp_data = []
        for row in f:
            pp_data.append(row.split("\t"))
    
        f.close()

        index = 0  # zero time
        for i in range(len(pp_data)):
            pp_data[i][-1] = pp_data[i][-1].split("\n")[0]
            
            for j in range(len(pp_data[0])):
                pp_data[i][j] = float(pp_data[i][j])
            
            if i>1 and pp_data[i][0] == 0:
                index = i    
    
        # interpolation and data update
        pp_f = interpolate.interp1d(pp_data[0][1:],pp_data[index][1:],kind='cubic')
        try:
            pp_data = pp_f(wm_range)
        except:
            try:
                pp_data = pp_f(wm_range[1:-1])
            except:
                print("Use smaller range of w$_m$")

        pp_data = np.array(pp_data)
        pp_data = pp_data/max(pp_data)
        pp_flag = True
        print("Pump-probe data is loaded")
    
    else:
        print("Do interpolation first")

# averaging the data : FFT each pre, post file and ...
def FFT():
    global raw_data
    global freq

    global interp_flag      # interpolation flag

    res = 0.825 # resolution of FFT?  default value : 0.825 cm-1

    # frequency range setup
    freq = []
    for i in range(8192):
        freq.append(i*res)
    
    mean_freq = sum(freq)/len(freq)
    for i in range(len(freq)):
        freq[i] -= mean_freq

    # M file loaded check
    if raw_data == []:
        print("Open M file before averaging")
    
    # FFT perform
    else:
        # manual zero padding
        t_len = 8192 - len(raw_data[0].pre[1][1:])
        zero_list = []
        for k in range(t_len):
            zero_list.append(0)

        for i in range(len(raw_data)):
            # clear the fft data container
            raw_data[i].fft_pre = []
            raw_data[i].fft_post = []

            for j in range(1,len(raw_data[0].pre)):
                # pre data setting
                fft_pre_y = zero_list + raw_data[i].pre[j][1:]
                fft_y = np.fft.fft(fft_pre_y,n=8192)
                fft_y = np.fft.fftshift(fft_y)
                raw_data[i].fft_pre.append(fft_y)

                # post data setting
                fft_post_y = raw_data[i].post[j][1:] + zero_list
                fft_y2 = np.fft.fft(fft_post_y,n=8192)
                fft_y2 = np.fft.fftshift(fft_y2)
                raw_data[i].fft_post.append(fft_y2)
            
            print(f"FFT processing : {(i+1)/len(raw_data)*100} %")

        # alarm for FFT (w1 axis)
        print("-------- FFT complete --------")
        interp_flag = False

def fftplot(pre_post):
    global raw_data
    global freq

    if raw_data[0].fft_pre==[]:
        print("Do FFT first")

    elif len(raw_data[0].fft_pre) == len(freq):
        for i in range(len(raw_data)):
            raw_data[i].swap("FFT_pre")
            raw_data[i].swap("FFT_post")
        
        print("FFT Data rearranged. Try again")
    
    elif len(raw_data[0].fft_pre[0]) == len(freq):
        # select the Tw and freq
        menu_tw = op_menu_tw['menu']
        Tw = var_tw.get()
        ind1 = menu_tw.index(Tw)

        menu_freq = op_menu_freq['menu']
        Wm = var_freq.get()
        ind2 = menu_freq.index(Wm)
        
        # plot
        xmin = float(entry_fft_wm1.get())
        xmax = float(entry_fft_wm2.get())

        ax_2d.clear()
        if pre_post == "pre":
            ax_2d.plot(freq,raw_data[ind1].fft_pre[ind2])
            ax_2d.set_xlim([xmin,xmax])
            canvas.draw()

        elif pre_post == "post":
            ax_2d.plot(freq,raw_data[ind1].fft_post[ind2])
            ax_2d.set_xlim([xmin,xmax])
            ax_2d.set_xlabel("$\omega_m$ (cm$^{-1}$)")
            canvas.draw()

        else:
            print("You should select pre or post")

    else:
        print("FFT can be plotted only before interpolation. Do FFT again")

def FFTplot_pre():
    fftplot("pre")

def FFTplot_post():
    fftplot("post")


def interp():
    global raw_data
    global freq
    global wm_freq

    global w1_range
    global wm_range

    global interp_flag

    if raw_data[0].fft_pre == []:
        print("Do FFT first")
    
    elif len(raw_data[0].fft_pre[0]) != 8192:
        print("Return to FFT part and do it again")

    else:
        for i in range(len(raw_data)):
            raw_data[i].swap("FFT_pre")
            raw_data[i].swap("FFT_post")
            print(f"FFT processing : {(i+1)/len(raw_data)*100} %")
        
        print("FFT data rearranged")

        # set w1 range
        w1_lb = int(entry_w1_lb.get())
        w1_ub = int(entry_w1_ub.get())

        ind = 0             # searching index (freq)
        temp_freq = w1_lb

        index_box = []      # index container
        w1_freq = []

        while(ind<8192):
            # get frequency and index in w1 range
            if w1_lb <= freq[ind] <= w1_ub:
                index_box.append(ind)
                w1_freq.append(freq[ind])
        
            # exit when freq[ind] is larger than the upper bound
            if freq[ind] > w1_ub:
                ind = 9999

            ind += 1

        temp_fft_box=[]
        temp_fft_box2=[]
        # modify fft_data for each data_box : pick data having freq value in w1_box
        for i in range(len(raw_data)):
            if index_box:
                temp_fft_box.clear()
                # pre data setting
                for j in range(len(index_box)):
                    temp_fft_box.append(raw_data[i].fft_pre[index_box[j]])
            
                if temp_fft_box:
                    raw_data[i].fft_pre = np.array(temp_fft_box)
                    # now, fft data has selected row (freq) and each row has 64 elements
                
                else:
                    print("temp_fft_box is empty. Please check the code")
            
                # post data setting
                temp_fft_box2.clear()
                for j in range(len(index_box)):
                    temp_fft_box2.append(raw_data[i].fft_post[index_box[j]])
            
                if temp_fft_box2:
                    raw_data[i].fft_post = np.array(temp_fft_box2)
                    # now, fft post data has selected row (freq) and each row has 64 elements

                else:
                    print("temp_fft_box is empty. Please check the code")

            else:
                print("Error detected. index box is empty!")
    
        # alarm to finished
        print("setting w1 axis and data rearrangement is complete")

        # flip wm_freq
        if min(wm_freq) != wm_freq[0]:
            wm_freq.reverse()

        # rearrangement of data - 1
        for i in range(len(raw_data)):
            for j in range(len(raw_data[i].fft_post)):
                #raw_data[i].fft_pre[j].reverse()
                #raw_data[i].fft_post[j].reverse()
                raw_data[i].fft_pre[j] = np.flip(raw_data[i].fft_pre[j])
                raw_data[i].fft_post[j] = np.flip(raw_data[i].fft_post[j])

        for i in range(len(raw_data)):
            raw_data[i].swap("FFT_pre")
            raw_data[i].swap("FFT_post")

            raw_data[i].fft_pre = np.array(raw_data[i].fft_pre)
            raw_data[i].fft_post = np.array(raw_data[i].fft_post)

        # test code : 2D spectrum drawing before interpolation (Only for debugging)
        test = True
        temp_z = []
        if test:
            try:
                menu_tw = op_menu_tw['menu']
                Tw = var_tw.get()
                ind = menu_tw.index(Tw)
            except:
                ind = 0

            temp_z = (raw_data[ind].fft_pre.real + raw_data[ind].fft_post.real)/2
            ax_2d.clear()
            ax_2d.contour(w1_freq,wm_freq,temp_z,levels=20,linewidths=0.5,colors='k')
            ax_2d.contourf(w1_freq,wm_freq,temp_z,levels=20,cmap="RdYlBu_r")
            canvas.draw()

        ###### interpolating the data #####
        [w1_axis, wm_axis] = np.meshgrid(w1_freq,wm_freq)
    
        # setting w1, wm ranges
        wm_lb = int(entry_wm_lb.get())
        wm_ub = int(entry_wm_ub.get())
        resln = int(entry_res.get())

        w1_range = []
        wm_range = []
    
        temp_freq = w1_lb
        while(temp_freq <= w1_ub):
            w1_range.append(temp_freq)
            temp_freq += resln
        
        temp_freq = wm_lb
        while(temp_freq <= wm_ub):
            wm_range.append(temp_freq)
            temp_freq += resln
    
        print("Interpolation ready")

        method = "grid"     # there are two options : grid (griddata) and Rbf
        [w1_grid,wm_grid] = np.meshgrid(w1_range,wm_range)

        if method == "grid":
            # interpolation data with griddata. faster than Rbf and accurate enough.
            for i in range(len(raw_data)):
                z_pre_real = interpolate.griddata((wm_axis.flatten(),w1_axis.flatten()),(raw_data[i].fft_pre.real).flatten(),(w1_grid,wm_grid),method='cubic')
                z_pre_imag = interpolate.griddata((wm_axis.flatten(),w1_axis.flatten()),(raw_data[i].fft_pre.imag).flatten(),(w1_grid,wm_grid),method='cubic')

                raw_data[i].fft_pre = np.array(z_pre_real) + np.array(z_pre_imag)*complex(0,1)

                z_post_real = interpolate.griddata((wm_axis.flatten(),w1_axis.flatten()),(raw_data[i].fft_post.real).flatten(),(w1_grid,wm_grid),method='cubic')
                z_post_imag = interpolate.griddata((wm_axis.flatten(),w1_axis.flatten()),(raw_data[i].fft_post.imag).flatten(),(w1_grid,wm_grid),method='cubic')

                raw_data[i].fft_post = np.array(z_post_real) + np.array(z_post_imag)*complex(0,1)

                print(f"interpolation : {(i+1)/len(raw_data)*100} %")

        elif method == "Rbf":
            # new interpolation part with Rbf function : Really slow for 2D data, but much more accurate.
            # be careful that when using this method, swap of fft data is not good.
            for i in range(len(raw_data)):
                z_pre_real = interpolate.Rbf(w1_axis,wm_axis,raw_data[i].fft_pre.real,function='cubic')
                z_pre_imag = interpolate.Rbf(w1_axis,wm_axis,raw_data[i].fft_pre.imag,function='cubic')
                raw_data[i].fft_pre = z_pre_real(w1_grid,wm_grid) + z_pre_imag(w1_grid,wm_grid)*complex(0,1)

                z_post_real = interpolate.Rbf(w1_axis,wm_axis,raw_data[i].fft_post.real,function='cubic')
                z_post_imag = interpolate.Rbf(w1_axis,wm_axis,raw_data[i].fft_post.imag,function='cubic')
                raw_data[i].fft_post = z_post_real(w1_grid,wm_grid) + z_post_imag(w1_grid,wm_grid)*complex(0,1)

                print(f"interpolation : {(i+1)/len(raw_data)*100} %")
            
        else:
            print("Use griddata method or Rbf method only")

        print("-------- Interpolation complete --------")
        interp_flag = True

        ### test code
        temp_zdata=[]
        try:
            temp_zdata = (raw_data[ind].fft_pre.real + raw_data[ind].fft_post.real)/2
        except:
            temp_zdata = (raw_data[0].fft_pre.real + raw_data[0].fft_post.real)/2

        ax_2d.clear()
        ax_2d.contour(w1_range,wm_range,temp_zdata,levels=20,linewidths=0.5,colors='k')
        ax_2d.contourf(w1_range,wm_range,temp_zdata,levels=20,cmap="RdYlBu_r")
        ax_2d.set_xlabel('$\omega_\\tau$ (cm$^{-1}$)')
        ax_2d.set_ylabel('$\omega_m$ (cm$^{-1}$)')
        canvas.draw()
        

# interpolation plot
def interp_plot():
    global raw_data
    global w1_range
    global wm_range

    global interp_flag

    if interp_flag:
        menu_tw = op_menu_tw['menu']
        Tw = var_tw.get()
        ind = menu_tw.index(Tw)

        temp_z = (raw_data[ind].fft_pre.real + raw_data[ind].fft_post.real)/2

        # plot the 2D spectrum    
        ax_2d.clear()
        ax_2d.contour(w1_range,wm_range,temp_z,levels=20,linewidths=0.5,colors='k')
        ax_2d.contourf(w1_range,wm_range,temp_z,levels=20,cmap="RdYlBu_r")
        ax_2d.set_xlabel('$\omega_\\tau$ (cm$^{-1}$)')
        ax_2d.set_ylabel('$\omega_m$ (cm$^{-1}$)')
        canvas.draw()

    else:
        print("Do interpolation first")

### phasing code : 
def phaser(damn):
    global raw_data
    global w1_range
    global wm_range
    global pp_data

    global interp_flag
    global work_flag
    global pp_flag

    if interp_flag and work_flag==False:
        print("phasing parameter modification detected")

        # Select Tw (data) and data setting
        menu_tw = op_menu_phasing_tw['menu']
        Tw = var_tw.get()
        ind1 = menu_tw.index(Tw)

        data_pre = np.array(raw_data[ind1].fft_pre)
        data_post = np.array(raw_data[ind1].fft_post)
        
        dt12 = float(entry_t12.get())
        dt3LO = float(entry_t3LO.get())
        c1 = float(entry_c1.get())
        c2 = float(entry_c2.get())

        # test code
        wm_range_d = np.array(wm_range)
        wm_range_d = (wm_range_d-np.mean(wm_range_d))/abs(max(wm_range_d)-min(wm_range_d))
        FCONV = 1.883*10**(-4)      # 2*pi*29979245800/10^15

        [w1_axis,wm_axis] = np.meshgrid(w1_range,wm_range)
        [w1_axis2,wm_axis_d] = np.meshgrid(w1_range,wm_range_d)
        data_pre = data_pre*np.exp(complex(0,1)*FCONV*(wm_axis*dt3LO-w1_axis*dt12+wm_axis_d*w1_axis*c1+c2*w1_axis*w1_axis*wm_axis_d*wm_axis_d*FCONV))
        data_post = data_post*np.exp(complex(0,1)*FCONV*(wm_axis*dt3LO+w1_axis*dt12+wm_axis_d*w1_axis*c1+c2*w1_axis*w1_axis*wm_axis_d*wm_axis_d*FCONV))

        data_sum = data_pre + data_post

        # data plot
        ax_2d.clear()
        ax_2d.contour(w1_range,wm_range,data_sum.real,levels=20,linewidths=0.5,colors='k')
        ax_2d.contourf(w1_range,wm_range,data_sum.real,levels=20,cmap="RdYlBu_r")
        canvas.draw()

        # if pump-probe data is loaded, plot it also.
        if pp_flag:
            diff_flag = False                       # default : False. It becomes True when len(pp_data) < len(wm_range)
            # find maximum value of data_sum
            temp_box = abs(data_sum)
            max_box = []
            for i in range(len(temp_box)):
                max_box.append(max(temp_box[i]))
            
            max_value = max(max_box)
            max_ind = np.where(temp_box==max_value)
            [ind1,ind2] = [max_ind[0][0],max_ind[1][0]]

            # calculating chi^2
            chi2 = 0
            temp_box = []
            for i in range(len(data_sum)):
                temp_box.append(data_sum[i][ind2])

            temp_box = np.array(temp_box).real
            temp_box = temp_box/max(temp_box)

            try:
                diff_box = pp_data - temp_box
            except:
                diff_box = pp_data - temp_box[1:-1]
                diff_flag = True

            for i in range(len(diff_box)):
                chi2 += diff_box[i]**2

            # drawing
            ax_pp2.clear()
            if diff_flag:
                ax_pp2.plot(wm_range,temp_box,'r',wm_range[1:-1],pp_data,'b')
            else:
                ax_pp2.plot(wm_range,temp_box,'r',wm_range,pp_data,'b')

            label_chi2['text'] = f"Chi-square : {chi2}"
            canvas.draw()

        # Print out that 2D spectrum update is complete
        print("-------- Phasing --------")
        work_flag = False

    elif work_flag:
        print("Phasing is in progress, please wait")
    
    else:
        print("Do interpolation before phasing the data")

####################### GUI Code ##########################
window_main = tkinter.Tk()
window_main.title("Phasing 2D data")
window_main.geometry("1200x900+100+100")
window_main.resizable(False,False)

# window close -> program quit function
def wclose():
    global window_main

    window_main.destroy()
    window_main.quit()
    sys.exit()

window_main.protocol("WM_DELETE_WINDOW",wclose)

# figure generation
fig = plt.figure(figsize=(9,9),dpi=100)
gs = gridspec.GridSpec(nrows=3,ncols=3)
ax_2d = fig.add_subplot(gs[1:3,0:2])
ax_pp1 = fig.add_subplot(gs[0,2])
ax_pp2 = fig.add_subplot(gs[1:3,2])
fig.subplots_adjust(left=0.1,bottom=0.16,top=0.95,wspace=0.4,hspace=0.34)

ax_2d.set_xlabel('$\omega_\\tau$ (cm$^{-1}$)')
ax_2d.set_ylabel('$\omega_m$ (cm$^{-1}$)')

canvas = FigureCanvasTkAgg(fig,master=window_main)
canvas.draw()

# canvas1 : button, entry (input box), label(rigid text), ...
canvas1 = tkinter.Canvas(window_main,width=300,height=800)
canvas1.place(x=50,y=0,anchor="nw")

# button set
button_open = tkinter.Button(window_main,text="Open M file",command=openMfile)
button_fft = tkinter.Button(window_main,text="FFT the data",command=FFT)
button_plot_pre = tkinter.Button(window_main,text="Plot FFT pre",command=FFTplot_pre)
button_plot_post = tkinter.Button(window_main,text="Plot FFT post",command=FFTplot_post)
button_interp = tkinter.Button(window_main,text="Interpolate the data",command=interp)
button_inplot = tkinter.Button(window_main,text="Plot 2D spectrum",command=interp_plot)

# loaded M file name
label_M = ttk.Label(window_main,text="M filename")

# option menu setting
var_tw = tkinter.StringVar(window_main)
var_tw.set("empty")
op_menu_tw = tkinter.OptionMenu(window_main,var_tw,*loaded_tw)
op_menu_tw.configure(state='normal')
op_menu_tw.pack()

label_tw = ttk.Label(window_main,text="Tw (ps) :")

var_freq = tkinter.StringVar(window_main)
var_tw.set("empty")
op_menu_freq = tkinter.OptionMenu(window_main,var_freq,*loaded_freq)
op_menu_freq.configure(state='normal')
op_menu_freq.pack()

label_freq = ttk.Label(window_main,text=u"w\u2098 (cm\u207B\u00B9) :")

# range input for FFT
label_fft_wm = ttk.Label(window_main,text=u"w\u2098 (cm\u207B\u00B9) :")
label_fft_tilde = ttk.Label(window_main,text="~")

entry_fft_wm1 = tkinter.Entry(window_main,width=10)
entry_fft_wm2 = tkinter.Entry(window_main,width=10)

entry_fft_wm1.insert(0,"1900")
entry_fft_wm2.insert(0,"3000")

# range input for interpolation
label_wm = ttk.Label(window_main,text=u"w\u2098 (cm\u207B\u00B9) :")
label_w1 = ttk.Label(window_main,text=u"w\u2081 (cm\u207B\u00B9) :")
label_tilde1 = ttk.Label(window_main,text="~")
label_tilde2 = ttk.Label(window_main,text="~")
entry_wm_lb = tkinter.Entry(window_main,width=10)
entry_wm_ub = tkinter.Entry(window_main,width=10)
entry_w1_lb = tkinter.Entry(window_main,width=10)
entry_w1_ub = tkinter.Entry(window_main,width=10)

label_res = ttk.Label(window_main,text=u"Resln (cm\u207B\u00B9) :")
entry_res = tkinter.Entry(window_main,width=5)

entry_wm_lb.insert(0,"1900")
entry_wm_ub.insert(0,"3000")
entry_w1_lb.insert(0,"1900")
entry_w1_ub.insert(0,"3000")
entry_res.insert(0,"1")

# labels and inputs for phasing
label_phasing = ttk.Label(window_main,text="---------------- Phasing part ----------------")

label_t12 = ttk.Label(window_main,text="1,2 timing :")
label_t3LO = ttk.Label(window_main,text="3,LO timing :")
label_c1 = ttk.Label(window_main,text="chirp 1 :")
label_c2 = ttk.Label(window_main,text="chirp 2 :")

#sv_t12 = StringVar()
#entry_t12 = tkinter.Entry(window_main,width=5,textvariable=sv_t12,validate="focusout",validatecommand=phaser)

entry_t12 = tkinter.Entry(window_main,width=5)
entry_t3LO = tkinter.Entry(window_main,width=5)
entry_c1 = tkinter.Entry(window_main,width=5)
entry_c2 = tkinter.Entry(window_main,width=5)

entry_t12.bind('<FocusOut>',phaser)
entry_t3LO.bind('<FocusOut>',phaser)
entry_c1.bind('<FocusOut>',phaser)
entry_c2.bind('<FocusOut>',phaser)

entry_t12.insert(0,"0")
entry_t3LO.insert(0,"0")
entry_c1.insert(0,"0")
entry_c2.insert(0,"0")

label_phasing_Tw = ttk.Label(window_main,text="Tw (ps) :")
op_menu_phasing_tw = tkinter.OptionMenu(window_main,var_tw,*loaded_tw)
op_menu_phasing_tw.configure(state='normal')
op_menu_phasing_tw.pack()

button_pp = tkinter.Button(window_main,text="Load pump-probe data",command=open_pp)
label_chi2 = ttk.Label(window_main,text="Chi-square :")

### Place button, label, input, ...
button_open.place(x=20,y=50)
button_fft.place(x=20,y=150)
button_plot_pre.place(x=120,y=150)
button_plot_post.place(x=220,y=150)
button_interp.place(x=20,y=290)
button_inplot.place(x=200,y=290)

# Place FFT plot contents
label_fft_wm.place(x=40,y=120)
canvas1.create_window(110,130,window=entry_fft_wm1)
label_fft_tilde.place(x=200,y=120)
canvas1.create_window(210,130,window=entry_fft_wm2)

label_tw.place(x=20,y=90)
op_menu_tw.place(x=80,y=85)
label_freq.place(x=190,y=90)
op_menu_freq.place(x=260,y=85)

# Place interpolation contents
label_wm.place(x=40,y=190)
canvas1.create_window(110,200,window=entry_wm_lb)
label_tilde1.place(x=200,y=190)
canvas1.create_window(210,200,window=entry_wm_ub)
label_w1.place(x=40,y=220)
canvas1.create_window(110,230,window=entry_w1_lb)
label_tilde2.place(x=200,y=220)
canvas1.create_window(210,230,window=entry_w1_ub)
label_res.place(x=40,y=250)
canvas1.create_window(110,260,window=entry_res)

# Place phasing contents
label_phasing.place(x=50,y=320)

label_phasing_Tw.place(x=20,y=350)
op_menu_phasing_tw.place(x=80,y=345)
label_t12.place(x=20,y=380)
canvas1.create_window(60,390,window=entry_t12)
label_t3LO.place(x=150,y=380)
canvas1.create_window(200,390,window=entry_t3LO)
label_c1.place(x=20,y=410)
canvas1.create_window(60,420,window=entry_c1)
label_c2.place(x=150,y=410)
canvas1.create_window(200,420,window=entry_c2)

button_pp.place(x=20,y=445)
label_chi2.place(x=180,y=450)

# Show M filename
label_M.pack(side=tkinter.TOP)

# canvas place + toolbar generation for figure (axes)
toolbar = NavigationToolbar2Tk(canvas,window_main)
toolbar.update()
toolbar.pack(side=tkinter.BOTTOM,fill=tkinter.X)
canvas.get_tk_widget().place(x=350,y=50)

# main loop. need for maintaining the window
window_main.mainloop()