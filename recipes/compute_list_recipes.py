# -*- coding: utf-8 -*-
import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu



# Compute recipe outputs
# TODO: Write here your actual code that computes the outputs
# NB: DSS supports several kinds of APIs for reading and writing data. Please see doc.

list_recipes_df = ... # Compute a Pandas dataframe to write into list_recipes


# Write recipe outputs
list_recipes = dataiku.Dataset("list_recipes")
list_recipes.write_with_schema(list_recipes_df)
