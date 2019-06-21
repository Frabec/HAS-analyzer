# Wavefront analyzer

Wavefront analyzer can analyze wavefront data acquired with a HASO, it only analyzes already processed .has files. Has analyzer has a GUI and can do several operations. 



## Requirements

To use Wavefront analyzer **[python 3](https://www.python.org/) ** must be installed as well as the **numpy** and **matplotlib** libraries. 

## Exporting properly the .has files 

If we are acquiring HASO data during a scan once the scan is finished, create a called **HAS** in the scan directory and export all the data there. If you acquired some HASO data for Scan 1 on 01/01/2019 export the .has files in the folder *N:\data\Y2019\01-Jan\19_0101\scans\Scan001\HAS*. It is important to respect this file arborescence if you want the Wavefront analyzer software to work correctly

## Preprocessing the .has files.

In order to be able to analyze the wavefront, the .has files must be processed with the labview program HAS analyzer located at *D:\Server\10_Software\ajg builds\HAS analyzer* in the appserver. This program will analyze a folder containing .has files (slopes) and output for each .has file two files : a .wft file containing a 2D map of the wavefront, a .zrn file containing the first 32 Zernike coefficients of the wavefront (on a single line separated by tab).  The HAS analyzer labview program GUI is like this

![Tony software](https://github.com/Frabec/Wavefront-analyzer/blob/images/tony.png?raw=true)



This scan will create a subdirectory called analysis in the directory of your HAS folder. Then inside the analysis directory it will create a subdirectory with the provided *analysis folder name* (filtered3 in the picture above). If you want to filter the wavefront please select *Zonal w filters* for *recon type*

#### Naming your analysis folder correctly. 

The Wavefront analyzer program works better if you name your analysis folder using the following convention.

| Wavefront exported | Name of analysis folder |
| :----------------: | :---------------------: |
|      Z1 only       |          tiltx          |
|      Z2 only       |          tilty          |
|     Z1 and Z2      |          tilt           |
|      Z3 only       |          focus          |
|    Z3 and above    |        filtered2        |
|    Z4 and above    |        filtered3        |

You can extract only Z2 component of the wavefront by selecting  *Zonal w filters* for *recon type* and ticking all the boxes except *curv*. 

## Wavefront analyzer

![initial_py](https://github.com/Frabec/Wavefront-analyzer/blob/images/python_intial.PNG?raw=true)



There are 4 different options for the software : 

##### Single folder

Click *Browse folder* and select the folder containing the *.wft* files. Then click *Do it*, the software will show on the right statistics about the wavefronts stored in the selected directory. Click *Show map of wavefront* to show a map of the RMS pixel by pixel.  The different statistics are : 

- **Mean of the RMS of images (nm)** : For each shot, the program calculates the RMS of the wavefront, then it takes the mean of the RMS over all shots
- **RMS of RMS of the inages (nm)**:  For each shot, the program calculates the RMS of the wavefront, then it takes the RMS of the RMS over all shots.
- **Mean of RMS pixel by pixel (nm)**: For each pixel of the wavefront the software calculates the RMS of the value of the pixel over all the shots. The software computes by doing so a "RMS image", that you can see by clicking on *Show map of wavefront*, then it computes a mean over all pixels.



##### Browse recursively

Click *Browse folder* and select a folder. The software will explore the sub directories recursively and find all the folder containing .wft files. It will then output a .txt file located in the selected directory containing the path of the subdirectories containing .wft files and statistics about those files. 



##### Browse folder recursively respecting the scan file arborescence. 

Click *Browse folder* and select the folder containing all the scans *e.g* **N:\data\Y2019\01-Jan\19_0101\scans** if  you named the analysis folder correctly (*c.f* table above) and respected the correct file arborescence the software will output a .txt file containing all the wavefront statistics. If the folder is misnamed a warning line will be printed in the python console

##### Make file for masterlog

It is the same feature as *Browse folder recursively respecting the scan file arborescence.* except the software will make a directory called *HASO_scan_files*. In this directory you will find a .txt file for each scan,  the .txt file   will have 1 column for each HASO data feature (*c.f* table below ) and 1 row for each scan shot. You can then easily add columns to masterlog using those files.

| HASO data feature |                         Description                         |
| :---------------: | :---------------------------------------------------------: |
|    HASO_tiltx     |     RMS of each .wft file in the analysis folder tiltx      |
|    HASO_tilty     |     RMS of each .wft file in the analysis folder tilty      |
|    HASO_focus     |     RMS of each .wft file in the analysis folder focus      |
|      HASO_Z1      | Value of the 1st Zernike coefficient found in the .zrn file |
|      HASO_Z2      | Value of the 2nd Zernike coefficient found in the .zrn file |
|      HASO_Z3      | Value of the 3rd Zernike coefficient found in the .zrn file |
| HASO_higher_order |        RMS of each .wft file in the folder filtered3        |

