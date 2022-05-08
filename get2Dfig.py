# for mathematical calculation
import math
import numpy as np

# for sys.exit()
import sys

# for GUI
import tkinter
from tkinter import (filedialog,ttk)

# for graph drawing
from matplotlib import pyplot as plt
from matplotlib import gridspec
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)


# loaded files list (tuple type) + loaded colormap list
loaded_files = ("hello","world")
loaded_files2 = ("RdBu_r","RdYlBu_r","gist_rainbow","rainbow","terrain","gnuplot")

# the number of loaded files, filenames list, data container for selected files
filenames = ["/"]
num_files = 0
xdata = []
ydata = []
zdata = []
Tw_text = " "

# open file dialog
def openfiles():
    global option_menu
    
    global filenames
    global num_files

    # file load
    filenames = filedialog.askopenfilenames(title='Select files',filetypes=(("dat files","*.dat"),("all files","*.*")))
    num_files = len(filenames)

    # option menu update
    menu = option_menu['menu']
    menu.delete(0,'end')

    for name in filenames:
        menu.add_command(label=name, command=lambda name=name: variable.set(name))
    
def draw_graph(mode,ind=0):
    # x, y, z data of selected file
    global xdata
    global ydata
    global zdata
    global wm_data
    global wt_data
    global int_data
    global filenames

    global Tw_text
    global label_Tw

    # load index of selected file on menu
    if mode != "all":
        menu = option_menu['menu']
        value = variable.get()
        index = menu.index(value)
    else:
        index = ind

    # get file name
    Tw_text = filenames[index].split("=")[-1]
    Tw_text = Tw_text.split(".dat")[0]
    label_Tw['text'] = f"Tw = {Tw_text}  "

    # file load + insert data
    f = open(filenames[index],'rt',encoding='utf-8')
    if filenames[index][-3:] == 'dat':
        raw_data = []
        for row in f:
            raw_data.append(row.split('\t'))
        
        # transpose the list
        temp_list = [list(x) for x in zip(*raw_data)]
        raw_data = temp_list

        # w_m, w_t axis setup + 2D data setup
        xdata = raw_data[0][1:]
        for i in range(len(xdata)):
            try:
                xdata[i] = float(xdata[i])
            except:
                xdata[i] = float(xdata[i].split("\n")[0])

        ydata = []
        for row in raw_data:
            ydata.append(row[0])
        ydata.pop(0)
        
        for i in range(len(ydata)):
            try:
                ydata[i] = float(ydata[i])
            except:
                try:
                    ydata[i] = float(ydata[i].split("\n")[0])
                except:
                    pass

        zdata = []
        for row in raw_data:
            temp = row
            temp.pop(0)
            zdata.append(temp)
        zdata.pop(0)

        for i in range(len(zdata)):
            for j in range(len(zdata[0])):
                try:
                    zdata[i][j] = float(zdata[i][j])
                except:
                    zdata[i][j] = float(zdata[i][j].split("\n")[0])

        # select data
        wm_data = []
        wt_data = []
        int_data = []

        # get entry values
        try:
            wm1 = int(entry_wm_lb.get())
            wm2 = int(entry_wm_ub.get())
            wt1 = int(entry_wt_lb.get())
            wt2 = int(entry_wt_ub.get())
        except:
            wm1 = 1670
            wm2 = 1790
            wt1 = 1670
            wt2 = 1790

        # append data in selected range to container
        for value in xdata:
            if wt1 <= value <= wt2:
                wt_data.append(value)
        
        for value in ydata:
            if wm1 <= value <= wm2:
                wm_data.append(value)

        xind1 = xdata.index(wt1)
        xind2 = xdata.index(wt2)
        yind1 = ydata.index(wm1)
        yind2 = ydata.index(wm2)

        for i in range(yind1,yind2+1):
            int_data.append([])

        for i in range(yind1,yind2+1):
            for j in range(xind1,xind2+1):
                int_data[i-yind1].append(zdata[i][j])

        ''' normalization of 2D data. it's not necessary..
        # size rearrangement of int_data
        # find maximum value of zdata (2D array)
        temp_max = []
        for row in int_data:
            temp_max.append(max(row))
        z_max = float(max(temp_max))

        for i in range(len(int_data)):
            for j in range(len(int_data[0])):
                int_data[i][j] = round(int_data[i][j]/z_max,3)
        '''

        # draw 2D contour plot of xdata, ydata, zdata
        ax_main.clear()

        # set the number of contour lines
        try:
            num_cl = int(entry_cl.get())
        except:
            num_cl = 20

        # load index of selected file on menu
        menu2 = option_menu2['menu']
        value2 = variable2.get()
        index2 = menu2.index(value2)

        scmap = loaded_files2[index2]

        if mode == "raw":
            ax_main.contour(xdata,ydata,zdata,levels=num_cl,linewidths=0.5,colors='k')
            ax_main.contourf(xdata,ydata,zdata,levels=num_cl,cmap=scmap)
        else:
            ax_main.contour(wt_data,wm_data,int_data,levels=num_cl,linewidths=0.5,colors='k')
            ax_main.contourf(wt_data,wm_data,int_data,levels=num_cl,cmap=scmap)
        
        ax_main.set_xlabel('$\omega_t$ (cm$^{-1}$)')
        ax_main.set_ylabel('$\omega_m$ (cm$^{-1}$)')
        canvas.draw()
    
    else:
        print("Insert *.dat file")

# flags for plots ginput
p_flag = False
fp_flag = False

# plot graphs with draw_graph function
def plot():
    # x, y, z data of selected file
    global xdata
    global ydata
    global zdata
    global filenames

    global Tw_text
    global label_Tw

    global p_flag
    global fp_flag

    draw_graph("selected")
    p_flag = True
    fp_flag = False

def fullplot():
    # x, y, z data of selected file
    global xdata
    global ydata
    global zdata
    global filenames

    global Tw_text
    global label_Tw

    global p_flag
    global fp_flag

    draw_graph("raw")
    p_flag = False
    fp_flag = True

# figure save code
def savefig(auto=False,getname = ""):
    #extent = ax_main.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    extent = ax_main.get_tightbbox(fig.canvas.get_renderer(),call_axes_locator=True,bbox_extra_artists=None).transformed(fig.dpi_scale_trans.inverted())
    if auto:
        savename = getname
    else:
        savename = filedialog.asksaveasfilename(defaultextension=("png file",".png"))
    #fig.savefig(savename,bbox_inches=extent.expanded(1.2,1.2))
    fig.savefig(savename,bbox_inches=extent.expanded(1.0,1.1))

def saveall():
    global num_files

    savename = filedialog.asksaveasfilename()
    for i in range(num_files):
        # 1. draw graph for each graph
        draw_graph("all",i)
        
        # 2. set savename for each file
        Tw_text = filenames[i].split("=")[-1]
        Tw_text = Tw_text.split(".dat")[0]
        name = savename + Tw_text + ".png"
        savefig(True,name)
    
    draw_graph("selected")

def callback(event):
    global p_flag       # flag for raw 2D spectrum plot or selected range of 2D spectrum plot
    global fp_flag

    global xdata        # data
    global ydata
    global zdata
    global wm_data
    global wt_data
    global int_data

    global horiz_x      # sliced spectra data
    global int1
    global vert_y
    global int2

    [x,y] = ax_main.transData.inverted().transform((event.x,899-event.y))
    [x,y] = [round(x),round(y)]

    if fp_flag and p_flag:
        print("Error detected. please re-plot the graph.")
        p_flag = False
        fp_flag = False
    
    elif fp_flag:
        # set index
        ind1 = xdata.index(x)
        ind2 = ydata.index(y)

        # draw horizontal slice data
        horiz_x = xdata
        int1 = zdata[ind2]

        ax1.clear()
        ax1.plot(horiz_x,int1)

        # draw vertical slice data
        vert_y = ydata
        int2 = []
        for i in range(len(ydata)):
            int2.append(zdata[i][ind1])
        
        ax2.clear()
        ax2.plot(int2,vert_y)

        # finally draw the slice graphs
        canvas.draw()
    
    elif p_flag:
        # set index
        ind1 = wm_data.index(x)
        ind2 = wt_data.index(y)

        # draw horizontal slice data
        horiz_x = wm_data
        int1 = int_data[ind2]

        ax1.clear()
        ax1.plot(horiz_x,int1)
        
        # draw vertical slice data
        vert_y = wt_data
        int2 = []
        for i in range(len(wt_data)):
            int2.append(int_data[i][ind1])
        
        ax2.clear()
        ax2.plot(int2,vert_y)

        # finally draw the slice graphs
        canvas.draw()


#####################  GUI code #############################
window_main = tkinter.Tk()
window_main.title("2D spectra viewer")
window_main.geometry("1200x900+100+100")
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
fig = plt.figure(figsize=(9,9),dpi=100)
gs = gridspec.GridSpec(nrows=3,ncols=3)
ax1 = fig.add_subplot(gs[0,0:2])
ax_main = fig.add_subplot(gs[1:3,0:2])
ax2 = fig.add_subplot(gs[1:3,2])
fig.subplots_adjust(left=0.1,top=0.95,wspace=0.4,hspace=0.34)

ax_main.set_xlabel('$\omega_t$ (cm$^{-1}$)')
ax_main.set_ylabel('$\omega_m$ (cm$^{-1}$)')

canvas = FigureCanvasTkAgg(fig,master=window_main)
canvas.draw()

# canvas : button, entry (input box), label (rigid text), menubar
canvas1 = tkinter.Canvas(window_main,width=300,height=600)
canvas1.place(x=50,y=0,anchor="nw")

# button set
button_open = tkinter.Button(window_main,text="Open files",command=openfiles)
button_plot = tkinter.Button(window_main,text="Plot 2D graph",command=plot)
button_fullplot = tkinter.Button(window_main,text="Plot raw data",command=fullplot)
button_save = tkinter.Button(window_main,text="save 2D spectrum",command=savefig)
button_saveall = tkinter.Button(window_main,text="save all 2D spectra",command=saveall)

# option menu setting
variable = tkinter.StringVar(window_main)
variable.set("loaded files")
option_menu = tkinter.OptionMenu(window_main,variable,*loaded_files)
option_menu.configure(state='normal')
option_menu.pack()

# Tw value of selected data
label_Tw = ttk.Label(window_main,text="T_w value")

# range input
label_wt = ttk.Label(window_main,text=u"w\u209C (cm\u207B\u00B9) :")
label_wm = ttk.Label(window_main,text=u"w\u2098 (cm\u207B\u00B9) :")
label_tilde1 = ttk.Label(window_main,text="~")
label_tilde2 = ttk.Label(window_main,text="~")
entry_wt_lb = tkinter.Entry(window_main,width=10)
entry_wt_ub = tkinter.Entry(window_main,width=10)
entry_wm_lb = tkinter.Entry(window_main,width=10)
entry_wm_ub = tkinter.Entry(window_main,width=10)

entry_wt_lb.insert(0,"1670")    # set default values (carbonyl stretch)
entry_wt_ub.insert(0,"1790")
entry_wm_lb.insert(0,"1670")
entry_wm_ub.insert(0,"1790")

# input : set the number of contour lines and colormap
label_cl = ttk.Label(window_main,text="# of contour lines :")
entry_cl = tkinter.Entry(window_main,width=5)
entry_cl.insert(0,"20")

label_cmap = ttk.Label(window_main,text="Color map of graph :")

# option menu for color map
variable2 = tkinter.StringVar(window_main)
variable2.set("RdYlBu_r")
option_menu2 = tkinter.OptionMenu(window_main,variable2,*loaded_files2)
option_menu2.configure(state='normal')
option_menu2.pack()

# positioning buttons, entry, and labels
button_open.place(x=20,y=50)
label_Tw.place(x=180,y=55)
button_plot.place(x=60,y=210)
button_fullplot.place(x=180,y=210)
button_save.place(x=40,y=240)
button_saveall.place(x=180,y=240)

label_wt.place(x=40,y=90)
label_wm.place(x=40,y=120)
canvas1.create_window(110,100,window=entry_wt_lb)
label_tilde1.place(x=200,y=90)
canvas1.create_window(210,100,window=entry_wt_ub)
canvas1.create_window(110,130,window=entry_wm_lb)
label_tilde2.place(x=200,y=120)
canvas1.create_window(210,130,window=entry_wm_ub)

label_cl.place(x=100,y=150)
canvas1.create_window(190,160,window=entry_cl)
label_cmap.place(x=90,y=180)
option_menu2.place(x=210,y=175)

# toolbar generation for figures (axes)
toolbar = NavigationToolbar2Tk(canvas,window_main)
toolbar.update()
toolbar.pack(side=tkinter.BOTTOM,fill=tkinter.X)
canvas.get_tk_widget().place(x=350,y=50)
canvas.get_tk_widget().bind("<Button-1>",callback)

# main loop. need for maintaining the window
window_main.mainloop()