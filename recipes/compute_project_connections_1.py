# -*- coding: utf-8 -*-
import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu



client = dataiku.api_client()

copy_projectkey= dataiku.get_custom_variables()["project_key"]

#project = client.get_project("ADHOC_AVT")

project = client.get_project(copy_projectkey)

all_datasets = project.list_datasets()

  
project_connections_lst = []

for dataset in all_datasets:
    try:
       # print('Dataset', dataset["name"], 'is using', dataset["params"]["connection"], "connection")
       # print( dataset["params"]["connection"])
        project_connections_lst.append(
            {
                'Connection': dataset["params"]["connection"]
            }
        )
    except KeyError:
        print('Dataset', dataset["name"], 'is using possibly upload dataset')
        
         
project_connections_df = pd.DataFrame(project_connections_lst)
            
# Compute recipe outputs
# TODO: Write here your actual code that computes the outputs
# NB: DSS supports several kinds of APIs for reading and writing data. Please see doc.

#project_connections_df = ... # Compute a Pandas dataframe to write into project_connections


# Write recipe outputs
project_connections = dataiku.Dataset("project_connections")
project_connections.write_with_schema(project_connections_df)
