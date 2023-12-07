# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# -*- coding: utf-8 -*-
import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu
from dataiku import api_client

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
client=api_client()
users=client.list_projects()

def write_data(list_jsons, output_dataset):
    writer = output_dataset.get_writer()
    output_dataset.write_schema([{"name": "object","type": "string"}])
    for list_objects in list_jsons:
        writer.write_row_array([json.dumps(list_objects)])
    writer.close()
# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
write_data(users, dataiku.Dataset("project_info"))