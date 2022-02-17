import os
import argparse
import pathlib
import markdown
import yaml
import pandas
import psycopg2 as pg
from dotenv import load_dotenv

load_dotenv()

def path_to_dict(path):
    """
    take a filepath and get contents and info into a dictionary structure
    :param path: path to read files from
    :returns: dictionary structure of folders and files
    """

    # the description of the folder is pulled from an index.yaml file in there
    tree = {
        "name": path.stem,
        "path": path,
        "type":"folder",
        "contents": yaml.safe_load(path.joinpath("index.yaml").read_text()),
        "children":[]
    }

    tree["children"].extend(
        [path_to_dict(x) for x in sorted(path.iterdir()) if x.is_dir()]
    )

    # any other yaml files in the directory contain information on columns
    tree["children"].extend([
        {
        "name": f.stem,
        "path": f,
        "type": "file",
        "contents": yaml.safe_load(f.read_text())
        }
        for f in sorted(path.iterdir()) if f.is_file() and
        f.suffix == '.yaml' and f.name != 'index.yaml'
    ])

    return tree

def process_column(d, header_level):
    """
    formats text for column files
    """

    out = [
        f"{'#'*header_level} {d['name']}",
        f"Data type: **{d['contents']['data_type']}**",
        f"{d['contents']['description']}",
    ]

    if 'codesystem' in d['contents'].keys():
        out.append(fetch_concepts(d['contents']['codesystem']))

    if 'fk' in d['contents'].keys():
        out.append(f"References {d['contents']['fk']}.")

    return "\n\n".join(out)

def process_table(d, header_level):
    """
    formats text for a table file
    """

    out = [
        f"{'#'*header_level} {d['name']}",
        f"__{d['contents']['caption']}__",
        f"{d['contents']['description']}"
    ]

    return "\n\n".join(out)

def process(d):

    md = []

    md.append(d['contents']['description'])

    for x in d['children']:

        if x['type'] == 'folder':

            md.append(process_table(x, 1))

            for y in x['children']:

                md.append(process_column(y, 2))

    return md

    return flat_list

def fetch_concepts(codesystem):
    """
    fetches concept codes and descriptions from config database and outputs
    a table for inclusion
    """

    sql = f"select concept_code as enumeration, concept_display as description from concept where codesystem_uri = '{codesystem}';"
    con = pg.connect(f"host={os.getenv('GR_DB_HOST')} dbname={os.getenv('GR_DB_NAME')} user={os.getenv('GR_DB_USER')} password={os.getenv('GR_DB_PWD')}")
    df = pandas.read_sql(sql, con)

    return df.to_markdown(index=False)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("input", help = "location of data files to be used")
    parser.add_argument("output", help = "location to output file to")
    args = parser.parse_args()
    outp = pathlib.Path(args.output)

    contents = path_to_dict(pathlib.Path(args.input))
    out = '\n\n'.join(process(contents))
    html = markdown.markdown(out, extensions = ['tables', 'fenced_code', 'toc'])

    outp.write_text(html)
