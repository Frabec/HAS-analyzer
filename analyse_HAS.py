from tkinter import *
from tkinter import filedialog
import os as os
import numpy as np


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
#get in a folder open all the files and stores them in an array, using a double array format
def form_folder_to_arrays(path, wavelength):
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
            modified=list(map(lambda x: wavelength*float(x) if not("NaN" in x) else 0., raw))
            #if list is not empty
            new_image.append(modified)
        #Now data_storage contains a list of images of same xlength and ylength, but we have converted the NaN to zeros

        data_storage.append(new_image)
        
    return data_storage

def calculate_RMS_images(data): 
    RMS_images=[None]*len(data)
    for i,image in enumerate(data):
        #We delete the 0 because they were NaN
        filtered_image=[list(filter(lambda x: x!=0., row)) for row in image]
        RMS_images[i]=np.std([pixel for row in filtered_image for pixel in row])
    return RMS_images

def calculate_RMS_pixel_by_pixel(data):
    RMS_pixels=np.std(data, axis=0)
    RMS_pixels=[list(filter(lambda x: x!=0., row)) for row in RMS_pixels]
    return RMS_pixels

def calculate_everything(path_to_folder, wavelength_str):
    wavelength=int(wavelength_str)
    data=form_folder_to_arrays(path_to_folder, wavelength)
    RMS_images=calculate_RMS_images(data)
    global mean_RMS
    mean_RMS.set(np.mean(RMS_images))
    global RMS_RMS
    RMS_RMS.set(np.std(RMS_images))
    RMS_pixel_by_pixel=calculate_RMS_pixel_by_pixel(data)
    print(RMS_pixel_by_pixel)
    global RMS_pixels
    RMS_pixels.set(np.mean([pixel for row in RMS_pixel_by_pixel for pixel in row]))


root = Tk()
root.title("HAS Analyzer")
root.geometry("600x300")
folder_path = StringVar()
mean_RMS= DoubleVar()
RMS_RMS = DoubleVar()
RMS_pixels =DoubleVar()
Wavelength = DoubleVar()
Wavelength.set(800.0)
lbl1 = Label(master=root,textvariable=folder_path)
lbl1.grid(row=0, column=2)
button2 = Button(text="Browse folder", command=browse_button)
button2.grid(row=0, column=1)
button3 = Button(text="Do it", state="disabled",command=lambda: calculate_everything(folder_path.get(), Wavelength.get()))
button3.grid(row=0, column=0)
#titles
lbl_mean_rms_global_title = Label(master=root, text="Mean of the RMS of the images(nm): ")
lbl_mean_rms_global_title.grid(row=2, column=0, sticky="W",pady=(50,10))
lbl_rms_rms_global_title = Label(master=root, text="RMS of the RMS of the images(nm): ")
lbl_rms_rms_global_title.grid(row=3, column=0, sticky="W",pady=10)
lbl_rms_pixel_by_pixel_title = Label(master=root, text="Mean of RMS pixel by pixel(nm): ")
lbl_rms_pixel_by_pixel_title.grid(row=4, column=0, sticky="W",pady=10)
lbl_wavelength = Label(master=root, text="Wavelength(nm): ")
lbl_wavelength.grid(row=1, column=0, sticky="E", pady=(20,0))
entry_wavelength = Entry(master=root, textvariable=Wavelength)
entry_wavelength.grid(row=1, column=1, sticky="W", pady=(20,0))
#values
lbl_mean_rms_global_value = Label(master=root, textvariable=mean_RMS)
lbl_mean_rms_global_value.grid(row=2, column=1, sticky="W",pady=(50,10))
lbl_rms_rms_global_value = Label(master=root, textvariable=RMS_RMS)
lbl_rms_rms_global_value.grid(row=3, column=1, sticky="W",pady=10)
lbl_rms_pixel_by_pixel_value = Label(master=root, textvariable=RMS_pixels)
lbl_rms_pixel_by_pixel_value.grid(row=4, column=1, sticky="W",pady=10)

mainloop()
