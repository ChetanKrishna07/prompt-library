import streamlit as st
import re
import os
import json

# Directories for storing prompts
USER_PROMPT_DIR = "user_prompts"
PRE_PROMPT_DIR = "pre_prompts"

# Ensure directories exist
os.makedirs(USER_PROMPT_DIR, exist_ok=True)
os.makedirs(PRE_PROMPT_DIR, exist_ok=True)

def replace_ignore_case(template: str, old: str, new: str) -> str:
    """
    Replace all occurrences of a substring in a template, ignoring case.

    Args:
        template (str): The original template string.
        old (str): The substring to be replaced.
        new (str): The substring to replace with.

    Returns:
        str: The template with all occurrences of the old substring replaced by the new substring.
    """
    pattern = re.compile(re.escape(old), re.IGNORECASE)
    return pattern.sub(new, template)

def build_prompt(template: str, variables: dict[str, str]) -> str:
    """
    Build the final prompt by replacing placeholders in the template with provided values.

    Args:
        template (str): The template string with placeholders.
        variables (dict[str, str]): A dictionary of variables where keys are placeholders and values are their replacements.

    Returns:
        str: The final prompt with placeholders replaced by their respective values.
    """
    for key, value in variables.items():
        template = replace_ignore_case(template, f'[{key}]', value)
    return template

def load_prompts(directory: str) -> dict:
    """
    Load prompts from a specified directory.

    Args:
        directory (str): The directory from which to load the prompts.

    Returns:
        dict: A dictionary of prompts loaded from the directory.
    """
    prompts = {}
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), 'r') as file:
                prompts[filename[:-5]] = json.load(file)
    return prompts

def save_prompt(directory: str, name: str, template: str, variable_names: list[str]) -> bool:
    """
    Save a new prompt to a specified directory.

    Args:
        directory (str): The directory where the prompt will be saved.
        name (str): The name of the prompt.
        template (str): The template string of the prompt.
        variable_names (list[str]): A list of variable names used in the template.

    Returns:
        bool: True if the prompt was saved successfully, False if a prompt with the same name already exists.
    """
    prompt_data = {"template": template, "variable_names": variable_names}
    with open(os.path.join(directory, f"{name}.json"), 'w') as file:
        json.dump(prompt_data, file)

def extract_variable_names(template: str) -> list[str]:
    """
    Extract variable names from the template.

    Args:
        template (str): The template string with placeholders.

    Returns:
        list[str]: A list of unique variable names found in the template.
    """
    vars = [var.lower().replace(" ", "_") for var in re.findall(r'\[(.*?)\]', template)]
    return list(set(vars))

def main():
    """
    Main function for the Streamlit app to build and manage dynamic prompts.

    Displays the UI components for selecting, editing, and creating prompt templates.
    """
    st.title("Dynamic Prompt Builder")

    # Load pre-built and user prompts
    pre_prompts = load_prompts(PRE_PROMPT_DIR)
    user_prompts = load_prompts(USER_PROMPT_DIR)

    prompt_choice = st.selectbox(
        "Choose a prompt",
        ["Select a prompt"] + list(pre_prompts.keys()) + list(user_prompts.keys())
    )

    if prompt_choice != "Select a prompt":
        if prompt_choice in pre_prompts:
            prompt_data = pre_prompts[prompt_choice]
            st.subheader(f"Pre-built Prompt: {prompt_choice}")
            is_pre_built = True
        else:
            prompt_data = user_prompts[prompt_choice]
            st.subheader(f"User Prompt: {prompt_choice}")
            is_pre_built = False

        template = prompt_data["template"]
        variable_names = prompt_data["variable_names"]

        st.header("Enter Variables")
        variable_dict = {}
        for var_name in variable_names:
            var_value = st.text_input(f"Enter value for {var_name}", key=var_name)
            if var_value:
                variable_dict[var_name] = var_value

        if st.button("Generate"):
            if len(variable_dict) == len(variable_names):
                output_prompt = build_prompt(template, variable_dict)
                st.subheader("Generated Prompt:")
                st.text(output_prompt)
            else:
                st.warning("Please fill in all the variables.")

        if not is_pre_built:
            st.header("Edit Prompt Template ✏️")
            new_template = st.text_area("Edit prompt template", value=template)

            if st.button("Save Edited Prompt"):
                if new_template:
                    new_variable_names = extract_variable_names(new_template)
                    for var_name in [var for var in re.findall(r'\[(.*?)\]', new_template)]:
                        new_template = replace_ignore_case(new_template, f'[{var_name}]', f'[{var_name.lower().replace(" ", "_")}]')
                        
                    save_prompt(USER_PROMPT_DIR, prompt_choice, new_template, new_variable_names)

                    st.success(f"Prompt '{prompt_choice}' updated successfully!")
                    
                else:
                    st.warning("Please provide a valid template for the prompt.")
            
            if st.button("Delete Prompt 🗑️"):
                os.remove(os.path.join(USER_PROMPT_DIR, f"{prompt_choice}.json"))
                st.success(f"Prompt '{prompt_choice}' deleted successfully!")
                
        else:
            st.subheader("Prompt Template")
            st.text(template)
            st.warning("Pre-built prompts cannot be edited.")

    st.header("Add New Prompt Template")
    new_prompt_name = st.text_input("Enter new prompt name")
    new_prompt_name = new_prompt_name.strip().replace(" ", "_").lower()
    new_template = st.text_area("Enter new prompt template")

    if new_template:
        new_variable_names = extract_variable_names(new_template)
        
        for var_name in [var for var in re.findall(r'\[(.*?)\]', new_template)]:
            new_template = replace_ignore_case(new_template, f'[{var_name}]', f'[{var_name.lower().replace(" ", "_")}]')

    if st.button("Save New Prompt"):
        if new_prompt_name and new_template and new_variable_names:
            if os.path.exists(os.path.join(USER_PROMPT_DIR, f"{new_prompt_name}.json")):
                save_prompt(USER_PROMPT_DIR, new_prompt_name, new_template, new_variable_names)
                st.success(f"New prompt '{new_prompt_name}' saved successfully!")
            else:
                st.error(f"Prompt '{new_prompt_name}' already exists. Please choose a different name.")
        else:
            st.warning("Please provide all details for the new prompt.")

if __name__ == "__main__":
    main()
