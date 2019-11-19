from argparse import ArgumentParser
from typing import List, Union
import os
import subprocess

"""
This could be cleaned up by separating the utility functions from the main
script functionality, but I wanted to keep everything in one place since it's for
my own convenience. Feel free to change that if you would like to repurpose the code.
"""

str_or_path = Union[str, os.PathLike]


def build_file_list(root_dir: str_or_path) -> List:

    """
    Builds the list of files to search by recursively searching directories 
    within the root directory, using os.walk. Excludes any directories specified
    by name in `do_not_search.txt`. `do_not_search.txt` should be formatted 
    using full or partial directory names, each separated by a newline.
    """

    files = []

    # Use a file (by default named 'do_not_search.txt') to specify no-search dirs
    # This allows you to keep your no-search dirs separate from the code
    no_search_path = os.path.join(root_dir, "do_not_search.txt")
    if os.path.exists(no_search_path):
        with open(no_search_path) as f:
            no_search_dirs = [line.strip() for line in f.readlines()]
    else: 
        no_search_dirs = []

    for dir_name, subdir_list, file_list in os.walk(root_dir):

        # If dir is in no_search_dirs, skip it
        if any([ns_dir in dir_name for ns_dir in no_search_dirs]):
            continue

        # Keep the full path as second item in tuple, for opening later
        files.extend([(fname, os.path.join(dir_name, fname)) for fname in file_list])

    return files


def search_file_list(query: str, file_list: List) -> List:

    """Searches the built-up file list for user's query; exits if nothing found."""

    # Searches only the filename (tup[0]) for the user's query
    search_result_list = [tup for tup in file_list if query.lower() in tup[0].lower()]
    if not search_result_list:
        print("No exact-match results. Try something else.")
        raise SystemExit()

    return search_result_list


def ask_user_which_file(search_result_list: List) -> os.PathLike:

    """
    Present user with indexed list of files they can choose from;
    use input to select a file and return the path.
    """

    # Index each file so user can select an option quickly
    file_dict = {i: tup for i, tup in enumerate(search_result_list)}

    print("Found these:\n")
    for i, tup in file_dict.items():
        print(f"[{i}]", ":", tup[0], end="\n\n")

    file_id = input("\nWhich file were you looking for? ")
    full_file_path = file_dict[int(file_id)][1]

    return full_file_path


def open_file(root_dir: str_or_path, file: str_or_path, app: str):

    """Opens the user-selected file in either Preview or Adobe Acrobat Reader."""
    
    subprocess.run(["open", "-a", app, file], cwd=root_dir, check=True)


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("-a", dest="acro", action="store_true")  # default: stores False
    args = parser.parse_args()

    root_dir = "."
    app = "Adobe Acrobat Reader DC" if args.acro else "Preview"

    files = build_file_list(root_dir)
    search_results = search_file_list(args.query, files)
    selected_file = ask_user_which_file(search_results)
    open_file(root_dir, selected_file, app)
