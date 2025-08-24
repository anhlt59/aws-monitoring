from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader

from src.modules.master.configs import TEMPLATE_DIR


def render_template(template_file: str, context: Dict[str, Any]) -> str:
    """
    Load and render a template file with a given context.
    Args:
        template_file (str): Relative path to the template file (e.g., 'templates/my_template.txt')
        context (dict): Dictionary of variables to inject into the template.
    Returns:
        str: Rendered template content as a string.
    """
    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)
    # Load and render the template
    template = env.get_template(template_file)
    return template.render(**context)
