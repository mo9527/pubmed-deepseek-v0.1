import os
import importlib.util
import sys

def import_models_from_directory(directory: str):
    print(f'Importing models...DIR: {directory}')
    project_root = os.path.abspath(os.path.join(directory, '..', '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    for filename in os.listdir(directory):
        if filename.endswith('.py') and filename not in ['__init__.py', 'base_model.py']:
            module_name = f"app.models.{filename[:-3]}"
            try:
                importlib.import_module(module_name)
                print(f"Successfully imported model: {module_name}")
            except Exception as e:
                print(f"Failed to import model {module_name}: {e}")

