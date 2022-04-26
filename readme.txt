1. voigtfit

This code is written to deconvolute IR spectra to two or three peaks automatically.
Here, explanation of this program is following:

1) Click 'Open files' button to load your spectra data. (you can open multiple files at once)
They should be csv file and first column should contain wavenumber data and second column should contain intensity data.
If you use PerkinElmer software, you don't need to care about data file type.

2) Click 'loaded files' button and choose one.

3) Set Range and peak positions for spectrum deconvolution.
Range : left one should has smaller value
peak positions : wavenumber data should be written on decreasing order. (ex: 1752,1720,1710)
When you write peak position, do not use space key.
Be careful that this program allows only 1, 2, 3 peaks.
I thought there will be much uncertainty on deconvolution with 4 or more peaks, so I did not add deconvolution function for 4 or more peaks.

4) If you want to see spectrum with written range, you can do it by clicking 'Draw graph' button.
Also, if you click 'Draw all' button, all loaded spectra will be drawn in one figure.

5) For deconvolution of selected file, click 'Data Fit' button.
Then filename, peak widths, peak areas, peak positions, and background(constant) will be printed.

If you click 'Fit all data' button, all loaded files will be deconvoluted and the results will be printed one by one

6) You can save figure by using save button on toolbar (located on bottom of this program)

----------------------------------------------------------------------------------

2. get2Dfig

This code is written to get figures of selected range of 2DIR spectra automatically.
Explanation of this code is following:

1) Click "Open files" button to load your data (it should be .dat file)
You can open multiple files at once.

2) Click "loaded files" button and select one of files and click "Plot raw data" to see full spectrum

3) Determine w_m (abscissa) range and w_t (ordinate) range and the number of contour lines.
Colormap of contour plot can also be modified by choosing one option of colormap button

4) After 3) process, click "Plot 2D spectrum" and then 2D spectrum of selected range will be drawn.
If you want to save this figure (2D spectrum only), just click "save 2D spectrum" button.

5) For repeatation 2)~4) processes at once, click "save all 2D spectra" button.
All files will be saved as png files and have same range determined at 3) process.

6) When you click the 2D spectrum, horizontal and vertical slice graphs will be shown.
mouse position is automatically changed to coordinates of spectrum and then slice graphs at the point are drawn.

-----------------------------------------------------------------------------------

3. phasing

This code is written for phasing 2DIR data.
Some functions are not embodied yet, so explanation of this code will be added later.

(Now, only FFT, interpolation, and single phasing of data are embodied..)