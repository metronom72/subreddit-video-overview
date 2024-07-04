import os

import toml

from src.cli.inputs import get_version, get_tts_library


def read_config(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Configuration file '{file_path}' not found.")

    with open(file_path, 'r') as file:
        config = toml.load(file)

    return config


def query_input(block, config_folder_path):
    if block.get('enabled', False):
        for key, value in block.items():
            if value == "" or value is None:
                new_value = input(f"Please enter a value for '{key}': ")
                block[key] = new_value

        if 'version' in block and block['version'] == "":
            block['version'] = get_version(config_folder_path)

        if 'tts_library' in block and block['tts_library'] == "":
            block['tts_library'] = get_tts_library()

    return block


def get_configuration(config_file_path):
    config_folder_path = os.path.dirname(config_file_path)
    try:
        config = read_config(config_file_path)
        print("Initial configuration:")
        print(config)

        # Iterate through the configuration sections and update as needed
        for section, block in config.items():
            print(f"\nProcessing section: {section}")
            if block.get('enabled', False):
                if 'version' in block and block['version'] == "":
                    block['version'] = get_version(os.path.join(config_folder_path, 'src/html/templates'))
                if 'tts_library' in block and block['tts_library'] == "":
                    block['tts_library'] = get_tts_library()
                updated_block = query_input(block, config_folder_path)
                config[section] = updated_block

        print("\nUpdated configuration:")
        print(config)

        return config

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    root_folder = os.path.join(os.path.dirname(__file__), './../../')
    config_file_path = os.path.join(root_folder, 'config.toml')
    get_configuration(config_file_path)
