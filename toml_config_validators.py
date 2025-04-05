import tomli
from pydantic import BaseModel, Field
from typing import List


class ProjectConfig(BaseModel):
    name: str = Field(..., description="Project name")
    version: str = Field(..., description="Project version")
    description: str = Field(..., description="Project description")
    readme: str = Field(..., description="Path to README file")
    requires_python: str = Field(
        ..., alias="requires-python", description="Python version requirement"
    )
    dependencies: List[str] = Field(..., description="List of dependencies")


class PyProject(BaseModel):
    project: ProjectConfig


def validate_toml_config(file_path: str) -> PyProject:
    """Reads and validates a TOML configuration file."""
    with open(file_path, "rb") as f:
        data = tomli.load(f)
    return PyProject(**data)


# config = validate_toml_config("pyproject.toml")
# print(config)
