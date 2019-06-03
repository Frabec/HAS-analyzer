from tkinter import *
from tkinter import filedialog
import os as os


def browse_button():
    global folder_path
    filename=filedialog.askdirectory()
    folder_path.set(filename)

#get in a folder open all the files and stores them in an array, using a double array format
def form_folder_to_arrays(path):
    data_storage= []
    data_storage_counter=0
    for file_names in os.listdir(path):
        #the files containing wavefront information are in wft extension
        if not str.endswith(file_names, ".wft"):
            continue
        f= open(path+'\\'+file_names,'r')
        data_storage.append([])
        for lines in f:
            raw=(lines.split('\t'))
            #remove all the NaN 
            filtered=list(filter(lambda x: not("NaN" in x), raw))
            #convert every float to string
            filtered=list(map(lambda x : float(x), filtered))
            #if list is not empty
            if filtered: 
                data_storage[data_storage_counter].append(filtered)
        data_storage_counter=data_storage_counter+1
    
    return data_storage

def calculate_everything(path_to_folder):
    data=form_folder_to_arrays(path_to_folder)
    #print(data)


root = Tk()
root.title("HAS Analyzer")
root.geometry("500x500")
folder_path = StringVar()
lbl1 = Label(master=root,textvariable=folder_path)
lbl1.grid(row=0, column=2)
button2 = Button(text="Browse folder", command=browse_button)
button2.grid(row=0, column=1)
button3 = Button(text="Do it", command=lambda: calculate_everything(folder_path.get()))
button3.grid(row=0, column=0)
lbl_mean_rms_global_title = Label(master=root, text="Mean of the RMS of the images: ")
lbl_mean_rms_global_title.grid(row=1, column=0, sticky="W")
lbl_rms_rms_global_title = Label(master=root, text="RMS of the RMS of the images: ")
lbl_rms_rms_global_title.grid(row=2, column=0, sticky="W")
lbl_rms_pixel_by_pixel_title = Label(master=root, text="Mean of RMS pixel by pixel: ")
lbl_rms_pixel_by_pixel_title.grid(row=3, column=0, sticky="W")


mainloop()
