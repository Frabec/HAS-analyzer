from tkinter import *
from tkinter import filedialog
import os as os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import rcParams


def browse_button():
    global folder_path
    global button3
    filename=filedialog.askdirectory()
    folder_path.set(filename)
    #activate the Do it button
    if len(folder_path.get())>0:
        button3.config(state="normal")
    else: 
        button3.config(state="disabled")
        button4.config(state="disabled")
#get in a folder open all the files and stores them in an array, using a double array format
def form_folder_to_arrays(path):
    data_storage= []
    for file_names in os.listdir(path):
        #the files containing wavefront information are in wft extension
        if not str.endswith(file_names, ".wft"):
            continue
        f= open(path+'\\'+file_names,'r')
        new_image=[]
        for lines in f:
            raw=(lines.split('\t'))
            #replace NaN by 0 and convert to float
            #*1000 to have values in nm
            modified=list(map(lambda x: 1000*float(x) if not("NaN" in x) else 0., raw))
            #if list is not empty
            new_image.append(modified)
        #Now data_storage contains a list of images of same xlength and ylength, but we have converted the NaN to zeros

        data_storage.append(new_image)
        f.close()
        
    return data_storage

def calculate_RMS_images(data): 
    RMS_images=[None]*len(data)
    for i,image in enumerate(data):
        #We delete the 0 because they were NaN
        filtered_image=[list(filter(lambda x: x!=0., row)) for row in image]
        RMS_images[i]=np.std([pixel for row in filtered_image for pixel in row])
    return RMS_images

def calculate_RMS_pixel_by_pixel(data):
    RMS_pixels=[]
    global RMS_map
    RMS_map=[]
    for i,_ in enumerate(data[0]):
        row=[]
        row_for_map=[]
        for j,_ in enumerate(data[0][i]):
            hasNaN=False
            for _,img in enumerate(data):
                if img[i][j] ==0:
                    hasNaN=True
                    break
            if not hasNaN:
                row.append(np.std([data[nber][i][j] for nber in range(len(data))], dtype=float))
                row_for_map.append(np.std([data[nber][i][j] for nber in range(len(data))], dtype=float))
            else:
                row_for_map.append(0.)
        if row:
            RMS_pixels.append(row)
        RMS_map.append(row_for_map)
    return RMS_pixels

def calculate_everything(path_to_folder, Recursive):
    if Recursive.get()==1:
        calculate_everything_recursive(path_to_folder)
    else: 
        calculate_everything_single_file(path_to_folder)

def  calculate_everything_single_file(path_to_folder):
        #Reset RMS map
        global RMS_map
        data=form_folder_to_arrays(path_to_folder)
        RMS_images=calculate_RMS_images(data)
        global mean_RMS
        mean_RMS.set(np.mean(RMS_images))
        global RMS_RMS
        RMS_RMS.set(np.std(RMS_images))
        RMS_pixel_by_pixel=calculate_RMS_pixel_by_pixel(data)
        global button4
        button4.config(state="normal")
        global RMS_pixels
        RMS_pixels.set(np.mean([pixel for row in RMS_pixel_by_pixel for pixel in row]))


def calculate_everything_recursive(path_to_folder):
    print("path_to_folder: " + path_to_folder)
    #There is no mean wavefront to plot
    global button4
    button4.config(state="normal")
    #Don't show any data it is only for single files
    global mean_RMS
    mean_RMS.set(None)
    global RMS_RMS
    RMS_RMS.set(None)
    global RMS_pixels
    RMS_pixels.set(None)
    write_file= open(path_to_folder+"/data.txt","w")
    write_file.write("Format of data:\nPath\nMean of RMS\tRMS of RMS\tRMS pixel by pixel\n")
    for root,_,_ in os.walk(path_to_folder, topdown="false"):
        #if there are files
            data=form_folder_to_arrays(root)
            if data:
                RMS_images=calculate_RMS_images(data)
                local_mean_RMS= np.mean(RMS_images)
                local_RMS_RMS=np.std(RMS_images)
                local_RMS_pixels_list=calculate_RMS_pixel_by_pixel(data)
                local_RMS_pixels=(np.mean([pixel for row in local_RMS_pixels_list for pixel in row]))
                write_file.write(root[len(path_to_folder):]+"\n")
                write_file.write(str(local_mean_RMS)+"\t"+str(local_RMS_RMS)+"\t"+str(local_RMS_pixels)+"\n")
            
    write_file.close()

#plot image map of RMS
def plotRMS():
    global RMS_map
    fig, ax = plt.subplots()
    im= ax.imshow(RMS_map, interpolation='hermite', cmap=cm.YlOrRd, origin='lower', extent=[-2,2,-2,2])
    cbar= fig.colorbar(im, label="RMS in nm")
    ###increase label size of colorbar
    ax = cbar.ax
    text = ax.yaxis.label
    font = matplotlib.font_manager.FontProperties(size=16)
    text.set_font_properties(font)
    ###
    plt.title("RMS map pixel by pixel", fontdict={'fontsize' : 22}, pad=20)
    #Add padding between title and plot
    plt.show()

root = Tk()
root.title("HAS Analyzer")
root.geometry("800x300")
#######################################
###           Global vars           ###
#######################################
folder_path = StringVar()
mean_RMS= DoubleVar()
RMS_RMS = DoubleVar()
RMS_pixels =DoubleVar()
Recursive = IntVar()
#store RMS map
RMS_map=[]
########################################


########################################
###               GUI                ###
########################################

lbl1 = Label(master=root,textvariable=folder_path)
lbl1.grid(row=0, column=3)
button2 = Button(text="Browse folder", command=browse_button)
button2.grid(row=0, column=2)
button3 = Button(text="Do it", state="disabled",command=lambda: calculate_everything(folder_path.get(), Recursive))
button3.grid(row=0, column=0)
button4 = Button(text="Show map of wavefront", state="disabled", command=plotRMS)
button4.grid(row=0, column=1)
#titles
lbl_mean_rms_global_title = Label(master=root, text="Mean of the RMS of the images(nm): ")
lbl_mean_rms_global_title.grid(row=2, column=0, sticky="W",pady=(50,10))
lbl_rms_rms_global_title = Label(master=root, text="RMS of the RMS of the images(nm): ")
lbl_rms_rms_global_title.grid(row=3, column=0, sticky="W",pady=10)
lbl_rms_pixel_by_pixel_title = Label(master=root, text="Mean of RMS pixel by pixel(nm): ")
lbl_rms_pixel_by_pixel_title.grid(row=4, column=0, sticky="W",pady=10)
#values
lbl_mean_rms_global_value = Label(master=root, textvariable=mean_RMS)
lbl_mean_rms_global_value.grid(row=2, column=1, sticky="W",pady=(50,10))
lbl_rms_rms_global_value = Label(master=root, textvariable=RMS_RMS)
lbl_rms_rms_global_value.grid(row=3, column=1, sticky="W",pady=10)
lbl_rms_pixel_by_pixel_value = Label(master=root, textvariable=RMS_pixels)
lbl_rms_pixel_by_pixel_value.grid(row=4, column=1, sticky="W",pady=10)
c= Checkbutton(master=root, text= "Browse folder recursively (output is a text file)", variable=Recursive)
c.grid(row=2, column= 1, sticky="W", pady=(0,30))
##########################################
mainloop()
