# -*- coding: utf-8 -*-
import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu
from dataiku import api_client
from pprint import pprint

client=api_client()
dss_connections = client.list_connections()

list_conns_filtered_df = pd.DataFrame.from_dict(dss_connections, orient='index', columns=['name', 'allowedGroups', 'usableBy']) 

# Write recipe outputs
list_conns_filtered = dataiku.Dataset("list_conn_filtered")
list_conns_filtered.write_with_schema(list_conns_filtered_df)

