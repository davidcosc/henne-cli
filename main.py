import questionary
import sys
import yaml
import re
from questionary import Validator, ValidationError


class RegexValidator(Validator):
    """
    A questionary Validator subclass that validates input against a regex pattern.
    """

    def __init__(self, pattern):
        """
        Initialize the validator with a regex pattern.

        Args:
            pattern (str): A regex pattern string to validate input against.
        """
        self.pattern = re.compile(pattern)

    def validate(self, document):
        """
        Check if the input matches the regex pattern.

        Args:
            document (questionary.Document): The input document to validate.

        Raises:
            ValidationError: If the input does not fully match the regex pattern.
        """
        if not self.pattern.fullmatch(document.text):
            raise ValidationError(
                message="Input does not match the required format.",
                cursor_position=len(document.text)  # Move cursor to end of input
            )


def read_config(config_path):
    """
    Load and parse a YAML configuration file.

    Args:
        config_path (str): Path to the YAML config file.

    Returns:
        dict: Parsed YAML content as a Python dictionary.

    Exits:
        On file not found or YAML parsing error, prints an error and exits the program.
    """
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        questionary.print(f"\n[ERROR] File not found: {config_path}", style="bold red")
        sys.exit(1)
    except yaml.YAMLError as e:
        questionary.print("\n[ERROR] Invalid YAML syntax:", style="bold red")
        questionary.print(str(e), style="italic red")
        sys.exit(1)
    return config


def validate_question_schema(question, index):
    """
    Validate the schema of a single question dictionary.

    Checks for required fields, supported types, choices for selects,
    and validity of regex patterns for text questions.

    Args:
        question (dict): The question dictionary to validate.
        index (int): The question's 1-based index (for error reporting).

    Returns:
        bool: True if the question is valid, False otherwise.
    """
    allowed_types = {"select", "text"}
    valid = True

    q_type = question.get("type")
    name = question.get("name")
    message = question.get("message")
    choices = question.get("choices")
    validate_pattern = question.get("validate")

    # Check required fields
    if not all([q_type, name, message]):
        questionary.print(
            f"[WARNING] Question {index} is missing required fields (type, name, message).",
            style="yellow"
        )
        valid = False

    # Check allowed types
    if q_type not in allowed_types:
        questionary.print(
            f"[WARNING] Question {index}: Unsupported type '{q_type}'. Only 'select' and 'text' are allowed.",
            style="yellow"
        )
        valid = False

    # Check choices for select questions
    if q_type == "select":
        if not isinstance(choices, list) or not choices:
            questionary.print(
                f"[WARNING] Question {index}: 'select' type must include a non-empty 'choices' list.",
                style="yellow"
            )
            valid = False

    # Validate regex pattern if provided for text questions
    if q_type == "text" and validate_pattern is not None:
        try:
            re.compile(validate_pattern)
        except re.error:
            questionary.print(
                f"[WARNING] Question {index}: Invalid regex pattern in 'validate': {validate_pattern}",
                style="yellow"
            )
            valid = False

    return valid


def validate_config(config):
    """
    Validate the overall configuration dictionary.

    Ensures 'questions' key exists and contains a list,
    and that each question passes individual schema validation.

    Args:
        config (dict): Parsed YAML configuration dictionary.

    Exits:
        On missing or invalid 'questions' list or invalid questions,
        prints an error and exits the program.
    """
    questions = config.get("questions")
    if not isinstance(questions, list):
        questionary.print("\n[ERROR] YAML must contain a top-level 'questions' list.", style="bold red")
        sys.exit(1)

    # Validate each question
    all_valid = True
    for idx, q in enumerate(questions, start=1):
        if not validate_question_schema(q, idx):
            all_valid = False
    if not all_valid:
        questionary.print("\n[ERROR] One or more questions are invalid. Fix the YAML and try again.", style="bold red")
        sys.exit(1)


def create_questions(config):
    """
    Create questionary prompt objects from validated configuration.

    Supports 'select' and 'text' types, applying regex validation for text inputs
    when a 'validate' pattern is specified.

    Args:
        config (dict): Validated YAML configuration dictionary.

    Returns:
        list[questionary.Question]: A list of questionary prompt objects.
    """
    question_configs = config.get("questions")
    questions = []

    for q in question_configs:
        q_type = q["type"]
        name = q["name"]
        message = q["message"]
        choices = q.get("choices", [])
        validate_pattern = q.get("validate")

        if q_type == "select":
            question = questionary.select(message=message, choices=choices)
        else:  # q_type == "text"
            if validate_pattern:
                validator = RegexValidator(validate_pattern)
                question = questionary.text(message=message, validate=validator)
            else:
                question = questionary.text(message=message)

        question.name = name
        questions.append(question)

    return questions


def ask_questions(questions):
    """
    Prompt the user with the given questions and collect answers.

    Args:
        questions (list[questionary.Question]): List of questionary prompt objects.

    Returns:
        dict: A dictionary mapping question names to user responses.
    """
    answers = {}

    for q in questions:
        answer = q.ask()
        answers[q.name] = answer
        
    return answers


def get_user_settings(settings_path):
    """
    Main function to load questions from YAML, validate, prompt user, and return answers.

    Args:
        settings_path (str): Path to the YAML file containing question definitions.

    Returns:
        dict: User's answers keyed by question name.
    """
    config = read_config(settings_path)
    validate_config(config)
    questions = create_questions(config)
    return ask_questions(questions)


def parse_uw_last_pairs(answers):
    """
    Parse the combined input from a single text field containing UW=Last pairs.

    For example: "SE=15MW,N=20MW" -> [{"type": "SE", "last": "15MW"}, {"type": "N", "last": "20MW"}]

    Args:
        answers (dict): Dictionary containing user input with key 'UWLastPaare'.

    Returns:
        list[dict]: A list of dictionaries with keys 'type' and 'last' for each UW.
    """
    pairs = answers["UWLastPaare"].split(",")
    ordered_uws = []

    for pair in pairs:
        uw = {}
        uw_type, last = pair.split("=")
        uw["type"] = uw_type
        uw["last"] = last
        ordered_uws.append(uw)

    return ordered_uws


# Example usage
if __name__ == "__main__":
    answers = get_user_settings("config.yaml")
    answers["UWs"] = parse_uw_last_pairs(answers)
    print(answers)
