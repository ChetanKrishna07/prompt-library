from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import re
from helper_functions import replace_ignore_case, document_to_dict, extract_variable_names

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGODB_URI")

# MongoDB client
client = MongoClient(MONGO_URI)
db = client["prompt_library"]
collection = db["prompt_templates"]

app = FastAPI()

class Prompt(BaseModel):
    name: str
    template: str
    type: str

class UpdatePrompt(BaseModel):
    name: str
    new_template: str
    new_variable_names: list[str]
    
class BuildPrompt(BaseModel):
    template: str
    variables: dict[str, str]


@app.post("/build_prompt/")
async def build_prompt(build_prompt: BuildPrompt):
    """
    Build the final prompt by replacing placeholders in the template with provided values.
    """
    template = build_prompt.template
    print(f"Building prompt for template: {template} with variables: {build_prompt.variables}")
    for key, value in build_prompt.variables.items():
        template = replace_ignore_case(template, f'[{key}]', value)
    print(f"Generated prompt: {template}")
    return {"prompt": template}

@app.get("/load_prompts/")
async def load_prompts():
    """
    Load prompts from the MongoDB collection.
    """
    print("Loading prompts from MongoDB")
    prompts = {}
    for document in collection.find():
        doc_dict = document_to_dict(document)
        prompts[doc_dict["name"]] = doc_dict
    print(f"Loaded prompts: {prompts.keys()}")
    return prompts

@app.post("/save_prompt/")
async def save_prompt(prompt: Prompt):
    """
    Save a new prompt to the MongoDB collection.
    """
    print(f"Saving new prompt: {prompt.name}")
    if collection.find_one({"name": prompt.name}):
        print(f"Prompt with name {prompt.name} already exists")
        raise HTTPException(status_code=400, detail="Prompt with this name already exists")
    
    
    var_names = extract_variable_names(prompt.template)
    
    if len(var_names) == 0:
        print(f"No variables found in the template")
        raise HTTPException(status_code=400, detail="No variables found in the template")
    
    for var_name in [var for var in re.findall(r'\[(.*?)\]', prompt.template)]:
        prompt.template = replace_ignore_case(prompt.template, f'[{var_name}]', f'[{var_name.lower().replace(" ", "_")}]')
    
    prompt_data = {"name": prompt.name, "prompt_template": prompt.template, "variables": var_names, "type": prompt.type}
    collection.insert_one(prompt_data)
    print(f"Prompt {prompt.name} saved successfully")
    return {"success": True, "template": prompt.template, "variables": var_names, "type": prompt.type}

@app.put("/update_prompt/")
async def update_prompt(prompt: UpdatePrompt):
    """
    Update an existing prompt in the MongoDB collection.
    """
    print(f"Updating prompt: {prompt.name}")
    if not collection.find_one({"name": prompt.name}):
        print(f"Prompt with name {prompt.name} not found")
        raise HTTPException(status_code=404, detail="Prompt not found")

    for var_name in [var for var in re.findall(r'\[(.*?)\]', prompt.new_template)]:
        prompt.new_template = replace_ignore_case(prompt.new_template, f'[{var_name}]', f'[{var_name.lower().replace(" ", "_")}]')
        
    collection.update_one(
        {"name": prompt.name},
        {"$set": {"prompt_template": prompt.new_template, "variables": prompt.new_variable_names}}
    )
    print(f"Prompt {prompt.name} updated successfully")
    return {"success": True}

@app.delete("/delete_prompt/{name}")
async def delete_prompt(name: str):
    """
    Delete an existing prompt from the MongoDB collection.
    """
    print(f"Deleting prompt: {name}")
    if not collection.find_one({"name": name}):
        print(f"Prompt with name {name} not found")
        raise HTTPException(status_code=404, detail="Prompt not found")

    collection.delete_one({"name": name})
    print(f"Prompt {name} deleted successfully")
    return {"success": True}
