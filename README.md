# MSF - Modified Single Flow DF Runout Model (ArcGIS Toolbox & python script)

## Description

This repository provides an **ArcGIS Toolbox and a Python script** implementing a debris flow potential propagation model from source points, following the Modified Single Flow Direction (MSF) approach based on the work by Huggel and colleagues. The methodology draws primarily from the following key references:

* Gruber & Huggel (2009) in *Geomorphometry* (Chapter 23)
* Huggel et al. (2003) in *Natural Hazards and Earth System Sciences*

(See the full **References** section below for details and DOIs).

The core tool implements the GIS procedures detailed in these references, designed for execution within the **Esri ArcGIS environment**.

### Additional Functionality

Beyond the core MSF implementation, supplementary Python scripts are included to enhance usability, mainly when dealing with multiple initiation points and potentially overlapping flooded/modelled areas:

1.  **Multiple Point Handling:** A script converts multiple input point features into the necessary raster format for the model.
2.  **Overlap Management:** It runs the MSF model based on inputs derived from these multiple points and ensures that the maximum potential impact value (`pqlim`) is retained in pixels potentially affected by overlapping runouts. This avoids lower values overwriting higher potential impact values from different sources.
3.  **Data Cleanup:** An additional utility script helps clear intermediate folders and data generated during runs, which is useful for managing outputs when performing multiple simulations or reruns.

## Requirements

* **Mandatory Esri Software:** A licensed installation of **Esri ArcGIS Desktop (ArcMap 10.x recommended) or ArcGIS Pro (2.x or later)** is required to run this toolbox and its associated scripts. The functionality relies heavily on the `ArcPy` site-package and native ArcGIS geoprocessing tools. **You must possess a valid ArcGIS license.**
* **Required ArcGIS Extensions:** The **Spatial Analyst Extension** for ArcGIS must be installed, licensed, and enabled in your ArcGIS session. The model utilizes essential raster processing functions (like flow direction, accumulation, etc.) from this extension.
* **Operating System:** Primarily designed for Windows, aligning with the requirements of ArcGIS Desktop/Pro.

## Installation / Setup

1.  Download or clone this repository to your local machine.
2.  Ensure your ArcGIS environment (ArcMap or Pro) is running and that the **Spatial Analyst extension** is licensed and enabled.
3.  In ArcMap (using the Catalog window) or ArcGIS Pro (using the Catalog pane), navigate to the directory where you saved the repository files.
4.  Add the `MSF_DF_Runout.tbx` (or the similarly named `.tbx` file present in the repository) as a Toolbox to your project.
    * In ArcMap: Right-click ArcToolbox -> Add Toolbox...
    * In ArcGIS Pro: Right-click Toolboxes in the Catalog Pane -> Add Toolbox...

## Usage

1.  Once the toolbox is added, expand it within the ArcToolbox window (ArcMap) or Catalog Pane (Pro) to see the tools.
2.  Open the main "MSF DF Runout Model" tool (note: the exact name might vary slightly, check inside the toolbox).
3.  Provide the required input parameters in the tool's dialog window. These will typically include:
    * Input Digital Elevation Model (DEM) raster
    * Input Source Points feature class (or a raster appropriately crafted with elevation int values at release points and nodata elsewhere)
    * Parameters
    * Specify the path and name for the output runout simulation raster.
4.  Run the tool. Monitor progress and check messages in the ArcGIS geoprocessing window/pane.
5.  Utilize the supplementary Python scripts (potentially run from the command line using ArcGIS's Python, or integrated as separate script tools if configured) for pre-processing multiple source points, running the MSF model, and optionally cleaning up output directories as needed.

## References

* Gruber, S., Huggel, C., Pike, R., 2009. Chapter 23 Modelling Mass Movements and Landslide Susceptibility, in: Hengl, T., Reuter, H.I. (Eds.), Developments in Soil Science, Geomorphometry. Elsevier, pp. 527–550. [https://doi.org/10.1016/S0166-2481(08)00023-8](https://doi.org/10.1016/S0166-2481(08)00023-8)
* Huggel, C., Kääb, A., Haeberli, W., Krummenacher, B., 2003. Regional-scale GIS-models for assessment of hazards from glacier lake outbursts: evaluation and application in the Swiss Alps. Nat. Hazards Earth Syst. Sci. 3, 647–662. [https://doi.org/10.5194/nhess-3-647-2003](https://doi.org/10.5194/nhess-3-647-2003)

## License - GNU GPLv2

The software in this repository (specifically, the Python scripts `.py` and ArcGIS toolbox structure `.tbx`) is free software: you can redistribute it and/or modify it under the terms of the **GNU General Public License as published by the Free Software Foundation, specifically version 2 of the License (GPLv2)**.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License v2 for more details.

**You should have received a copy of the GNU General Public License v2 along with this program.** Please check for a file named `LICENSE` in the root of this repository. If you did not receive a copy, you can view it online here: <https://www.gnu.org/licenses/old-licenses/gpl-2.0.html>

**Important Clarification on Dependencies:**
Please be aware that while the code *within this repository* is licensed under the open-source GPLv2, its actual execution **is fundamentally dependent on proprietary software: Esri ArcGIS Desktop/Pro and its Spatial Analyst extension**. The GPLv2 license governing this project **does not** grant you any rights whatsoever to use Esri's software; you must independently obtain a valid ArcGIS license from Esri according to their specific licensing terms and conditions. The GPLv2 license applies *only* to the specific code files provided here by the repository maintainers.
