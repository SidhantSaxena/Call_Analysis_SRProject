"""Functions to validate input text based on the predefined rules and patterns."""

import re
from typing import List, Tuple
from rapidfuzz import fuzz
from functionality.config_validators import validate_words_config

CONFIG_PATH = "words_config.yaml"
config = validate_words_config(CONFIG_PATH)

Greetings = config.Greetings or []
Disclaimers = config.Disclaimers or []
Closing_Statements = config.ClosingStatements or []
prohibited_phrases = config.ProhibitedPhrases or []
personal_information_patterns = config.PersonalInformationPatterns or {}
sensitive_information_patterns = config.SensitiveInformationPatterns or {}

# print(Greetings, Disclaimers, Closing_Statements, prohibited_phrases, personal_information_patterns, sensitive_information_patterns)


def required_phrase_validation(text) -> Tuple[int, int, int, List[str]]:
    """
    Comparing input text with predefined required phrases (Greetings, Disclaimers,
    Closing Statements) using the sorted token method to find similarities and
    returns the counts of valid phrases along with the categories of matched phrases.
    """
    greets, disclaims, closures, phrase_cat = 0, 0, 0, []

    for greet in Greetings:
        similarity = fuzz.token_sort_ratio(text, greet)
        if similarity > 55:
            greets = 1
            phrase_cat.append("Greetings")

    for disclaim in Disclaimers:
        similarity = fuzz.token_sort_ratio(text, disclaim)
        if similarity > 55:
            disclaims = 1
            phrase_cat.append("Disclaimers")

    for closure in Closing_Statements:
        similarity = fuzz.token_sort_ratio(text, closure)
        if similarity > 55:
            closures = 1
            phrase_cat.append("Closing_Statements")

    return (greets, disclaims, closures, phrase_cat)


def is_valid_atm_pin(text) -> bool:
    """
    Checks if the given text contains a valid ATM PIN.
    """

    patterns = sensitive_information_patterns.model_dump()  # Ensure dictionary format
    potential_atm_pins = re.findall(patterns.get("atm_pin", ""), text)

    personal_details = list(personal_information_patterns.model_dump().keys())

    for pin in potential_atm_pins:
        if any(re.search(patterns.get(p, ""), pin) for p in personal_details):
            continue
        else:
            return True
    return False


def detect_personal_details(text) -> Tuple[int, List[str]]:
    """
    Checks if important personal information (credit card number, ATM PIN, account password)
    is present in the given text and returns a flag indicating presence,
    along with the categories of sensitive information shared.
    """

    pil_present, pil_cat = 0, []
    # sensitive_information_patterns = {}
    for key, pattern in sensitive_information_patterns.model_dump().items():
        if (key != "atm_pin" and re.search(pattern, text)) or (
            key == "atm_pin" and is_valid_atm_pin(text)
        ):
            pil_present += 1
            pil_cat.append(key)
    
    for key, pattern in personal_information_patterns.model_dump().items():
        if (key != "atm_pin" and re.search(pattern, text)) or (
            key == "atm_pin" and is_valid_atm_pin(text)
        ):
            pil_present += 1
            pil_cat.append(key)

    return pil_present, pil_cat


def detect_prohibited_phrases(text) -> Tuple[int, List[str]]:
    """
    To detect profanity and inappropriate words present in the call transcript .
    """
    words_count, prohibited_words = 0, []

    text_token = text.split()

    for token in text_token:
        if token.lower() in prohibited_phrases:
            words_count += 1
            prohibited_words.append(token.lower())

    return words_count, prohibited_words
