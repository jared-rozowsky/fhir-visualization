# fhir-visualization
Extract data from fhir-document-reference and create visualizations

The purpose of this repo is to extract metadata (gender, race, ethnicity, etc.) from the fhir-document-reference that is attached to each file in a [CAVATICA](https://www.cavatica.org/) project.


### Quick guide
1 - use [Implement.ipynb](https://github.com/jared-rozowsky/fhir-visualization/blob/main/Implement.ipynb) to extract data using Extract_Visualize_Data.py  
2 - use [Visualize.ipynb](https://github.com/jared-rozowsky/fhir-visualization/blob/main/Visualization.ipynb) to visualize the data using Panels

### Full guide

These scripts were tested on a project that imported the HTP study from the [INCLUDE portal](https://portal.include.com/) into a project, but could be generalized to any project where each file has a fhir-document-reference. 

The .py script to extract data using the FHIR api is Extract_Visualize_Data.py  
Quick help:
```
usage: Extract_Visualize_Data.py [-h] --cavatica_token CAVATICA_TOKEN
                                 --cavatica_project CAVATICA_PROJECT
                                 --include_fhir_authentication_cookie
                                 INCLUDE_FHIR_AUTHENTICATION_COOKIE

Retrieve metadata from the INCLUDE Server and updates the metadata on the
Cavatica Project

optional arguments:
  -h, --help            show this help message and exit
  --cavatica_token CAVATICA_TOKEN
                        You can find your developer token at
                        https://cavatica.sbgenomics.com/developer/token
  --cavatica_project CAVATICA_PROJECT
                        The Cavatica project where the files are already
                        imported from the INCLUDE Portal
  --include_fhir_authentication_cookie INCLUDE_FHIR_AUTHENTICATION_COOKIE
                        The Authorization cookie from the INCLUDE FHIR Server
                        (https://include-api-fhir-service.includedcc.org/) To
                        obtain the cookie, open the Chorme or Firefox console,
                        go to the Application tab and copy the value contained
                        in `AWSELBAuthSessionCookie-0`.
```

The data extracted from the fhir-document-reference is saved as a dataframe. See [Implement.ipynb](https://github.com/jared-rozowsky/fhir-visualization/blob/main/Implement.ipynb) for how to do this. 

Once the data is saved as a dataframe, the visualization is created using Panels - see [Visualize.ipynb](https://github.com/jared-rozowsky/fhir-visualization/blob/main/Visualization.ipynb) for how this is done. 

*To save time, the dataframe is saved as a .csv file, so the Visualization.ipynb can be run without re-running the Implement.ipynb.
