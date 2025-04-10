# -*- coding: utf-8 -*-

# This file is part of the MSF - Modified Single Flow DF runout Model toolbox.
#
# MSF - Modified Single Flow DF runout Model is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2.
#
# MSF - Modified Single Flow DF runout Model is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License (version 2)
# along with this program (check the LICENSE file in the repository).
# If not, see <https://www.gnu.org/licenses/old-licenses/gpl-2.0.html>.

"""
Created on Mon Mar 13 10:02:06 2017
Updated on Thu Feb 27 12:22:31 2025

@author: stefano.crema@cnr.it
"""
# Name: PointToRaster_Ex_02.py (or a more descriptive name if desired)
# Description: Converts multiple point features (potential debris flow sources)
#              to individual raster datasets, runs the MSF model separately for each,
#              and then combines the results retaining the maximum potential impact
#              (pqlim) value in any overlapping runout areas.
#              **Requires Esri ArcGIS Desktop/Pro with Spatial Analyst Extension.**

# %% Import system modules
import arcpy # Requires Esri ArcGIS installation with ArcPy
from arcpy import env
from arcpy.sa import * # Requires Spatial Analyst Extension
import os

# Ensure overwriting is allowed (useful for rerunning the script)
arcpy.env.overwriteOutput = True

# ---------------------------------------------------------------------------
# Configuration - SET YOUR PATHS AND PARAMETERS HERE
# ---------------------------------------------------------------------------

# Set the analysis resolution (e.g., "3m", "5m", "10m") - Ensure DEM matches!
res = "3m"
print("Analysis resolution is " + res)

# Define Base Workspace and Output Folders - *** MODIFY THESE PATHS ***
# It's recommended to use relative paths or configure paths externally if possible.
base_path = "C:/test/simulazioni/" + res + "/"
env.workspace = os.path.join(base_path, "main_folder") # Main working folder for intermediate shapefiles
msfdir = os.path.join(base_path, "MSF") # Folder to store single MSF results
rasterdir = os.path.join(base_path, "raster_source_split") # Intermediate rasters for each point
rasteralldir = os.path.join(base_path, "raster_source_all") # Optional: Combined source raster
pqlimalldir = os.path.join(base_path, "pq_lim_all") # Final combined pq_lim output

# Input Shapefile containing source points - *** MODIFY THIS PATH ***
shp = "C:/test/simulazioni/shape/PuntiInizioDF.shp"
# Required fields in shapefile: 'Id' (Unique Integer ID), 'Source' (Short Integer, typically 1)

# Input Digital Elevation Model (DEM) - *** MODIFY THIS PATH ***
DTM = os.path.join(base_path, "dtm_fill.tif") # Assumes DEM is filled

# Model Parameters
H_L_threshold = "0.19" # Threshold for H/L ratio (mobility) - adjust as needed

# ---------------------------------------------------------------------------
# Setup: Create directories if they don't exist
# ---------------------------------------------------------------------------
dirs_to_create = [env.workspace, msfdir, rasterdir, rasteralldir, pqlimalldir]
for d in dirs_to_create:
    if not os.path.exists(d):
        try:
            os.makedirs(d)
            print("Created directory: " + d)
        except OSError as e:
            print("Error creating directory {}: {}".format(d, e))
            # Consider exiting if directory creation fails for critical folders
            # sys.exit() # Uncomment to exit if creation fails

# ---------------------------------------------------------------------------
# Part 1: Split input shapefile into individual features (Optional step)
# ---------------------------------------------------------------------------
# This section creates separate shapefiles for each point in the input 'shp'.
# If you already have individual source shapefiles or rasters, you might adapt the script.
print("Splitting input features...")
try:
    # Check if required fields exist
    field_names = [f.name for f in arcpy.ListFields(shp)]
    if "Id" not in field_names or "Source" not in field_names:
        raise ValueError("Input shapefile must contain 'Id' and 'Source' fields.")

    with arcpy.da.SearchCursor(shp, ["SHAPE@", "Id", "Source"]) as cursor:
        for row in cursor:
            # Ensure Id is suitable for filename (convert to string)
            feature_id_str = str(row[1])
            # Define output feature class path (within env.workspace)
            outfc_name = "Id_" + feature_id_str + ".shp"
            outfc_path = os.path.join(env.workspace, outfc_name)

            # Copy the single feature geometry
            arcpy.CopyFeatures_management(row[0], outfc_path)

            # Add 'Source' field if it wasn't copied automatically (unlikely but safe check)
            if "Source" not in [f.name for f in arcpy.ListFields(outfc_path)]:
                 arcpy.AddField_management(outfc_path, "Source", "SHORT")

            # Calculate/populate the fields ('Id' might already be present from OBJECTID/FID)
            # Using CalculateField ensures the correct values from the original feature are present
            # Note: Check if 'Id' field needs adding too, depending on CopyFeatures behaviour
            # arcpy.CalculateField_management(outfc_path, "Id", row[1], "PYTHON_9.3") # Use if needed
            arcpy.CalculateField_management(outfc_path, "Source", row[2], "PYTHON_9.3")

    print("Finished splitting features.")

except ValueError as ve:
    print("Error: {}".format(ve))
    # Consider adding sys.exit() here if fields are missing
except arcpy.ExecuteError:
    print(arcpy.GetMessages(2))
except Exception as e:
    print("An unexpected error occurred during feature splitting: {}".format(e))


# ---------------------------------------------------------------------------
# Part 2: Prepare Environment & Global Rasters
# ---------------------------------------------------------------------------
print("Preparing environment and global rasters...")
try:
    # Use the ListFeatureClasses function to get the list of shapefiles just created
    # Ensure the workspace is set correctly before this
    fcList = arcpy.ListFeatureClasses("Id_*.shp") # More specific listing based on naming convention
    if not fcList:
        print("Warning: No split shapefiles found in workspace: " + env.workspace)
        # Consider exiting or handling this case depending on workflow

    # Set processing extent based on the DTM
    extentRaster = Raster(DTM)
    arcpy.env.extent = extentRaster.extent
    arcpy.env.snapRaster = DTM # Ensure alignment
    arcpy.env.cellSize = DTM # Ensure consistent cell size

    # Get cell size from DTM description
    description = arcpy.Describe(DTM)
    try:
      # Access meanCellHeight for raster layers
      cellSize = description.meanCellHeight # Use this if DTM is confirmed raster layer
      # Or if DTM might be path to raster dataset:
      # cellSize = description.children[0].meanCellHeight # More robust for datasets? Test needed.
      print("Processing cell size = " + str(cellSize))
    except (AttributeError, IndexError):
      print("Warning: Could not automatically determine cell size from DTM. Using environment setting.")
      cellSize = arcpy.env.cellSize # Fallback


    # Set local variables for Point to Raster Conversion
    valField = "Source" # Field containing the value to burn into the raster
    assignmentType = "MOST_FREQUENT" # How to handle multiple points in one cell
    priorityField = "" # Optional field to prioritize points

    # Optional: Create a single raster containing ALL source points
    # Useful for comparison or other models (e.g., TauDEM)
    raster_src_all_path = os.path.join(rasteralldir, "ras_src_all.tif") # Use .tif extension
    print("Creating combined source raster (optional): " + raster_src_all_path)
    arcpy.PointToRaster_conversion(shp, valField, raster_src_all_path, assignmentType, priorityField, cellSize)

    # Calculate Flow Direction (once for the whole area)
    print("Calculating Flow Direction...")
    # Define output paths for flow direction rasters
    fdir_path = os.path.join(msfdir, "fdir.tif") # Use .tif extension
    fdir_deg_path = os.path.join(msfdir, "fdir_deg.tif") # Use .tif extension
    Output_drop_raster = "" # Optional output drop raster

    # Process: Flow Direction (D8)
    arcpy.gp.FlowDirection_sa(DTM, fdir_path, "NORMAL", Output_drop_raster)

    # Process: Convert Flow Direction to degrees (0-360) for PathAllocation
    # Assuming standard ArcMap flow dir coding (1=E, 2=SE, 4=S, 8=SW, 16=W, 32=NW, 64=N, 128=NE)
    # Log2 converts these to 0-7, formula maps to degrees clockwise from East (?) - VERIFY THIS LOGIC
    # The formula seems non-standard. Typical conversion uses Con statements.
    # Example standard conversion (verify angles match PathAllocation needs):
    # out_fdir_deg = Con(fdir == 1, 0, Con(fdir == 2, 45, Con(fdir == 4, 90, ... ))) # Degrees CW from N?
    # USING ORIGINAL FORMULA BELOW - USER MUST CONFIRM IT WORKS AS INTENDED WITH PATHALLOCATION
    print("Calculating Flow Direction in degrees (using original formula)...")
    out_fdir_deg = Con(Log2(Raster(fdir_path)) < 6, (Log2(Raster(fdir_path)) + 2) * 45, (Log2(Raster(fdir_path)) - 6) * 45)
    out_fdir_deg.save(fdir_deg_path)

    print("Finished environment setup.")

except arcpy.ExecuteError:
    print(arcpy.GetMessages(2))
except Exception as e:
    print("An unexpected error occurred during environment setup: {}".format(e))
    # Consider sys.exit()


# ---------------------------------------------------------------------------
# Part 3: Process each source point feature individually
# ---------------------------------------------------------------------------
print("\nStarting processing for individual source points...")
pq_list = [] # List to store paths of individual pq_lim rasters

for fc in fcList:
    try:
        fc_path = os.path.join(env.workspace, fc) # Full path to the shapefile
        fc_basename = fc.replace(".shp", "") # Base name like "Id_123"
        print("\nProcessing source: " + fc_basename)

        # Convert individual point feature to raster
        outRaster_path = os.path.join(rasterdir, fc_basename + ".tif") # Explicitly add .tif
        print("  Converting point to raster: " + outRaster_path)
        arcpy.PointToRaster_conversion(fc_path, valField, outRaster_path,
                                       assignmentType, priorityField, cellSize)

        # Check if the raster was created and is valid
        if not arcpy.Exists(outRaster_path):
             print("  Warning: Raster conversion failed for " + fc_basename)
             continue # Skip to next feature

        # Ensure the created raster is treated as integer for PathAllocation if needed
        # Source_int_null_tif = Int(Raster(outRaster_path)) # Uncomment if needed, depends on 'Source' field type

        # Use SetNull to ensure only source cells have values (handle potential extent issues)
        Source_int_null_tif = SetNull(Raster(outRaster_path) <= 0, Raster(outRaster_path))


        # Define output paths for this specific feature's MSF results
        pq_lim = os.path.join(msfdir, "pq_lim_" + fc_basename + ".tif")
        PathAll_Sour1 = os.path.join(msfdir, "PathAll_Sour1_" + fc_basename + ".tif")
        start_z = os.path.join(msfdir, "start_z_" + fc_basename + ".tif")
        hi = os.path.join(msfdir, "hi_" + fc_basename + ".tif")
        li = os.path.join(msfdir, "li_" + fc_basename + ".tif")
        h_l = os.path.join(msfdir, "h_l_" + fc_basename + ".tif")
        h_l_lim = os.path.join(msfdir, "h_l_lim_" + fc_basename + ".tif")
        fri = os.path.join(msfdir, "fri_" + fc_basename + ".tif")
        pqi = os.path.join(msfdir, "pqi_" + fc_basename + ".tif")
        # Optional backlink rasters (usually not needed unless debugging paths)
        # Output_backlink_raster = os.path.join(msfdir, "backlink1_" + fc_basename + ".tif")
        # Output_backlink_raster__2_ = os.path.join(msfdir, "backlink2_" + fc_basename + ".tif")
        Output_backlink_raster = "" # Disable saving backlink
        Output_backlink_raster__2_ = "" # Disable saving backlink

        # --- MSF Core Calculations using Path Distance Allocation ---
        # These functions calculate cost surfaces based on travel formulas.
        # Refer to ArcGIS Path Distance help for details on parameters (Hf, Vf).
        # HfForward(1.0, 1.0): Simple forward horizontal factor (cost is 1 per unit distance)
        # HfLinear(0.5, 90, 0.011111): Linear horizontal factor based on angle deviation
        # VfBinary(1.0, -30, 30): Vertical factor - cost is 1 within slope range (-30 to 30 deg), infinite otherwise

        # Process: Path Distance Allocation (1) - Calculates 'li' (travel length?) and elevation at source 'start_z'
        print("  Running Path Allocation (1)...")
        # PathAllocation returns allocation raster, output cost raster, output backlink
        out_li_alloc, out_li_cost, _ = PathAllocation(Source_int_null_tif, "", "", fdir_deg_path, HfForward(1.0, 1.0), "", VfBinary(1.0, -30, 30), output_distance_raster=li, output_backlink_raster=Output_backlink_raster)
        # The cost raster from this run with VfBinary seems intended to capture source cell elevations? Verify this logic.
        out_li_cost.save(start_z)
        # The distance raster is saved as li

        # Process: Path Distance Allocation (2) - Calculates 'fri' (friction/cost?) and saves allocation 'PathAll_Sour1'
        print("  Running Path Allocation (2)...")
        out_fri_alloc, out_fri_cost, _ = PathAllocation(Source_int_null_tif, "", "", fdir_deg_path, HfLinear(0.5, 90, 0.011111), "", VfBinary(1.0, -30, 30), output_distance_raster=fri, output_backlink_raster=Output_backlink_raster__2_)
        out_fri_alloc.save(PathAll_Sour1) # Saves the allocation result
        # The distance raster is saved as fri

        # --- Raster Calculator Steps ---
        print("  Performing Raster Calculations...")
        # Process: Raster Calculator (3) - Calculate height difference 'hi'
        out_hi = Raster(start_z) - Raster(DTM)
        out_hi.save(hi)

        # Process: Raster Calculator (4) - Calculate H/L ratio 'h_l'
        # Add small epsilon to denominator to avoid divide-by-zero if li can be 0
        out_h_l = Raster(hi) / (Raster(li) + 1e-9)
        out_h_l.save(h_l)

        # Process: Raster Calculator (5) - Apply H/L threshold 'h_l_lim'
        out_h_l_lim = Con(Raster(h_l) >= float(H_L_threshold), Raster(h_l))
        out_h_l_lim.save(h_l_lim)

        # Process: Raster Calculator (2) - Calculate 'pqi' (momentum?)
        # Add small epsilon to denominator
        out_pqi = Raster(li) / (Raster(fri) + 1e-9)
        out_pqi.save(pqi)

        # Process: Raster Calculator (6) - Combine to get final potential impact 'pq_lim'
        # Formula seems unusual: h_l_lim + pqi - h_l_lim simplifies to just pqi?
        # Original: out_pq_lim = Raster(h_l_lim) + Raster(pqi) - Raster(h_l_lim)
        # This is equivalent to:
        # out_pq_lim = Con(IsNull(Raster(h_l_lim)), Raster(h_l_lim), Raster(pqi))
        # It means: where h_l_lim is valid (i.e., H/L threshold met), the value is pqi, otherwise NoData.
        # Using Con(IsNull(...)) is clearer:
        print("  Calculating final pq_lim...")
        out_pq_lim = Con(IsNull(Raster(h_l_lim)), Raster(h_l_lim), Raster(pqi)) # Equivalent, maybe clearer
        out_pq_lim.save(pq_lim)

        # Add the path of the successfully created pq_lim raster to the list
        pq_list.append(pq_lim)
        print("  Finished processing for " + fc_basename)

    except arcpy.ExecuteError:
        print("  ERROR processing {}: {}".format(fc_basename, arcpy.GetMessages(2)))
        # Continue to the next feature even if one fails
    except Exception as e:
        print("  UNEXPECTED ERROR processing {}: {}".format(fc_basename, e))
        # Continue to the next feature

# ---------------------------------------------------------------------------
# Part 4: Combine individual results using Cell Statistics
# ---------------------------------------------------------------------------
print("\nCombining individual pq_lim results...")
if pq_list: # Only proceed if at least one pq_lim raster was successfully created
    try:
        # Define final output path
        pq_lim_all_path = os.path.join(pqlimalldir, "pq_lim_combined_max.tif") # Descriptive name

        # Execute CellStatistics to find the maximum value across all individual pq_lim rasters
        # "MAXIMUM": Computes the maximum value for each cell.
        # "DATA": Ignores NoData values in the calculation. If all inputs are NoData for a cell, output is NoData.
        print("  Running Cell Statistics (MAXIMUM)...")
        outCellStatistics = CellStatistics(pq_list, "MAXIMUM", "DATA")

        # Save the final combined raster
        print("  Saving final combined raster: " + pq_lim_all_path)
        outCellStatistics.save(pq_lim_all_path)
        print("\nProcessing successfully completed!")
        print("Final combined output: " + pq_lim_all_path)

    except arcpy.ExecuteError:
        print("  ERROR during Cell Statistics: {}".format(arcpy.GetMessages(2)))
    except Exception as e:
        print("  UNEXPECTED ERROR during Cell Statistics: {}".format(e))
else:
    print("\nWarning: No individual pq_lim rasters were successfully generated. Cannot perform Cell Statistics.")

# ---------------------------------------------------------------------------
# Optional Cleanup - Uncomment if desired
# ---------------------------------------------------------------------------
# print("\nCleaning up intermediate files...")
# import shutil
# try:
#    if os.path.exists(env.workspace):
#        shutil.rmtree(env.workspace) # Removes main_folder and all its contents
#        print("Removed intermediate workspace: " + env.workspace)
#    if os.path.exists(msfdir):
#        # Be careful! This removes all individual results too. Only keep final combined?
#        # shutil.rmtree(msfdir)
#        # print("Removed MSF directory: " + msfdir)
#        pass # Keep individual results by default
#    if os.path.exists(rasterdir):
#         shutil.rmtree(rasterdir) # Removes split raster sources
#         print("Removed split raster source directory: " + rasterdir)
# except OSError as e:
#    print("Error during cleanup: {}".format(e))

print("\nScript finished.")
