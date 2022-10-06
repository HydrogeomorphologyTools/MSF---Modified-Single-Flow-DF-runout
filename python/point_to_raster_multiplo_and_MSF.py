# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 10:02:06 2017

@author: stefano
"""
# Name: PointToRaster_Ex_02.py
# Description: Converts point features to a raster dataset.

#%% Import system modules
import arcpy
from arcpy import env
from arcpy.sa import *
import os
arcpy.env.overwriteOutput = True
#
#                              
# Set the workspace for the ListFeatureClass function
#
res = "3m"
print "Analisys resolution is "+res
#
env.workspace = "E:/PhD/assegno/Pescara_PC/simulazioni/"+res+"/shape_source_split/"
msfdir = "E:/PhD/assegno/Pescara_PC/simulazioni/"+res+"/MSF/" # folder to store single MSF results
rasterdir = "E:/PhD/assegno/Pescara_PC/simulazioni/"+res+"/raster_source_split"
rasteralldir = "E:/PhD/assegno/Pescara_PC/simulazioni/"+res+"/raster_source_all"
pqlimalldir = "E:/PhD/assegno/Pescara_PC/simulazioni/"+res+"/pq_lim_all"
#
#%% Comment this section if the export to single features is not needed
#
shp = "E:/PhD/assegno/Pescara_PC/simulazioni/shape/PuntiInizioDF_5m_q.shp"
#
#%%
#Create folder for the analysis, removed at the end
if not os.path.exists(env.workspace):
    os.makedirs(env.workspace)
if not os.path.exists(msfdir):
    os.makedirs(msfdir)
if not os.path.exists(rasterdir):
    os.makedirs(rasterdir)
if not os.path.exists(rasteralldir):
    os.makedirs(rasteralldir)
if not os.path.exists(pqlimalldir):
    os.makedirs(pqlimalldir)
#
#
outws = env.workspace

with arcpy.da.SearchCursor(shp, ["SHAPE@","Id","Source"]) as cursor:
    for row in cursor:
        outfc = os.path.join(outws, "Id_" + str(row[1]))
        #Copy the single feature
        arcpy.CopyFeatures_management(row[0], outfc)
        #Add missing field/s
        arcpy.AddField_management((outfc+".shp"), "Source", "SHORT") # Add only Source field cause Id field should already exist !!!
        #Calculate/populate the fields
        arcpy.CalculateField_management((outfc+".shp"), "Id",row[1],"PYTHON_9.3")
        arcpy.CalculateField_management((outfc+".shp"), "Source",row[2],"PYTHON_9.3")
        #

# Use the ListFeatureClasses function to return a list of 
#  all shapefiles.
#
fcList = arcpy.ListFeatureClasses() # lists the features found in the env.workspace folder
#
#
DTM = "E:/PhD/assegno/Pescara_PC/simulazioni/"+res+"/fill.tif" # provide a default value if unspecified
extentRaster = Raster(DTM)
arcpy.env.extent = extentRaster.extent
#
description = arcpy.Describe(DTM)  
cellSize = description.children[0].meanCellHeight
print "cellsize = " + str(cellSize)
#
# Set local variables for Point to Raster Conversion
valField = "Source"
assignmentType = "MOST_FREQUENT"
priorityField = ""
#
raster_src_all = "E:/PhD/assegno/Pescara_PC/simulazioni/"+res+"/raster_source_all/ras_src_all"
#
# Convert shapefile point to raster to create a unique raster to run also in Taudem Avalanche Runout as source file
arcpy.PointToRaster_conversion(shp,valField, raster_src_all, assignmentType, priorityField, cellSize)
#
#local variables
Output_drop_raster = ""
fdir = msfdir + "fdir_" + ".tif"
fdir_deg = msfdir + "fdir_deg_" + ".tif"
pq_lim_all = "E:/PhD/assegno/Pescara_PC/simulazioni/"+res+"/pq_lim_all/pq_lim_all.tif"

# Process: Flow Direction
arcpy.gp.FlowDirection_sa(DTM, fdir, "NORMAL", Output_drop_raster)
  
# Process: Raster Calculator
out_fdir_deg = Con(Log2(fdir) < 6, (Log2(fdir) + 2) * 45, (Log2(fdir) - 6) * 45)
out_fdir_deg.save(fdir_deg) 

pq_list = []
    
for fc in fcList:
    outRaster = rasterdir + "/" + fc.rstrip(".shp") #Important!!! Here avoid extension .tif cause point to raster tool can have extent problem with GeoTIFF adding zerovalues to a variable extent, and setnull does not work automatically in that case
    arcpy.PointToRaster_conversion(fc, valField, outRaster, 
                               assignmentType, priorityField, cellSize)
    #
    # Script arguments
    Source_int_null_tif = outRaster
    #
    pq_lim = msfdir + "pq_lim_" + fc.rstrip(".shp") + ".tif"
    #
    H_L_threshold =  "0.19" 
    #
    # Local variables:
    Output_backlink_raster = ""
    PathAll_Sour1 = msfdir + "PathAll_Sour1_"+fc.rstrip(".shp") + ".tif"
    Output_backlink_raster__2_ = ""
    start_z = msfdir + "start_z_" + fc.rstrip(".shp") + ".tif"
    hi = msfdir + "hi_" + fc.rstrip(".shp") + ".tif"
    li = msfdir + "li_" + fc.rstrip(".shp") + ".tif"
    h_l = msfdir + "h_l_" + fc.rstrip(".shp") + ".tif"
    h_l_lim = msfdir + "h_l_lim_" + fc.rstrip(".shp") + ".tif"
    fri = msfdir + "fri_" + fc.rstrip(".shp") + ".tif"
    pqi = msfdir + "pqi_" + fc.rstrip(".shp") + ".tif"
    
    # Process: Path Distance Allocation (1)
    out_li = PathAllocation(Source_int_null_tif, "", "", fdir_deg, HfForward(1.0, 1.0), "", VfBinary(1.0, -30, 30), "", "", "Value", li, Output_backlink_raster)
    out_li.save(start_z)
    
    # Process: Path Distance Allocation (2)
    out_fri = PathAllocation(Source_int_null_tif, "", "", fdir_deg, HfLinear(0.5, 90, 0.011111), "", VfBinary(1.0, -30, 30), "", "", "Value", fri, Output_backlink_raster__2_)
    out_fri.save(PathAll_Sour1)
    
    # Process: Raster Calculator (3)
    out_hi = Raster(start_z) - Raster(DTM)
    out_hi.save(hi)
    
    # Process: Raster Calculator (4)
    out_h_l = Raster(hi) / Raster(li)
    out_h_l.save(h_l)
    
    # Process: Raster Calculator (5)
    out_h_l_lim = Con(h_l >= float(H_L_threshold), h_l)
    out_h_l_lim.save(h_l_lim)
    #
    
    # Process: Raster Calculator (2)
    out_pqi = Raster(li) / Raster(fri)
    out_pqi.save(pqi)
    #
    
    # Process: Raster Calculator (6)
    out_pq_lim = Raster(h_l_lim) + Raster(pqi) - Raster(h_l_lim)
    out_pq_lim.save(pq_lim)
    pq_list.append(pq_lim)
    #
    print fc.rstrip(".shp")
#
# Execute CellStatistics
outCellStatistics = CellStatistics(pq_list, "MAXIMUM", "DATA")
# Save the CellSatistics output 
outCellStatistics.save(pq_lim_all)
#
#
#                          