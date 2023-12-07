# -*- coding: utf-8 -*-
import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu
import os, shutil
import datetime, time


dip_home = os.environ['DIP_HOME']
dss_folder = os.path.join(dip_home,'')
exports_folder = os.path.join(dip_home, 'exports')
        
timestr = time.strftime("%Y%m%d-%H%M%S")

maximum_age = int(self.config.get("age", 15))
maximum_timestamp = int(time.mktime((datetime.datetime.now() - datetime.timedelta(days=maximum_age)).timetuple()))
        
to_delete = []
        
    if self.config["folder"] == "dss_data":
        for dss_id in os.listdir(dss_folder):
            if os.stat(os.path.join(dss_folder, dss_id)).st_mtime < maximum_timestamp:
                to_delete.append(dss_id)

        def folder_size(folder):
            total_size = 0
              for dirpath, dirnames, filenames in os.walk(folder):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
            return total_size       

            

            for dss_id in to_delete:
                dssdata_folder = os.path.join(dss_folder, dss_id)
                size = folder_size(dssdata_folder)

                mtime = os.stat(dss_folder).st_mtime
                age = (time.mktime(datetime.datetime.now().timetuple()) - mtime)/86400

               
                rt.add_record([dss_id, int(age), size/1024])


# Write recipe outputs
AdminData = dataiku.Folder("6OMA98xF")
AdminData_info = AdminData.get_info()
