import importlib
import os

from typing import List
from dataclasses import dataclass
from threading import Lock
from contextlib import contextmanager
import traceback

from honeyhive.utils.config import collect_files


_lazy_load = False

@contextmanager
def _set_lazy_load(lazy_load: bool):
    global _lazy_load
    current = _lazy_load
    try:
        _lazy_load = lazy_load
        yield
    finally:
        _lazy_load = current

INCLUDE = [
    "**/*.eval.py",
]
EXCLUDE = ["**/site-packages/**"]


_import_lock = Lock()

@dataclass
class FileHandle:
    in_file: str
    dir: str
    
    def rebuild(self):
        in_file = os.path.abspath(self.in_file)

        with _import_lock:
            with _set_lazy_load(True):

                try:
                    # https://stackoverflow.com/questions/67631/how-can-i-import-a-module-dynamically-given-the-full-path
                    spec = importlib.util.spec_from_file_location("eval", in_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                except Exception as e:
                    print(f"Error importing {in_file}: {e}")
                    traceback.print_exc()


def initialize_handles(files):
    input_paths = files if len(files) > 0 else ["."]

    fnames = set()
    for path in input_paths:
        for dir, fname in collect_files(path, INCLUDE, EXCLUDE):
            print(dir, fname)
            fnames.add(os.path.abspath(fname))

    return [FileHandle(in_file=fname, dir=dir) for fname in fnames]

def run_once(handles: List[FileHandle]):
    terminate_on_failure = True
    for handle in handles:
        try:
            handle.rebuild()
        except Exception as e:
            if terminate_on_failure:
                raise
            else:
                print(f"Failed to import {handle.in_file}: {e}")
                continue

def run(args):
    handles = initialize_handles(args.files)
    run_once(handles)

def build_parser(subparsers, parent_parser):
    
    parser = subparsers.add_parser(
        "eval",
        help="Run evals locally.",
        parents=[parent_parser],
    )

    parser.add_argument(
        "files",
        nargs="*",
        help="A list of files or directories to run. If no files are specified, the current directory is used.",
    )
    
    parser.set_defaults(func=run)
    