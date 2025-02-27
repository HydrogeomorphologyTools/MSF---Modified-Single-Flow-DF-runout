ArcGIS Toolbox implementing debris flow potential propagation from source points following the work by Huggel and colleagues:

Regional-scale GIS-models for assessment of hazards from glacier lake outbursts: evaluation and application in the Swiss Alps
C. Huggel, A. Kääb, W. Haeberli, and B. Krummenacher
Natural Hazards and Earth System Sciences (2003)

https://doi.org/10.5194/nhess-3-647-2003



The Python script is then provided with the following intent: converting multiple point features to an input raster dataset and subsequently running separately MSF retaining the max pqlim value in overlapping areas.
This is done to avoid  potential re-write of different values on pixels involved by multiple debris flow runouts.
Additional Python script is provided to clear folders and data in case of multiple runs and files overwrite.
