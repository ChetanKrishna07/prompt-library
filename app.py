import streamlit as st
import requests
from helper_functions import extract_variable_names, replace_ignore_case

API_URL = "http://localhost:8000"

def main():
    """
    Main function for the Streamlit app to build and manage dynamic prompts.

    Displays the UI components for selecting, editing, and creating prompt templates.
    """
    st.title("Dynamic Prompt Builder")

    # Load prompts from MongoDB
    print("Loading prompts from API")
    response = requests.get(f"{API_URL}/load_prompts/")
    prompts = response.json()
    print(f"Loaded prompts: {prompts.keys()}")

    prompt_choice = st.selectbox(
        "Choose a prompt",
        ["Select a prompt template"] + list(prompts.keys())
    )

    if prompt_choice != "Select a prompt template":
        prompt_data = prompts[prompt_choice]
        st.subheader(f"Prompt Template: {prompt_choice} ({prompt_data['type']})")

        template = prompt_data["prompt_template"]
        variable_names = prompt_data["variables"]
        prompt_type = prompt_data["type"]

        st.header("Enter Variables")
        variable_dict = {}
        for var_name in variable_names:
            var_value = st.text_input(f"Enter value for {var_name}", key=var_name)
            if var_value:
                variable_dict[var_name] = var_value

        if st.button("Generate"):
            if len(variable_dict) == len(variable_names):
                print(f"Generating prompt for template: {template} with variables: {variable_dict}")
                response = requests.post(f"{API_URL}/build_prompt/", json={"template": template, "variables": variable_dict})
                output_prompt = response.json().get("prompt")
                st.subheader("Generated Prompt:")
                st.text(output_prompt)
                print(f"Generated prompt: {output_prompt}")
            else:
                st.warning("Please fill in all the variables.")

        if prompt_type == "user_defined":
            st.header("Edit Prompt Template ✏️")
            new_template = st.text_area("Edit prompt template", value=template)

            if st.button("Save Edited Prompt"):
                if new_template:
                    new_variable_names = extract_variable_names(new_template)
                    print(f"Updating prompt: {prompt_choice} with new template: {new_template}")
                    response = requests.put(f"{API_URL}/update_prompt/", json={"name": prompt_choice, "new_template": new_template, "new_variable_names": new_variable_names})
                    if response.status_code == 200:
                        st.success(f"Prompt '{prompt_choice}' updated successfully!")
                        print(f"Prompt '{prompt_choice}' updated successfully")
                    else:
                        st.error(f"Failed to update prompt '{prompt_choice}': {response.json().get('detail')}")
                        print(f"Failed to update prompt '{prompt_choice}': {response.json().get('detail')}")
                else:
                    st.warning("Please provide a valid template for the prompt.")

            if st.button("Delete Prompt 🗑️"):
                print(f"Deleting prompt: {prompt_choice}")
                response = requests.delete(f"{API_URL}/delete_prompt/{prompt_choice}")
                if response.status_code == 200:
                    st.success(f"Prompt '{prompt_choice}' deleted successfully!")
                    print(f"Prompt '{prompt_choice}' deleted successfully")
                else:
                    st.error(f"Failed to delete prompt '{prompt_choice}': {response.json().get('detail')}")
                    print(f"Failed to delete prompt '{prompt_choice}': {response.json().get('detail')}")

        else:
            st.subheader("Prompt Template")
            st.text(template)
            st.warning("Pre-built prompts cannot be edited.")

    st.header("Add New Prompt Template")
    new_prompt_name = st.text_input("Enter new prompt name")
    new_prompt_name = new_prompt_name.strip().replace(" ", "_").lower()
    new_template = st.text_area("Enter new prompt template")


    if st.button("Save New Prompt Template"):
        print(f"Saving new prompt template: {new_template}")
        response = requests.post(f"{API_URL}/save_prompt/", json={"name": new_prompt_name, "template": new_template, "type": "user_defined"})
        if response.status_code == 200:
            st.success(f"New prompt template '{new_prompt_name}' saved successfully!")
            print(f"New prompt template'{new_prompt_name}' saved successfully with template: {response.json().get('template')} and variables: {response.json().get('variables')}")
        else:
            st.error(f"{response.json().get('detail')}")
            print(f"{response.json().get('detail')}")

if __name__ == "__main__":
    main()
