import os
import argparse
import pathlib
import markdown

#TODO: add yaml to top stuff in markdown, https://stackoverflow.com/questions/44215896/markdown-metadata-format
#TODO: is this where the calls to get enumeratiosn woudl go?
#TODO: bit of a tidy up

def path_to_dict(path):
    """
    take a filepath and get contents and info into a dictionary structure
    :param path: path to read files from
    :returns: dictionary structure of folders and files
    """

    tree = {
        "name": path.stem,
        "path": path,
        "type":"folder",
        "description": f'# {path.stem} \n {path.joinpath("README.md").read_text()}',
        "children":[]
    }

    tree["children"].extend(
        [path_to_dict(x) for x in sorted(path.iterdir()) if x.is_dir()]
    )

    tree["children"].extend([
        {
        "name": f.stem,
        "path": f,
        "type": "file",
            "data_type": f.suffix[1:],
        "contents": f'## {f.stem}\n {f.read_text()}'
        }
        for f in sorted(path.iterdir()) if f.is_file() and f.suffix != '.md'
    ])

    return tree

def process(d):

    md = []

    md.append(d['description'])

    md.append([process(x) for x in d['children'] if x['type'] == 'folder'])

    md.append([x['contents'] for x in d['children'] if x['type'] == 'file'])

    return md

flat_list = list()
def flatten_list(list_of_lists):
    for item in list_of_lists:
        if type(item) == list:
            flatten_list(item)
        else:
            flat_list.append(item)
    
    return flat_list


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("input", help = "location of data files to be used")
    parser.add_argument("output", help = "location to output file to")
    args = parser.parse_args()
    outp = pathlib.Path(args.output)

    contents = path_to_dict(pathlib.Path(args.input))
    print(contents)
    out = ''.join(flatten_list(process(contents)))
    html = markdown.markdown(out, extensions = ['tables', 'fenced_code', 'toc'])

    outp.write_text(html)
