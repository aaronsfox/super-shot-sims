#This code is currently set to grab matches from the 2020 Suncorp Super
#Netball season using the superNetballR package. As such it needs to be
#installed using:

# library(remotes)

# remotes::install_github("SteveLane/superNetballR")

#Load appropriate packages
library(dplyr)
library(superNetballR)
library(jsonlite)

#Download matches and save as .json

#Set 2020 competition ID
compID = "11108"

#Loop through rounds
for (rr in 1:14) {

  #Set round to grab based on loop iteration
  getRound = rr
  
  #Loop through the four matches for the round and save as .json
  for (mm in 1:4) {
    #Download match
    matchData <- downloadMatch(compID,getRound,mm)
    #Save as .json
    write_json(matchData,paste("Data/SuperNetball2020_CD/r",getRound,"_g",mm,"_SSN2020.json",sep=""))
  }
  
}

##### TODO: set as relevant loop when comp complete
#NOTE: an error 'please install xml2 package' will occur with invalid match numbers