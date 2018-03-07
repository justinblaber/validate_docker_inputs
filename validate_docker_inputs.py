#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" This will validate that the docker INPUTS directory is correct """

import os
import sys
from collections import OrderedDict

import yaml

# These are hard coded in each docker
INPUTS_PATH = os.path.join(os.sep, 'INPUTS')
INPUTS_YAML_PATH = os.path.join(os.sep, 'extra', 'inputs.yaml')

# Set delimiter to indicate comments in YAML file
COMMENT_DELIMITER = '//'

def ordered_load(stream, loader=yaml.Loader, object_pairs_hook=OrderedDict):
    """ this function will load a yaml file as an OrderedDict """
    class OrderedLoader(loader): #pylint: disable-msg=missing-docstring,too-many-ancestors
        pass
    def construct_mapping(loader, node): #pylint: disable-msg=missing-docstring
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)

def validate_inputs_dict(inputs_dict):
    """ validate inputs dict """
    for key in inputs_dict.keys():
        # Value is either empty or a list
        if not inputs_dict[key]:
            pass
        elif isinstance(inputs_dict[key], list):
            # List item can be another OrderedDict or string
            for item in inputs_dict[key]:
                if isinstance(item, OrderedDict):
                    # Another file structure; recurse
                    validate_inputs_dict(item)
                elif isinstance(item, str):
                    pass
                else:
                    RuntimeError('Unrecognized input: ' + str(item))
        else:
            raise RuntimeError('Unrecognized input: ' + str(inputs_dict[key]))

def parse_comments(string):
    """ returns [string, comment] """
    string_split = string.split(COMMENT_DELIMITER)
    if len(string_split) == 1:
        return [string, None]
    elif len(string_split) == 2:
        return [string_split[0].strip(), string_split[1].strip()]
    else:
        raise RuntimeError('Must have either no comment or a single comment: ' + string)

def handle_comment(string):
    """ returns 'string (optional comment)' """
    string_parsed = parse_comments(string)
    if string_parsed[1]:
        return string_parsed[0] + ' (' + string_parsed[1] + ')'
    else:
        return string_parsed[0]

def print_inputs_dict(inputs_dict, depth=0):
    """ prints inputs dict """
    for key in inputs_dict.keys():
        # Print directory - note that root is skipped
        directory = handle_comment(key)
        if depth >= 1:
            print('  '*(depth-1) + '\\' + directory)

        # Value is either empty or a list
        if not inputs_dict[key]:
            # Empty directory
            pass
        else:
            # List item can be another OrderedDict or string
            for item in inputs_dict[key]:
                if isinstance(item, OrderedDict):
                    # Another file structure; recurse
                    print_inputs_dict(item, depth+1)
                else:
                    # This is a file
                    print('  '*depth + '-' + handle_comment(item))

def validate_inputs_dir(inputs_dict, parent_path=os.sep):
    """ validates inputs dir based on inputs_dict """
    for key in inputs_dict.keys():
        # Get directory path
        directory = parse_comments(key)[0]
        if directory == 'root':
            directory = os.sep
        directory_path = os.path.join(parent_path, directory)

        # Validate directory path
        if not os.path.isdir(directory_path):
            raise RuntimeError('Directory does not exist: ' + directory_path)

        # Value is either empty or a list
        if not inputs_dict[key]:
            # Empty directory
            pass
        else:
            # List item can be another OrderedDict or string
            for item in inputs_dict[key]:
                if isinstance(item, OrderedDict):
                    # Another file structure; recurse
                    validate_inputs_dir(item, directory_path)
                else:
                    # This is a file
                    file_path = os.path.join(directory_path, parse_comments(item)[0])
                    if not os.path.isfile(file_path):
                        raise RuntimeError('File does not exist: ' + file_path)

def main():
    """ Main program """
    # Make sure INPUTS directory exists
    if not os.path.isdir(INPUTS_PATH):
        raise RuntimeError('Could not find: ' + INPUTS_PATH)

    # Make sure inputs.yaml file exists
    if not os.path.isfile(INPUTS_YAML_PATH):
        raise RuntimeError('Could not find: ' + INPUTS_YAML_PATH)

    # Read inputs yaml as dictionary
    with open(INPUTS_YAML_PATH, 'rt') as file:
        inputs_dict = ordered_load(file.read(), yaml.SafeLoader)

    # validate_inputs_dict will throw an exception is inputs yaml file is not structured properly
    validate_inputs_dict(inputs_dict)

    # If inputs directory is empty, just print what the inputs are
    if not os.listdir(INPUTS_PATH):
        print('This docker has the following INPUTS directory structure: ')
        print_inputs_dict(inputs_dict)

        # Return a non-zero exit code
        return -1
    else:
        # Try to validate inputs dir
        # validate_inputs_dir will throw an exception if an input is missing in the inputs directory
        try:
            validate_inputs_dir(inputs_dict)
        except Exception as exception: #pylint: disable-msg=unused-variable,broad-except
            # Print inputs
            print('Incorrect inputs; reason: ' + str(exception) + '\n')
            print('This docker has the following INPUTS directory structure: ')
            print_inputs_dict(inputs_dict)

            # Return a non-zero exit code
            return -1

    # Return zero exit code
    print('INPUTS directory is correct!')
    return 0

if __name__ == "__main__":
    sys.exit(main())
