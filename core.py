from openai import OpenAI
import mcschematic
import sys
import json

from log_writer import logger
import config

def initialize():
    """
    Initializes the software.

    This function logs the software launch, including the version number and platform.

    Args:
        None

    Returns:
        None
    """
    logger(f"Launch. Software version {config.VERSION_NUMBER}, platform {sys.platform}")

def askgpt(system_prompt: str, user_prompt: str, model_name: str):
    """
    Interacts with ChatGPT using the specified prompts.

    Args:
        system_prompt (str): The system prompt.
        user_prompt (str): The user prompt.

    Returns:
        str: The response from ChatGPT.
    """
    client = OpenAI(api_key=config.API_KEY, base_url=config.BASE_URL)
    logger("Initialized the OpenAI client.")

    # Define the messages for the conversation
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    logger(f"askgpt: system {system_prompt}")
    logger(f"askgpt: user {user_prompt}")

    # Create a chat completion
    response = client.chat.completions.create(
        model=model_name,
        response_format={"type": "json_object"},
        messages=messages
    )

    logger(f"askgpt: response {response}")

    # Extract the assistant's reply
    assistant_reply = response.choices[0].message.content
    logger(f"askgpt: extracted reply {assistant_reply}")
    return assistant_reply

def text_to_schem(text: str):
    """
    Converts a JSON string to a Minecraft schematic.

    Args:
        text (str): The JSON string to convert.
        
    Returns:
        mcschematic.MCSchematic: The Minecraft schematic.
    
    """
    try:
        data = json.loads(text)
        block_id_dict = {}
        logger(f"text_to_command: loaded JSON data {data}")
        schematic = mcschematic.MCSchematic()

        # Iterate over the materials
        for material in data["materials"]:
            key, value = material.split(": ")
            block_id_dict[key.strip()] = value.strip('"')

        # Iterate over the structures
        for structure in data["structures"]:
            floor = structure["floor"]
            structure_data = structure["structure"]

            # Iterate over the rows of the structure
            rows = structure_data.split("\n")

            for y, row in enumerate(rows):
                # Iterate over the blocks in each row
                for x, block_id in enumerate(row):
                    # Get the corresponding block from the materials dictionary
                    block = block_id_dict.get(block_id)
                    if block: 
                        schematic.setBlock((x, floor, y), block)
        return schematic
    
    except (json.decoder.JSONDecodeError, KeyError, TypeError, ValueError, AttributeError, IndexError) as e:
        logger(f"text_to_command: failed to load JSON data. Error: {e}")
        return None

def input_version_to_mcs_tag(input_version):
    """
    Converts an input version string to the corresponding MCSchematic tag.

    Args:
        input_version (str): The input version string in the format "X.Y.Z".

    Returns:
        str: The MCSchematic tag corresponding to the input version.

    Example:
        >>> input_version_to_mcs_tag("1.20.1")
        'JE_1_20_1'
    """
    version = input_version.split(".")
    return getattr(mcschematic.Version, f"JE_{version[0]}_{version[1]}_{version[2]}")

if __name__ == "__main__":
    print("This script is not meant to be run directly. Please run console.py instead.")