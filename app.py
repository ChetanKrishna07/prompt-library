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

# Function to replace variables in the template
def replace_ignore_case(template: str, old: str, new: str) -> str:
    pattern = re.compile(re.escape(old), re.IGNORECASE)
    return pattern.sub(new, template)

# Function to build the final prompt
def build_prompt(template: str, variables: dict[str, str]) -> str:
    for key, value in variables.items():
        template = replace_ignore_case(template, f'[{key}]', value)
    return template

# Function to load prompts from a directory
def load_prompts(directory):
    prompts = {}
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), 'r') as file:
                prompts[filename[:-5]] = json.load(file)
    return prompts

# Function to save a new prompt to a directory
def save_prompt(directory, name, template, variable_names):
    prompt_data = {"template": template, "variable_names": variable_names}
    with open(os.path.join(directory, f"{name}.json"), 'w') as file:
        json.dump(prompt_data, file)

# Function to extract variable names from the template
def extract_variable_names(template):
    vars = [var.lower().replace(" ", "_") for var in re.findall(r'\[(.*?)\]', template)]
    return list(set(vars))

# Main function for the Streamlit app
def main():
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
                    st.experimental_rerun()
                else:
                    st.warning("Please provide a valid template for the prompt.")
            
            if st.button("Delete Prompt 🗑️"):
                os.remove(os.path.join(USER_PROMPT_DIR, f"{prompt_choice}.json"))
                st.success(f"Prompt '{prompt_choice}' deleted successfully!")
                st.experimental_rerun()
                
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
            save_prompt(USER_PROMPT_DIR, new_prompt_name, new_template, new_variable_names)
            st.success(f"New prompt '{new_prompt_name}' saved successfully!")
            st.experimental_rerun()
        else:
            st.warning("Please provide all details for the new prompt.")

if __name__ == "__main__":
    main()