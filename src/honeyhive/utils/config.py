
import os
import sys
from typing import Optional
import yaml
import fnmatch
from .dotdict import dotdict


CONFIG_PATTERN = ["**/honeyhive.yaml"]

def get_assumed_config_path() -> Optional[str]:
    try:
        # Get the directory containing the file being run
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle, use the sys._MEIPASS
            running_dir = sys._MEIPASS
        else:
            # If it's not bundled, use the directory containing the script
            running_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

        print(running_dir)

        return running_dir

        # Prepend the directory containing the running file to config.path
        config_path = os.path.join(running_dir, USER_CONFIG_PATH)
        if os.path.exists(config_path):
            return config_path
        

    except Exception as e:
        print(f'Error while loading config file: {e}')
        print('Continuing...')
        
    return None

def check_match(path_input, include_patterns, exclude_patterns):
    p = os.path.abspath(path_input)
    if include_patterns:
        include = False
        for pattern in include_patterns:
            if fnmatch.fnmatch(p, pattern):
                include = True
                break
        if not include:
            return False

    if exclude_patterns:
        exclude = False
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(p, pattern):
                exclude = True
                break
        return not exclude

    return True

def collect_files(input_path, include_patterns, exclude_patterns):
    if os.path.isdir(input_path):
        for root, dirs, files in os.walk(input_path):
            for file in files:
                fname = os.path.join(root, file)
                if check_match(fname, include_patterns, exclude_patterns):
                    yield (os.path.dirname(fname), fname)
    else:
        if not check_match(input_path, include_patterns, exclude_patterns):
            print(
                f"Reading {input_path} because it was specified directly. Rename it to *.eval.py "
                + "to include it automatically when you specify a directory."
            )
        yield (os.path.dirname(input_path), input_path)

# TODO: parse evaluators from yaml and add them to the evaluators registry

def load_yaml(_yaml) -> dict:
    if _yaml is None:
        return None
    
    content = None
    try:
        content = yaml.safe_load(_yaml)
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML: {str(e)}")
    except ValueError as e:
        raise ValueError(f"Validation error: {str(e)}")
        
    return content

def get_yaml_dotdict(path: str | None = None) -> dotdict:
    try:
        if path is None:
            _, path = next(collect_files(os.getcwd(), CONFIG_PATTERN, ["**/site-packages/**"]))
    except StopIteration:
        return dotdict()

    if not path:
        return dotdict()

    with open(path) as f:
        content = load_yaml(f)
    
    content = content or dict()
    
    return dotdict(content)

config = get_yaml_dotdict()
