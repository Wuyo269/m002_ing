# W005_ING

## Description
Portfolio project

Application categorises banking transactions based on provided mapping.


### Installation
1. Install Python 3.14+
2. Create virtual environment -> `python venv venv`
3. Install dependencies -> `python -m pip install requirements.txt `


## Usage
1. Put banking transaction csv file in `files/input` folder 
2. Adjust CSV field mapping located in `files/mapping/field_mapping.json`
3. Adjust category mapping located in `files/mapping/category_mapping.json`
4. Run -> `python main.py`


Categorised file will be saved in `files/output` folder
Uncategorised title and contractor fields will be saved in `files/uncategorised` folder


## Supported banks
Currently supports CSV exports from ING bank.


## Configuration
- `files/mapping/field_mapping.json`: Maps CSV column names from ING export to internal field names.
- `files/mapping/category_mapping.json`: Maps contractor and title values to category labels.