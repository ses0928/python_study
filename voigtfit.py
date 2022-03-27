# for mathematical calculation
#from logging import root
import math
import numpy as np
from scipy.optimize import curve_fit
import sys

# for GUI
import csv
import tkinter
from tkinter import (filedialog,ttk)

# for graph drawing
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

'''
How to use this program
1. load data files (Open files) : it should be .csv file and 1st column should contain wavenumber data and 2nd column should contain intensity
2. select file by clicking loaded files
3. write fitting range and peak positions (write higher wavenumber first, lower wavenumber later)
4. click 'Data Fit' button and see printed fitting parameters
5. click 'Draw graph' and see the fitting result
'''


# voigt function definition
def voigt(x,mu,w,A,xc,backg):
    return A*(mu*2/math.pi*w/(4*(x-xc)**2+w**2) + (1-mu)*math.sqrt(4*math.log(2)/math.pi)/w*np.exp(-4*math.log(2)/w**2*(x-xc)**2)) + backg

def voigt2p(x,mu1,w1,A1,xc1,mu2,w2,A2,xc2,backg):
    v1 = A1*(mu1*2/math.pi*w1/(4*(x-xc1)**2+w1**2) + (1-mu1)*math.sqrt(4*math.log(2)/math.pi)/w1*np.exp(-4*math.log(2)/w1**2*(x-xc1)**2))
    v2 = A2*(mu2*2/math.pi*w2/(4*(x-xc2)**2+w2**2) + (1-mu2)*math.sqrt(4*math.log(2)/math.pi)/w2*np.exp(-4*math.log(2)/w2**2*(x-xc2)**2))
    return v1+v2+backg

def voigt3p(x,mu1,w1,A1,xc1,mu2,w2,A2,xc2,mu3,w3,A3,xc3,backg):
    v1 = A1*(mu1*2/math.pi*w1/(4*(x-xc1)**2+w1**2) + (1-mu1)*math.sqrt(4*math.log(2)/math.pi)/w1*np.exp(-4*math.log(2)/w1**2*(x-xc1)**2))
    v2 = A2*(mu2*2/math.pi*w2/(4*(x-xc2)**2+w2**2) + (1-mu2)*math.sqrt(4*math.log(2)/math.pi)/w2*np.exp(-4*math.log(2)/w2**2*(x-xc2)**2))
    v3 = A3*(mu3*2/math.pi*w3/(4*(x-xc3)**2+w3**2) + (1-mu3)*math.sqrt(4*math.log(2)/math.pi)/w3*np.exp(-4*math.log(2)/w3**2*(x-xc3)**2))
    return v1+v2+v3+backg

# x, y data containers
xdata = []
ydata = []

xdata_temp = []
ydata_temp = []

# fitting parameters container
para_set = []
para_sets = []

# loaded files list (tuple type)
loaded_files = ("hello","world")

# the number of loaded files
num_files = 0

# open file dialog
def openfiles():
    global xdata
    global ydata
    global loaded_files
    global num_files

    if len(xdata):
        xdata = []
        ydata = []
        ax1.clear()

    # file load
    filenames = filedialog.askopenfilenames(title='Select files')
    num_files = len(filenames)

    # option menu update
    menu = option_menu['menu']
    menu.delete(0,'end')
    
    for name in filenames:
        menu.add_command(label=name, command=lambda name=name: variable.set(name))

    # csv file : data copy
    for i in range(len(filenames)):
        if filenames[i][-3:] == 'csv':
            xdata.append([])
            ydata.append([])

            f = open(filenames[i],'rt',encoding='utf-8')
            try:
                for row in csv.reader(f):
                    try:
                        xdata[i].append(float(row[0]))
                        ydata[i].append(float(row[1]))
                    except:
                        pass

            except csv.Error:
                pass

            f.close()

            ax1.plot(xdata[0],ydata[0])
            canvas.draw()
        
        else: print(filenames[i])

def draw_graph():
    global xdata_temp
    global ydata_temp
    global para_set

    if len(xdata_temp):
        ax1.clear()

        # 1 : plot raw data
        ax1.plot(xdata_temp,ydata_temp,color='black')
        ax1.axis([min(xdata_temp),max(xdata_temp),0,max(ydata_temp)*1.1])
        ax1.set_xlabel('Wavenumber (cm$^{-1}$)')
        ax1.set_ylabel('Absorbance')

        # 2 : plot fitting data
        fit_result = []
        peak_num = int((len(para_set)-1)/4)
        
        for i in range(len(xdata_temp)):
            fit_result.append(para_set[-1])

        # subsets plot if we have 2 or more peaks
        if peak_num > 1:
            fit_subset1 = []
            fit_subset2 = []
            fit_subset3 = []

            for i in range(len(xdata_temp)):
                fit_subset1.append(para_set[-1])
                fit_subset2.append(para_set[-1])
                fit_subset3.append(para_set[-1])

        # data setting
        if peak_num == 1:
            [mu,w,A,xc] = para_set[0:4]
            
            for i in range(len(xdata_temp)):
                x = xdata_temp[i]
                fit_result[i] += A*(mu*2/math.pi*w/(4*(x-xc)**2+w**2) + (1-mu)*math.sqrt(4*math.log(2)/math.pi)/w*np.exp(-4*math.log(2)/w**2*(x-xc)**2))
            
        elif peak_num == 2:
            [mu1,w1,A1,xc1,mu2,w2,A2,xc2] = para_set[0:8]
            
            for i in range(len(xdata_temp)):
                x = xdata_temp[i]
                fit_subset1[i] += A1*(mu1*2/math.pi*w1/(4*(x-xc1)**2+w1**2) + (1-mu1)*math.sqrt(4*math.log(2)/math.pi)/w1*np.exp(-4*math.log(2)/w1**2*(x-xc1)**2))
                fit_subset2[i] += A2*(mu2*2/math.pi*w2/(4*(x-xc2)**2+w2**2) + (1-mu2)*math.sqrt(4*math.log(2)/math.pi)/w2*np.exp(-4*math.log(2)/w2**2*(x-xc2)**2))
                fit_result[i] = fit_subset1[i] + fit_subset2[i] - para_set[-1]
        
        elif peak_num == 3:
            [mu1,w1,A1,xc1,mu2,w2,A2,xc2,mu3,w3,A3,xc3] = para_set[0:12]

            for i in range(len(xdata_temp)):
                x = xdata_temp[i]
                fit_subset1[i] += A1*(mu1*2/math.pi*w1/(4*(x-xc1)**2+w1**2) + (1-mu1)*math.sqrt(4*math.log(2)/math.pi)/w1*np.exp(-4*math.log(2)/w1**2*(x-xc1)**2))
                fit_subset2[i] += A2*(mu2*2/math.pi*w2/(4*(x-xc2)**2+w2**2) + (1-mu2)*math.sqrt(4*math.log(2)/math.pi)/w2*np.exp(-4*math.log(2)/w2**2*(x-xc2)**2))
                fit_subset3[i] += A3*(mu3*2/math.pi*w3/(4*(x-xc3)**2+w3**2) + (1-mu3)*math.sqrt(4*math.log(2)/math.pi)/w3*np.exp(-4*math.log(2)/w3**2*(x-xc3)**2))
                fit_result[i] = fit_subset1[i] + fit_subset2[i] + fit_subset3[i] - 2*para_set[-1]
                

        # draw fitting data
        ax1.plot(xdata_temp,fit_result,color='red')

        if peak_num == 2:
            ax1.plot(xdata_temp,fit_subset1,color='limegreen')
            ax1.plot(xdata_temp,fit_subset2,color='limegreen')
        
        elif peak_num == 3:
            ax1.plot(xdata_temp,fit_subset1,color='limegreen')
            ax1.plot(xdata_temp,fit_subset2,color='limegreen')
            ax1.plot(xdata_temp,fit_subset3,color='limegreen')
                
        canvas.draw()

    else:
        ax1.clear()
        ax1.plot(xdata[0],ydata[0],color='black')
        ax1.set_xlabel('Wavenumber (cm$^{-1}$)')
        ax1.set_ylabel('Absorbance')
        canvas.draw()

# voigt fitting function
def voigt_fit(index):
    global xdata
    global ydata
    global xdata_temp
    global ydata_temp
    global para_set

    if len(xdata_temp):
        xdata_temp = []
        ydata_temp = []
    
    # wavenumber range setting for fitting
    if int(entry_lb.get()): x1 = int(entry_lb.get())
    else: x1 = 1680

    if int(entry_ub.get()): x2 = int(entry_ub.get())
    else: x2 = 1800
    
    # default : index = 0

    if x1 < xdata[0][-1] or x2 > xdata[0][0]:
        print("Error")

    elif len(xdata) > 0:
        for i in range(len(xdata[index])):
            if x1 <= xdata[index][i] <= x2:
                xdata_temp.append(xdata[index][i])
                ydata_temp.append(ydata[index][i])

        # initial conditions : the number of peaks, peak positions
        temp_peaks = entry_peaks.get()
        temp_peaks = temp_peaks.split(",")

        peaks = []
        for peak in temp_peaks:
            peaks.append(float(peak))

        peak_num = len(peaks)

        # initial condition : peak amplitude setting
        data_interval = abs(xdata_temp[1]-xdata_temp[2])
        peak_amplitudes = []
        for i in range(peak_num):
            for j in range(len(xdata_temp)):
                if abs(xdata_temp[j]-peaks[i]) < data_interval:
                    peak_amplitudes.append(ydata_temp[j])
                    break
        
        sum_peakA = sum(peak_amplitudes)
        for i in range(peak_num):
            temp_amplitude = peak_amplitudes[i]/sum_peakA*sum(ydata_temp)/2
            peak_amplitudes[i] = temp_amplitude
        
        # initial conditions : setting
        initial = []
        for i in range(peak_num):
            initial.append(0.5)
            initial.append(10)
            initial.append(peak_amplitudes[i])
            initial.append(peaks[i])

        initial.append(min(ydata_temp)/2)

        # lower, upper bound setting for voigt fitting
        lb = []
        ub = []

        for i in range(peak_num):
            lb.append(0)
            lb.append(1)
            lb.append(sum(ydata_temp)/1000)
            lb.append(peaks[i]-10)
            ub.append(1)
            ub.append(50)
            ub.append(sum(ydata_temp))
            ub.append(peaks[i]+10)

        lb.append(0)
        ub.append(min(ydata_temp))

        lb_tuple = tuple(lb)
        ub_tuple = tuple(ub)

        if peak_num == 1:
            popt, pcov = curve_fit(voigt,xdata_temp,ydata_temp,p0=initial,bounds=(lb_tuple,ub_tuple))
            print(popt)
        
        elif peak_num == 2:
            popt, pcov = curve_fit(voigt2p,xdata_temp,ydata_temp,p0=initial,bounds=(lb_tuple,ub_tuple))
            print(f"1st peak width : {popt[1]:.2f}, 1st peak area : {popt[2]:.2f}, 1st peak position : {popt[3]:.2f} cm-1\n")
            print(f"2nd peak width : {popt[5]:.2f}, 2nd peak area : {popt[6]:.2f}, 2nd peak position : {popt[7]:.2f} cm-1\n")
            print(f"background : {popt[-1]:.3f}")
            
            # print(popt)
        
        elif peak_num == 3:
            popt, pcov = curve_fit(voigt3p,xdata_temp,ydata_temp,p0=initial,bounds=(lb_tuple,ub_tuple))
            print(popt)

        para_set = popt

# call the voigt fit function - single fit, all fit
def call_voigtfit():
    menu = option_menu['menu']
    value = variable.get()
    index = menu.index(value)

    voigt_fit(index)

def all_voigtfit():
    global para_sets
    global num_files

    if len(para_sets):
        para_sets = []

    for i in range(num_files):
        voigt_fit(i)
        para_sets.append(para_set)

# calculate the coordination number
def cal_cn():
    global para_set
    
    conc = int(entry_conc.get())
    gamma = float(entry_gamma.get())

    if len(para_set) == 9:
        if conc > 0:
            cn = 100/conc*para_set[6]/(para_set[6]+gamma*para_set[2])
            print(cn)

def cal_acn():
    global para_sets

    conc = int(entry_conc.get())
    gamma = float(entry_gamma.get())

    cn_set = []
    if len(para_sets) > 0 and conc > 0:
        if len(para_sets[0])==9:
            for i in range(len(para_sets)):
                cn = 100/conc*para_sets[i][6]/(para_sets[i][6]+gamma*para_sets[i][2])
                cn_set.append(cn)

            print(cn_set)

####### basic setting for the window size, location and resizability
window_main = tkinter.Tk()

window_main.title("Voigt fitting")
window_main.geometry("900x600+100+100")
window_main.resizable(False,False)

# window close
def wclose():
    global window_main

    window_main.destroy()
    window_main.quit()
    sys.exit()

menubar = tkinter.Menu(window_main)
window_main.config(menu=menubar)
window_main.protocol("WM_DELETE_WINDOW",wclose)

# figure generation
fig = plt.figure(figsize=(5,4), dpi=100)
ax1 = fig.add_subplot(1,1,1)
ax1.set_xlabel('Wavenumber (cm$^{-1}$)')
ax1.set_ylabel('Absorbance')
canvas = FigureCanvasTkAgg(fig,master=window_main)
canvas.draw()

# canvas : button, entry (input box), label (rigid text)
canvas1 = tkinter.Canvas(window_main,width=300,height=600)
canvas1.place(x=50,y=0,anchor="nw")

    # button set
button_open = tkinter.Button(window_main,text="Open files",command=openfiles)
button_draw = tkinter.Button(window_main,text="Draw graph",command=draw_graph)
button_vfit = tkinter.Button(window_main,text="Data Fit",command=call_voigtfit)
button_afit = tkinter.Button(window_main,text="Fit all data",command=all_voigtfit)
button_cn = tkinter.Button(window_main,text="Calculate coordination number",command=cal_cn)
button_acn = tkinter.Button(window_main,text="Calculate all CNs",command=cal_acn)

    # option menu setting
variable = tkinter.StringVar(window_main)
variable.set("loaded files")
option_menu = tkinter.OptionMenu(window_main,variable,*loaded_files)
option_menu.configure(state='normal')
option_menu.pack()

    # range input
label_v = ttk.Label(window_main,text="Range (cm\u207B\u00B9) :")
label_tilde = ttk.Label(window_main,text="~")
entry_lb = tkinter.Entry(window_main,width=10)
entry_ub = tkinter.Entry(window_main,width=10)

entry_lb.insert(0, "1680")     # set default values
entry_ub.insert(0, "1800")

    # peak positions input
label_peaks = ttk.Label(window_main,text="peak positions (cm\u207B\u00B9) :")
entry_peaks = tkinter.Entry(window_main,width=20)
entry_peaks.insert(0,"1752")

    # input for calculation of coordination number
label_conc = ttk.Label(window_main,text="concentration (mol %) :")
label_gamma = ttk.Label(window_main,text="gamma value :")
entry_conc = tkinter.Entry(window_main,width=5)
entry_gamma = tkinter.Entry(window_main,width=5)

entry_conc.insert(0,"0")
entry_gamma.insert(0,"1.4")

# positioning buttons, entry, and labels
button_open.place(x=20,y=50)
button_draw.place(x=50,y=150,anchor="nw")
button_vfit.place(x=150,y=150,anchor="nw")
button_afit.place(x=220,y=150,anchor="nw")
button_cn.place(x=30,y=260)
button_acn.place(x=220,y=260)

option_menu.place(x=100,y=50)

label_v.place(x=50,y=90)
label_tilde.place(x=230,y=90)
canvas1.create_window(140,100,window=entry_lb)
canvas1.create_window(240,100,window=entry_ub)

label_peaks.place(x=10,y=120)
canvas1.create_window(170,130,window=entry_peaks)

label_conc.place(x=10,y=190)
label_gamma.place(x=50,y=220)
canvas1.create_window(130,200,window=entry_conc)
canvas1.create_window(130,230,window=entry_gamma)

# toolbar generation -> graph canvas visualization
toolbar = NavigationToolbar2Tk(canvas,window_main)
toolbar.update()
toolbar.pack(side=tkinter.BOTTOM,fill=tkinter.X)
canvas.get_tk_widget().pack(side=tkinter.RIGHT)

# main loop. need for maintaing the window
window_main.mainloop()