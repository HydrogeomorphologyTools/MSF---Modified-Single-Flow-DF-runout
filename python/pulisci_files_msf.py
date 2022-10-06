# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 14:36:16 2017

@author: stefano
"""
import shutil

res = "10m"
#
msfdir = "E:/PhD/assegno/CSAsN_PC/analisi/"+res+"/MSF/" # folder to store single MSF results
rasterdir = "E:/PhD/assegno/CSAsN_PC/analisi/"+res+"/raster_source_split"

shutil.rmtree(msfdir)
shutil.rmtree(rasterdir)
#