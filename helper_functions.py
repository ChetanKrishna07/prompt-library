import re
from bson import ObjectId

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

def document_to_dict(doc):
    """
    Convert MongoDB document to a JSON-serializable dictionary.
    """
    return {k: str(v) if isinstance(v, ObjectId) else v for k, v in doc.items()}

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
