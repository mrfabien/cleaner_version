# Libraries
library(tidyverse)
library(magrittr)
library(vegan)
library(corrplot)
library(codep)
library(FactoMineR)
library(factoextra)
library(dendextend)
library(ggplot2)
library(readxl)

setwd('~/Documents/GitHub/master-project-cleaned/pre_processing/cluster')

# Presence/absence ----------------------------------------
data_main <- read_csv("max_all_storms_pca.csv") # read-in data

#-------------------------------------------------------------------------
# Elbow for number of clusters

PCA_wind <- PCA(data_main, graph= TRUE)

fviz_screeplot(PCA_wind, ncp=10)
