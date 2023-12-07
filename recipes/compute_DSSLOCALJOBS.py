# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# -*- coding: utf-8 -*-
import dataiku, dataikuapi
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu
from time import process_time

import json
from datetime import datetime as dt, timedelta

from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
disable_warnings(InsecureRequestWarning)

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
dataiku.clear_remote_dss()
client = dataiku.api_client()
custom_vars = dataiku.get_custom_variables()

## Define range of days to pickup only projects who's jobs ran in this range
RANGE_DAYS=int(custom_vars["daysRange"])
delta=dt.today()-timedelta(days=RANGE_DAYS)
print("Days range used to scan projects:",RANGE_DAYS,"with date:", delta)

if custom_vars["isRemote"] == 'true':
    print ("Using remote DSS ",custom_vars["remoteURL"])
    client=dataikuapi.DSSClient(custom_vars["remoteURL"],custom_vars["remoteAPIKey"])
    client._session.verify=False
else:
    print ("Using local DSS")

keys=client.list_project_keys()
print("Number of projects to process:",len(keys))

recipe_details = []

IS_DEV=False
keys=client.list_project_keys()

if custom_vars["isDev"] == 'true':
    IS_DEV=True
    
    testKey=custom_vars["testKey"]
    if testKey in keys:
        keys = [testKey]
        print("Running in DEV mode using project", keys)
    else:
        raise Exception("Test PROJECTKEY: "+testKey+" was not found in a list of availables PROJECTKEYS")
        
else:
    print("Number of projects to process:",len(keys))

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
def get_project_permissions(key):
    p = client.get_project(key)
    pp = p.get_permissions()
    result={}
    result['Owner']=pp['owner']

    gg=[]
    for permission in pp['permissions']:
        try:
            gg.append(permission['group'])
        except KeyError:
            gg.append("{}")

    result["Groups"]=gg

    return result;

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
def is_project_in_range(key):
    p = client.get_project(key)
    jt=[]

    jobs = p.list_jobs()
    if len(jobs) == 0:
        print("Project", key, "has no jobs, will process.")
        return True

    for job in p.list_jobs():
        jt.append(int(job['startTime'] ))

    jt.sort(reverse=True)
    last_run=jt[0]
    in_range=(dt.fromtimestamp(last_run/1000)>=delta)

    print("Most recent run:", dt.fromtimestamp(last_run/1000))
    print("Poject last run in range?",in_range)

    return in_range

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
### Gets recipe dataset types
def get_recipe_ds_types(p,recipe_ds,recipe_name):
   # get references

    if ( recipe_ds == {}):
        #print("No datasets detected for ", recipe_name)
        return []

    try:
        types_list=[]
        ds_type="other"
        key=list(recipe_ds.keys())[0]
        #print("Recipe dataset ref key",key,"for",recipe_ds)

        if type(recipe_ds[key]['items'])==list:
            for ref in recipe_ds[key]['items']:
                try:
                    if 'folder' in key:
                        ds_type="managed_folder"
                    else:

                        try:
                            p.get_dataset(ref.get('ref'))
                            ds_type=p.get_dataset(ref.get('ref')).get_settings().type
                        except:
                            ds_type="other"

                except Exception as ex:
                    print("Issue with ref", ref)
                    print( str(ex))
                finally:
                    # print ("DSTYPE",ds_type)
                    if ds_type not in types_list: types_list.append(ds_type)
        else:
            print("Unable to find ref items for", recipe_ds )

    except Exception as e:
        print("Exception when looking for ref", recipe_ds )
        print( str(e))

    finally:
        return types_list

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
def get_settings(keys):
    details = []

    for key in keys:

        print("-----------------------------------------\n", key)
        p = client.get_project(key)

        if len(p.list_recipes())==0:
            print("Project {} has no recipes, skipping.".format(key))
            continue
        elif not is_project_in_range(key):
            print("Skipping project",key,"not in range!")
            continue
        else:
            print("Processing project", key,"with",len(p.list_recipes()),"recipes")


        ps = p.get_settings().get_raw()
        permissions = get_project_permissions(key)

        t1 = process_time()

        for recipe in p.list_recipes():
            #if IS_DEV:
            #    print("Recipe",recipe['name'])

                #print(json.dumps(recipe,indent=2))


            inputs=get_recipe_ds_types(p,recipe['inputs'],recipe['name'])
            outputs=get_recipe_ds_types(p,recipe['outputs'],recipe['name'])
            recipe_recommended_engine_type=''
            recipe_container_conf=''
            recipe_sel_engine_type=''
            is_sel_eng_recommended=False

            recipeObj = p.get_recipe(recipe['name'])
            rs = recipeObj.get_status()
            # Obtain Selected Recipe Engine Details
            try:
                r_sel_det=rs.get_selected_engine_details()
                recipe_sel_engine_type = r_sel_det['type']
                is_sel_eng_recommended = r_sel_det['recommended']
            except Exception as ex:
                print("No engine selection found for ", recipe['name'])


            #Obtain Recommended Recipe Engine Details
            try:
                for ed in rs.get_engines_details():
                    if ed['recommended']==True:
                        recipe_recommended_engine_type=ed['type']
                        break;
                    else:
                        recipe_recommended_engine_type=''
            except Exception as ex:
                print("No engine details for ", recipe['name'])


            # Obtain recipe container information
            try:
                    recipe_container_type = recipe['params']['containerSelection']['containerMode']
                    if recipe_container_type != 'INHERIT':
                        recipe_container_conf = recipe['params']['containerSelection']['containerConf']
            except KeyError:
                    if  recipe['type'] in ['spark_sql_query', 'pyspark']:
                            recipe_container_type = 'SPARK'
                    elif 'params' in recipe and 'engineType' in recipe['params']:
                            recipe_container_type = recipe['params']['engineType']
                    else:
                            try:
                                    recipe_container_type = p.get_recipe(recipe['name']).get_status().get_selected_engine_details()['type']
                            except:
                                    recipe_container_type = 'LOCAL'


            try:
                    modification_info = recipe["creationTag"]
            except KeyError:
                    modification_info = 'undefined'

            detail = {
                       "project_name"           : recipe["projectKey"],
                       "recipe_name"            : recipe["name"],
                       "recipe_type"            : recipe["type"],
                       "recipe_input_types"     : ','.join(inputs),
                       "recipe_output_types"    : ','.join(outputs),
                       "project_container_type" : ps['settings']['container']['containerMode'],
                       "recipe_container_type"  : recipe_container_type,
                       "recipe_container_conf"  : recipe_container_conf,
                       "recipe_selected_engine" : recipe_sel_engine_type,
                       "is_sel_eng_recommended" : is_sel_eng_recommended,
                       "recipe_recommended_engine_type" : recipe_recommended_engine_type,
                       "project_permissions"    : str(permissions),
                       "modification_info"      : modification_info}
            details.append(detail)

        t2 = process_time()
        print("Project processing finished with elapsed time", t2-t1)

    return details;

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
#TEST_KEY= 'BM33UKICS' #'ADAMTESTING'  #'ABROCITINIBPOSTLAUNCHDASHBOARD'

### Main method that goes scans each project key in the list
recipe_details = get_settings(keys)

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
recipe_info = pd.DataFrame(recipe_details)
dsslocaljobs_df = recipe_info # Compute a Pandas dataframe to write into DSSLOCALJOBS

#print ("DF Size:",dsslocaljobs_df.shape[0])

# Write recipe outputs
if IS_DEV:
    dsslocaljobs = dataiku.Dataset("DSSLOCALJOBS_DEV")
else:
    dsslocaljobs = dataiku.Dataset("DSSLOCALJOBS")

dsslocaljobs.write_with_schema(dsslocaljobs_df)