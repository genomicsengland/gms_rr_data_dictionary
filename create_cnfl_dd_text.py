"""
script to process directory of YAML files and produce formatted text
python create_cnfl_dd_text.py <location of data files> <filepath to output to>
"""
import argparse
import os
import pathlib

import pandas
import psycopg2 as pg

# import markdown
import yaml
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
        'name': path.stem,
        'path': path,
        'type': 'folder',
        'contents': yaml.safe_load(path.joinpath('index.yaml').read_text()),
        'children': [],
    }

    tree['children'].extend(
        [path_to_dict(x) for x in sorted(path.iterdir()) if x.is_dir()]
    )

    # any other yaml files in the directory contain information on columns
    tree['children'].extend(
        [
            {
                'name': f.stem,
                'path': f,
                'type': 'file',
                'contents': yaml.safe_load(f.read_text()),
            }
            for f in sorted(path.iterdir())
            if f.is_file() and f.suffix == '.yaml' and f.name != 'index.yaml'
        ]
    )

    return tree


def process_column(d, header_level):
    """
    formats text for column files
    :param d: dictionary of column data
    :param header_level: header level to use in markdown
    :returns: string of markdown
    """

    out = [
        f"h{header_level}. {d['name']}",
        f"Data type: *{d['contents']['data_type']}*",
        f"{d['contents']['description']}",
    ]

    if 'codesystem' in d['contents'].keys():
        out.append(fetch_concepts(d['contents']['codesystem']))

    if 'fk' in d['contents'].keys():
        out.append(f"References +{d['contents']['fk']}+.")

    return '\n\n'.join(out)


def process_table(d, header_level):
    """
    formats text for a table file
    :param d: dictionary of table data
    :param header_level: header level to use in markdown
    :returns: string of markdown
    """

    out = [
        f"h{header_level}. {d['name']}",
        f"_{d['contents']['caption']}_",
        f"{d['contents']['description']}",
    ]

    return '\n\n'.join(out)


def process(d):
    """
    process a dictionary of table and column data
    :params d: input dictionary of table and column data
    :returns: list of markdown sections
    """

    md = []
    md.append(d['contents']['description'])

    starting_header_level = 2

    for x in d['children']:

        if x['type'] == 'folder':

            md.append(process_table(x, starting_header_level))

            for y in x['children']:

                md.append(process_column(y, starting_header_level + 1))

    return md


def fetch_concepts(codesystem):
    """
    fetches concept codes and descriptions from config database and outputs
    a table for inclusion
    :params codesystem: the concept codesystem of interest
    :returns: table of enumerations and descriptions as markdown string
    """

    sql = (
        f'select concept_code as enumeration, concept_display as description '
        f"from concept where codesystem_uri = '{codesystem}';"
    )
    con = pg.connect(
        f"host={os.getenv('GR_DB_HOST')} dbname={os.getenv('GR_DB_NAME')} "
        f"user={os.getenv('GR_DB_USER')} password={os.getenv('GR_DB_PWD')}"
    )
    df = pandas.read_sql(sql, con)

    return df.to_markdown(index=False, tablefmt='jira')


if __name__ == '__main__':

    # gather arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='location of data files to be used')
    parser.add_argument('output', help='location to output file to')
    args = parser.parse_args()
    outp = pathlib.Path(args.output)

    # extract information from input directory
    contents = path_to_dict(pathlib.Path(args.input))

    # process the dictionary and join the resulting list of strings
    out = '\n\n'.join(process(contents))

    # write out the markdown text to file
    outp.write_text(out)
