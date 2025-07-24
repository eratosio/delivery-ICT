# delivery-ICT
This is a code repository for new ICT orders.

## Set Up
install requirement via [hatch](https://hatch.pypa.io/1.9/install/)
```commandline
pip install hatch
```
or
```commandline
pipx install hatch
```

Create a hatch environment using
```commandline
hatch env create default
```
This creates a virtual environment in .venv/default and installs the project in editable mode. 
Activate using source 
```
.venv/default/bin/activate
```


## Functionalities
Follow the steps below to configure datastreams, populate them using a workflow, and automate the creation of a Grafana dashboard.

1. `fetch_platform_from_excel/`
   - Place the Excel file and ict_senaps_key inside this directory.
   - Run fetch_data_from_excel.py to extract and prepare datastreams.

   
3. `create_workflow/`
   - Edit constant.py to include new organization’s name and ID.
   - Run make.py to generate the workflow zip file.
   - Upload the generated zip to Senaps, configure the port setting.


3. `create_dashboard/` 
   - Retrieve the service account key and UID from your Grafana organization.
   - Save them as separate `.json` files and place them in this directory.
   - Run sapflow_automation.py to push the dashboard.


