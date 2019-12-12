# Aerosol observations tool

A tool for analysis and plotting different aerosol observations. Current version handles AERONET daily data (All sites). 
The package is still under developments to include and compare other observations including MODIS and in situ measurements. 

## Getting started

### Requirements

- numpy
- pandas
- matplotlib
- plotly

### Installing

Clone the respository and add the dependency to your environment, or just place the repository in your working folder.

### Instructions

See [demo_analysis.ipynb](demo_analysis.ipynb) for data analysis, [demo_plot.ipynb](demo_plot.pynb) for plotting.

Current functions include:

- Extracting AOD, Angstrom Exponent and size distributions from all points data in specific periods and sites
- Calculate average of all sites, filtered by number of records
- Searching sites located in region
- Plotting:
  - Averaged values
  - Time series and size dsitributions at specific sites
  - Two-parameter comparison

## License
This project is licensed under the MIT License
