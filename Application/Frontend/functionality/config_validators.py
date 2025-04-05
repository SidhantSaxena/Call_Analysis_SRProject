"""Validating the words_config.yaml file using Pydantic."""

from pydantic import BaseModel, ConfigDict
from pathlib import Path
from typing import List, Union
import yaml
from rich.console import Console
from rich.traceback import install

install()
console = Console()


class PersonalInformationPatterns(BaseModel):
    phone_number: str = r"\d{4}-\d{4}"
    date_dd_mm_yyyy: str = r"\d{2}-\d{2}-\d{4}"
    multi_4_digit_patt: str = r"\b\d{4}\b.*\b\d{4}\b"


class SensitiveInformationPatterns(BaseModel):
    credit_card: str = r"\b(?:\d{4}[- ]?){3}\d{4}\b"
    atm_pin: str = r"\b\d{4}\b"
    account_password: str = (
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    )


class WordsConfigSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    Greetings: List[str]
    Disclaimers: List[str]
    ProhibitedPhrases: List[str]
    ClosingStatements: List[str]
    PersonalInformationPatterns: PersonalInformationPatterns
    SensitiveInformationPatterns: SensitiveInformationPatterns


def validate_words_config(file_name: str) -> Union[WordsConfigSchema, Exception]:
    try:
        with Path(file_name).open(encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f)

        config = WordsConfigSchema(**yaml_data)
        console.print("[bold green]Configuration is valid![/bold green]")
        # console.print(config.model_dump_json(indent=2))
        return config
    except Exception as e:
        console.print(f"[bold red]Validation error:[/bold red] {e}", style="red")
        return e


# if __name__ == "__main__":
#     validate_words_config("words_config.yaml")
