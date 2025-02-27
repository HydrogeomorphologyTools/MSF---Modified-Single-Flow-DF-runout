ArcGIS Toolbox implementing debris flow potential propagation from source points following the work by Huggel and colleagues reported within the following two main references:

Gruber, S., Huggel, C., Pike, R., 2009. Chapter 23 Modelling Mass Movements and Landslide Susceptibility, in: Hengl, T., Reuter, H.I. (Eds.), Developments in Soil Science, Geomorphometry. Elsevier, pp. 527–550. https://doi.org/10.1016/S0166-2481(08)00023-8

and

Huggel, C., Kääb, A., Haeberli, W., Krummenacher, B., 2003. Regional-scale GIS-models for assessment of hazards from glacier lake outbursts: evaluation and application in the Swiss Alps. Nat. Hazards Earth Syst. Sci. 3, 647–662. https://doi.org/10.5194/nhess-3-647-2003

In the first bibliographic reference GIS procedures/computation/tools are reported step by step.

The Python script is then provided with the following intent: converting multiple point features to an input raster dataset and subsequently running separately MSF retaining the max pqlim value in overlapping areas.
This is done to avoid  potential re-write of different values on pixels involved by multiple debris flow runouts.
Additional Python script is provided to clear folders and data in case of multiple runs and files overwrite.
