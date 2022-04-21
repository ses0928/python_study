# for mathematical calculation
import math
import numpy as np
from scipy import interpolate

# from logging import root
import sys

# for GUI
import tkinter
from tkinter import (filedialog,ttk)

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
'''

# data container
raw_data = []

# option menu container
loaded_tw = ("0.0")
loaded_freq = ("1767")

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
    
    menu_tw = op_menu_tw['menu']
    menu_tw.delete(0,'end')

    for name in temp_tw_box:
        menu_tw.add_command(label=name, command=lambda name=name: var_tw.set(name))

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

# averaging the data : FFT each pre, post file and ...
def FFT():
    global raw_data
    global freq

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

        # modify fft_data for each data_box : pick data having freq value in w1_box
        for i in range(len(raw_data)):
            if index_box:
                temp_fft_box = []
                # pre data setting
                for j in range(len(index_box)):
                    temp_fft_box.append(raw_data[i].fft_pre[index_box[j]])
            
                if temp_fft_box:
                    raw_data[i].fft_pre = temp_fft_box
                    # now, fft data has selected row (freq) and each row has 64 elements
            
                # post data setting
                temp_fft_box = []
                for j in range(len(index_box)):
                    temp_fft_box.append(raw_data[i].fft_post[index_box[j]])
            
                if temp_fft_box:
                    raw_data[i].fft_post = temp_fft_box
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
            for j in range(len(raw_data[0].fft_post)):
                raw_data[i].fft_pre[j].reverse()
                raw_data[i].fft_post[j].reverse()

        for i in range(len(raw_data)):
            raw_data[i].swap("FFT_pre")
            raw_data[i].swap("FFT_post")

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

        # interpolation part
        for i in range(len(raw_data)):
            # pre data interpolate
            tck_real = interpolate.bisplrep(w1_axis,wm_axis,np.real(raw_data[i].fft_pre))
            sp_real = interpolate.bisplev(w1_range,wm_range,tck_real)

            tck_imag = interpolate.bisplrep(w1_axis,wm_axis,np.imag(raw_data[i].fft_pre))
            sp_imag = interpolate.bisplev(w1_range,wm_range,tck_imag)

            temp_fft_box = []
            for j in range(len(sp_real)):
                temp_fft_box.append([])
                for k in range(len(sp_real[0])):
                    temp_fft_box[j].append(complex(sp_real[j][k],sp_imag[j][k]))

            raw_data[i].fft_pre = temp_fft_box

            # post data interpolate
            tck2_real = interpolate.bisplrep(w1_axis,wm_axis,np.real(raw_data[i].fft_post))
            sp2_real = interpolate.bisplev(w1_range,wm_range,tck2_real)

            tck2_imag = interpolate.bisplrep(w1_axis,wm_axis,np.imag(raw_data[i].fft_post))
            sp2_imag = interpolate.bisplev(w1_range,wm_range,tck2_imag)

            temp_fft_box = []
            for j in range(len(sp_real)):
                temp_fft_box.append([])
                for k in range(len(sp_real[0])):
                    temp_fft_box[j].append(complex(sp2_real[j][k],sp2_imag[j][k]))
        
            raw_data[i].fft_post = temp_fft_box

            print(f"interpolation : {(i+1)/len(raw_data)*100} %")

        # rearrangement of fft data : last swap
        for i in range(len(raw_data)):
            raw_data[i].swap("FFT_pre")
            raw_data[i].swap("FFT_post")

        print("-------- Interpolation complete --------")

        ### test code
        temp_z = []
        for i in range(len(raw_data[0].fft_pre)):
            temp_z.append([])
            for j in range(len(raw_data[0].fft_pre[0])):
                temp_z[i].append((raw_data[0].fft_pre[i][j] + raw_data[0].fft_post[i][j]).real/2)

        ax_2d.clear()
        ax_2d.contour(w1_range,wm_range,temp_z,levels=20,linewidths=0.5,colors='k')
        ax_2d.contourf(w1_range,wm_range,temp_z,levels=20,cmap="RdYlBu_r")
        ax_2d.set_xlabel('$\omega_\\tau$ (cm$^{-1}$)')
        ax_2d.set_ylabel('$\omega_m$ (cm$^{-1}$)')
        canvas.draw()

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
canvas1 = tkinter.Canvas(window_main,width=300,height=600)
canvas1.place(x=50,y=0,anchor="nw")

# button set
button_open = tkinter.Button(window_main,text="Open M file",command=openMfile)
button_fft = tkinter.Button(window_main,text="FFT the data",command=FFT)
button_plot_pre = tkinter.Button(window_main,text="Plot FFT pre",command=FFTplot_pre)
button_plot_post = tkinter.Button(window_main,text="Plot FFT post",command=FFTplot_post)
button_interp = tkinter.Button(window_main,text="Interpolate the data",command=interp)

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

# range input for interpolation and
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

### Place button, label, input, ...
button_open.place(x=20,y=50)
button_fft.place(x=20,y=150)
button_plot_pre.place(x=120,y=150)
button_plot_post.place(x=220,y=150)
button_interp.place(x=20,y=290)

# FFT plot contents
label_fft_wm.place(x=40,y=120)
canvas1.create_window(110,130,window=entry_fft_wm1)
label_fft_tilde.place(x=200,y=120)
canvas1.create_window(210,130,window=entry_fft_wm2)

label_tw.place(x=20,y=90)
op_menu_tw.place(x=80,y=85)
label_freq.place(x=190,y=90)
op_menu_freq.place(x=260,y=85)

# Interpolation contents
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


label_M.pack(side=tkinter.TOP)


# canvas place + toolbar generation for figure (axes)
toolbar = NavigationToolbar2Tk(canvas,window_main)
toolbar.update()
toolbar.pack(side=tkinter.BOTTOM,fill=tkinter.X)
canvas.get_tk_widget().place(x=350,y=50)

# main loop. need for maintaining the window
window_main.mainloop()