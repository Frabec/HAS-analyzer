from tkinter import *
from tkinter import filedialog
import os as os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import re
from matplotlib import rcParams
import threading as thr

class Scan: 
    def __init__(self):
        self.all= "NaN"
        self.filtered2= "NaN"
        self.filtered3= "NaN"
        self.tilt= "NaN"
        self.focus= "NaN"
        self.tiltx= "NaN"
        self.tilty= "NaN"
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
#get in a folder open all the wavefront (.wft) files and stores them in an array, using a double array format
def from_folder_to_arrays(path):
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

#get in a folder open all the zernike files (.zrn) and stores the first 3 coeffs of each shot, using a double array format
def from_folder_to_arrays_zernike(path):
    storage=[]
    for file_name in os.listdir(path): 
        if not str.endswith(file_name, ".zrn"):
            continue
        f=open(os.path.join(path, file_name), 'r')
        raw=f.readline()
        split=raw.split('\t')
        storage.append(split[0:3])
        f.close()
    return storage

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

def do_it_action(path_to_folder, mode):
    if mode.get()!=3: 
        thread1= thr.Thread(target=calculate_everything, args=(path_to_folder, mode.get()))
        thread1.start()
    #need to create masterlog like txt file
    else:
        thread1=thr.Thread(target=add_columns_to_masterlog, args=(path_to_folder,))
        thread1.start()

def calculate_everything(path_to_folder, mode):
    global RMS_map
    global mean_RMS
    global RMS_RMS
    global button4
    global RMS_pixels
    #single file
    if mode==0:
        data=from_folder_to_arrays(path_to_folder)
        RMS_images=calculate_RMS_images(data)
        mean_RMS.set(np.mean(RMS_images))
        RMS_RMS.set(np.std(RMS_images))
        RMS_pixel_by_pixel=calculate_RMS_pixel_by_pixel(data)
        button4.config(state="normal")
        RMS_pixels.set(np.mean([pixel for row in RMS_pixel_by_pixel for pixel in row]))
        return
    #browse without structure
    #There is no mean wavefront to plot
    button4.config(state="disabled")
    #Don't show any data it is only for single files
    mean_RMS.set(None)
    RMS_RMS.set(None)
    RMS_pixels.set(None)
    if mode==1:
        write_file= open(path_to_folder+"/data.txt","w")
        write_file.write("Format of data:\nPath\nMean of RMS\tRMS of RMS\tRMS pixel by pixel\n")
        for root,_,_ in os.walk(path_to_folder, topdown="false"):
            #if there are files
            data=from_folder_to_arrays(root)
            if data:
                RMS_images=calculate_RMS_images(data)
                local_mean_RMS= np.mean(RMS_images)
                local_RMS_RMS=np.std(RMS_images)
                local_RMS_pixels_list=calculate_RMS_pixel_by_pixel(data)
                local_RMS_pixels=(np.mean([pixel for row in local_RMS_pixels_list for pixel in row]))
                write_file.write(root[len(path_to_folder):]+"\n")
                write_file.write(str(local_mean_RMS)+"\t"+str(local_RMS_RMS)+"\t"+str(local_RMS_pixels)+"\n")
        write_file.close()
    #Browse with order
    elif mode==2: 
         #dictionnnary Key= scan number, value Scan class associated to scan number 'Key'
        data_dict={}
        for entry in os.scandir(path_to_folder):
            if entry.is_dir() and ("Scan" in entry.name):
                analysis_path=os.path.join(entry.path, "HAS", "analysis")
                #we make sure we have an HAS\analysis folder
                if not os.path.exists(analysis_path):
                    continue
                for in_scan in os.scandir(analysis_path):
                    #We only send folders to from_folders_to_array
                    if not os.path.isdir(in_scan.path):
                        continue
                    data=from_folder_to_arrays(in_scan.path)
                    if data :
                        #store into the dictionnary the data point
                        m=re.search("[0-9]+", entry.name)
                        scan_number=m.group(0)
                        RMS_images=calculate_RMS_images(data)
                        local_RMS_RMS=str(np.std(RMS_images))
                        if scan_number not in data_dict:
                            data_dict[scan_number]=Scan()
                        if in_scan.name=="all":
                            data_dict[scan_number].all=local_RMS_RMS
                        elif in_scan.name=="filtered2":
                            data_dict[scan_number].filtered2=local_RMS_RMS
                        elif in_scan.name=="filtered3":
                            data_dict[scan_number].filtered3=local_RMS_RMS
                        elif in_scan.name=="tilt":
                            data_dict[scan_number].tilt=local_RMS_RMS
                        elif in_scan.name=="focus":
                            data_dict[scan_number].focus=local_RMS_RMS
                        elif in_scan.name=="tiltx":
                            data_dict[scan_number].tiltx=local_RMS_RMS
                        elif in_scan.name=="tilty":
                            data_dict[scan_number].tilty=local_RMS_RMS
                        else:
                            print("Warning scan "+scan_number+ " misnammed folder!!!! : "+ in_scan.name)
        #Now write everything into the text file
        #Format : 
        #Scan number    RMS_of_RMS_all  RMS_of_RMS_all-tilt,tip RMS_of_RMS_all-tilt,tip,focus   RMS_of_RMS_tilt,tip    RMS_of_RMS_focus
        write_file= open(path_to_folder+"/data_formated.txt","w")
        write_file.write("Format of data: Scan number\tRMS_of_RMS_all\tRMS_of_RMS_all-tilt,tip\tRMS_of_RMS_all-tilt,tip,focus\tRMS_of_RMS_tilt,tip\tRMS_of_RMS_tiltx\tRMS_of_RMS_tilty\tRMS_of_RMS_focus\n")
        for number, scan in data_dict.items():
            write_file.write(number+"\t"+scan.all+"\t"+scan.filtered2+"\t"+scan.filtered3+"\t"+scan.tilt+"\t"+scan.tiltx+"\t"+scan.tilty+"\t"+scan.focus+"\n")
        write_file.close()
    else : 
        print("Non recongnized analysis mode")
#plot image map of RMS
def add_columns_to_masterlog(path):
    useless_names=["all","tilt","filtered2","filtered3"]
    folder= os.path.join(path, "HASO_scan_files")
    os.mkdir(folder)
    for entry in os.scandir(path):
        if entry.is_dir() and ("Scan" in entry.name):
            scan_data=Scan()
            #contains empty columns
            empty=["tiltx", "tilty", "focus", "filtered3"]
            non_empty=[]
            analysis_path=os.path.join(entry.path, "HAS", "analysis")
            #If we have a HAS\analysis folder inside the scan folder"
            if os.path.exists(analysis_path):
                for in_scan in os.scandir(analysis_path):
                    #We send to from_folder_to_arrays only a folder not a file
                    if os.path.isdir(in_scan):
                        data=from_folder_to_arrays(in_scan.path)
                        #zernike decompostion isn't influenced by the filters
                        zernike_data= from_folder_to_arrays_zernike(in_scan.path)
                    else :
                        continue
                    
                    if in_scan.name=="tiltx":
                        if data:
                            scan_data.tiltx=calculate_RMS_images(data)
                            empty.remove("tiltx")
                            non_empty.append("tiltx")
                    elif in_scan.name=="tilty":
                        if data:
                            scan_data.tilty=calculate_RMS_images(data)
                            empty.remove("tilty")
                            non_empty.append("tilty")
                    elif in_scan.name=="focus":
                        if data:
                            scan_data.focus=calculate_RMS_images(data)
                            empty.remove("focus")
                            non_empty.append("focus")
                    elif in_scan.name=="filtered3":
                        if data:
                            scan_data.filtered3=calculate_RMS_images(data)
                            empty.remove("filtered3")
                            non_empty.append("filtered3")
                    elif in_scan.name in useless_names:
                        continue
                    else : 
                        print("Warning scan "+entry.name+ " misnammed folder!!!!")
                if non_empty:
                    length=len(getattr(scan_data,non_empty[0]))
                    for _,attribute in enumerate(empty):
                        setattr(scan_data,attribute,["NaN"]*length)
                    write_scan_file(entry.name, scan_data, zernike_data,folder)

#create scan file in directory scan_files to add to masterlog
def write_scan_file(scan_name, scan_data, zernike_data,dir_path):
    scan_file=open(os.path.join(dir_path,scan_name+"_HASO"+".txt"), "w")
    scan_file.write("HASO_tiltx\tHASO_tilty\tHASO_focus\tHASO_Z1\tHASO_Z2\tHASO_Z3\tHASO_higher_order\n")
    for i,_ in enumerate(scan_data.filtered3):
        scan_file.write(str(scan_data.tiltx[i])+"\t"+str(scan_data.tilty[i])+"\t"+str(scan_data.focus[i])+"\t"+zernike_data[i][0]+"\t"+zernike_data[i][1]+"\t"+zernike_data[i][2]+"\t"+str(scan_data.filtered3[i])+"\n")
    scan_file.close()

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

############################################################################################################
#Start
root = Tk()
root.title("Wavefront analyzer")
root.geometry("{}x{}".format(900,350))
#######################################
###           Global vars           ###
#######################################
folder_path = StringVar()
mean_RMS= DoubleVar()
RMS_RMS = DoubleVar()
RMS_pixels =DoubleVar()
analyzing_mode= IntVar()
analyzing_mode.set(0)
#store RMS map
RMS_map=[]
########################################
###               GUI                ###
########################################

################Frames##################
root.grid_rowconfigure(0,weight=1)
root.grid_rowconfigure(1,weight=1)
root.grid_columnconfigure(0,weight=1)
root.grid_columnconfigure(1,weight=1)
top_frame= Frame(master=root, width=800, height=30)
left_frame=Frame(master=root, width=300, height=300)
right_frame=Frame(master=root, width=500, height=300)

top_frame.grid(row=0,columnspan=2,sticky="nsew")
left_frame.grid(row=1, column=0, sticky="w")
right_frame.grid(row=1, column=1,stick="w")
top_frame.pack_propagate(False)
left_frame.pack_propagate(False)
right_frame.grid_propagate(False)
#Packing in top frame
button3 = Button(top_frame, text="Do it", state="disabled",command=lambda: do_it_action(folder_path.get(), analyzing_mode))
button3.pack(side=LEFT, fill=Y, padx=(0,50))
button2 = Button(top_frame, text="Browse folder", command=browse_button)
button2.pack(side=LEFT, fill=Y)
lbl1 = Label(top_frame,textvariable=folder_path)
lbl1.pack(side=LEFT)

#Packing in left frame
listbox_lbl=Label(left_frame, text="Select analysis mode")
listbox_lbl.pack(fill=X, pady=(50,0))
modes_of_analyzing = ["Single folder", "Browse recursively", "Browse recursively respecting the scan file arborescence", "Make file for masterlog"]
for val, modes in enumerate(modes_of_analyzing):
    Radiobutton(left_frame, text=modes, variable=analyzing_mode, value=val, indicatoron=0).pack(fill=X)


    #button
button4 = Button(master=right_frame,text="Show map of wavefront", state="disabled", command=plotRMS)
button4.grid(row=0, column=0,pady=(50,0),padx=(10,0))
    #titles
lbl_mean_rms_global_title = Label(master=right_frame, text="Mean of the RMS of the images(nm): ")
lbl_mean_rms_global_title.grid(row=1, column=0, sticky="e",pady=10,padx=(50,0))
lbl_rms_rms_global_title = Label(master=right_frame, text="RMS of the RMS of the images(nm): ")
lbl_rms_rms_global_title.grid(row=2, column=0, sticky="e",pady=10,padx=(50,0))
lbl_rms_pixel_by_pixel_title = Label(master=right_frame, text="Mean of RMS pixel by pixel(nm): ")
lbl_rms_pixel_by_pixel_title.grid(row=3, column=0, sticky="e",pady=10,padx=(50,0))
    #values
lbl_mean_rms_global_value = Label(master=right_frame, textvariable=mean_RMS)
lbl_mean_rms_global_value.grid(row=1, column=1, sticky="e",pady=10)
lbl_rms_rms_global_value = Label(master=right_frame, textvariable=RMS_RMS)
lbl_rms_rms_global_value.grid(row=2, column=1, sticky="e",pady=10)
lbl_rms_pixel_by_pixel_value = Label(master=right_frame, textvariable=RMS_pixels)
lbl_rms_pixel_by_pixel_value.grid(row=3, column=1, sticky="e",pady=10)

#########################################

mainloop()
