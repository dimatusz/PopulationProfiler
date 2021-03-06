# PopulationProfiler

PopulationProfiler – is light-weight cross-platform open-source tool for data analysis in image-based screening experiments. The main idea is to reduce per-cell measurements to per-well distributions, each represented by a histogram. These can be optionally further reduced to sub-type counts based on gating (setting bin ranges) of known control distributions and local adjustments to histogram shape. Such analysis is necessary in a wide variety of applications, e.g. DNA damage assessment using foci intensity distributions, assessment of cell type specific markers, and cell cycle analysis.

The software imports measurements from a simple text file, visualizes population distributions in a compact and comprehensive way, and can create gates for subpopulation classes based on control samples. The simple graphical user interface (GUI) allows selection of multiple csv files with image-based screening data. Each file is treated as a separate plate (i.e. independent experiment) with rows representing cell measurements. One measurement is processed at a time and cells are grouped based on well labels. The measurement is selected by the user from a drop-down list created from the csv file header (first row). The GUI also allows selection of control wells based on the treatment labels. If such labels are not available, the user can select control wells manually. The corresponding data is pooled and stored as a separate record in the output csv file. PopulationProfiler thereafter calculates and displays the distribution of the selected measurement as a histogram for each well. A vector representation of each well’s histogram is saved in the output file, and can be used as input for e.g., cluster analysis, elsewhere. The cell count for each well is also saved as a measure of statistical relevance of population effects.

For more information on PopulationProfiler use go to the manual file.

This software can be cited as:
Matuszewski, D. J., Wählby, C., Puigvert, J. C., Sintorn, I.-M. 
PopulationProfiler: a tool for population analysis and visualization of image-based cell screening data. 
PLoS ONE. (2016) 
