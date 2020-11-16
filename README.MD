# Super Netball 2020: Super Shot Simulations

Placeholder readme for repo.



## Code

The following section provides details on various aspects of the code used in this project. All Python code should be run from it's own directory as the base directory, while all R code should be run from the R Project directory.

### Python

*Note that the Python code for this project was run Python version 3.7.*

The Python code associated with this project includes a number of dependencies that likely come with the Anaconda Python distribution, so this may be an easy way to get started. Alternatively, and 'environment.yml' file is provided that can be used to setup a Conda environment with the relevant dependencies.

#### superShotSimulator.py

This is the main piece of Python code for analysis in this project. It pulls in the data from the extracted .json files (see 'getChampionData_SuperNetball.R' below) and runs the simulations of the Super Shot period.

#### ssn202DataHelper.py

This is a script of accessory functions that help in getting the data from the Champion Data .json files into the Python environment.

#### ssn202FigHelper.py

This is a script of accessory functions that help in generating figures from the results compiled by 'superShotSimulator.py'.

### R

*Note that the R code for this project was run on R version 4.0.2.*

#### getChampionData_SuperNetball.R

This script was used to access the Champion Data match centre for the 2020 Super Netball regular season via the [SuperNetballR package](https://github.com/SteveLane/superNetballR). The code is fairly straight forward, and could be easily adapted to get data from the 2020 finals series or other Super Netball seasons by changing the competition ID. We recommend reviewing the SuperNetballR package documentation for appropriate usage. The script also has the dependencies of the {dplyr} and {jsonlite} packages. The script might take a few minutes or so — so hit run and go grab yourself a cup of coffee.

## Data

### Raw Data

As noted above, R code is used to access and store the Champion Data match centre outputs for the Super Netball 2020 season as .json files. A .csv file 'squadLists' is also included as raw data to supplement the loading in of this data and appropriately allocate players to their relevant squads.

