# README

The code here generates a summary of the structure of clinical data in the GMS Research Release - the data dictionary.

The relevant information is stored in a hierarchy of yaml files:

```
data_files/
 |- index.yaml <summary of the dataset as a whole>
 |- <table>/ <each folder represents a table>
 |  |- index.yaml <summary of the table>
 |  |- <column>.yaml <every other yaml file in the directory refers to a field in the table>
 '  '
```

The hierarchy of files is processed by `create_cnfl_dd_text.py` into a markdown file that can be copy and pasted into a Confluence page (whilst editing a page, go to Insert More Content > Markup).
As part of the process relevant enumerations are fetched from the GMS `genomic_record` database.

`create_data_file_structure.sh` runs queries against the intermediate database and generates a fresh hierarchy of files. To check for differences between the database and `data_files` do:

```sh
bash create_data_file_structure.sh ~/scr/dd
vim -d <(tree data_files) <(tree ~/scr/dd)
```

`er_diag.plantuml` is an ER diagram for the dataset using PlantUML syntax. The diagram can be generated using [their online server](https://www.plantuml.com/plantuml/uml).

A `.env` file is required with the following variables:

```sh
GR_DB_HOST=<GMS genomic_record DB host>
GR_DB_PORT=<GMS genomic_record DB port>
GR_DB_USER=<GMS genomic_record DB user>
GR_DB_PWD=<GMS genomic_record DB password>
GR_DB_NAME=<GMS genomic_record DB name>
```
