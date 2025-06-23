import questionary
import sys
import yaml

def validate_question_schema(question, index):
    """
    Validate a single question dictionary.

    Args:
        question (dict): The question to validate.
        index (int): The index of the question for error display.

    Returns:
        bool: True if valid, False otherwise.
    """
    allowed_types = {"select", "confirm"}
    valid = True

    q_type = question.get("type")
    name = question.get("name")
    message = question.get("message")
    choices = question.get("choices")

    # Check required fields
    if not all([q_type, name, message]):
        questionary.print(
            f"[WARNING] Question {index} is missing required fields (type, name, message).",
            style="yellow"
        )
        valid = False

    # Check type support
    if q_type not in allowed_types:
        questionary.print(
            f"[WARNING] Question {index}: Unsupported type '{q_type}'. Only 'select' and 'confirm' are allowed.",
            style="yellow"
        )
        valid = False

    # Check choices for select
    if q_type == "select":
        if not isinstance(choices, list) or not choices:
            questionary.print(
                f"[WARNING] Question {index}: 'select' type must include a non-empty 'choices' list.",
                style="yellow"
            )
            valid = False

    return valid


def load_questions_from_yaml(yaml_path):
    """
    Load a YAML file and generate a list of validated questionary prompt objects.

    Returns only prompts of type 'select' and 'confirm'.

    Args:
        yaml_path (str): Path to the YAML file.

    Returns:
        list[questionary.Question]: A list of questionary prompts, or empty if validation fails.
    """
    try:
        with open(yaml_path, "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        questionary.print(f"\n[ERROR] File not found: {yaml_path}", style="bold red")
        sys.exit(1)
    except yaml.YAMLError as e:
        questionary.print("\n[ERROR] Invalid YAML syntax:", style="bold red")
        questionary.print(str(e), style="italic red")
        sys.exit(1)

    questions = config.get("questions")
    if not isinstance(questions, list):
        questionary.print("\n[ERROR] YAML must contain a top-level 'questions' list.", style="bold red")
        sys.exit(1)

    # Validate structure
    all_valid = True
    for idx, q in enumerate(questions, start=1):
        if not validate_question_schema(q, idx):
            all_valid = False
    if not all_valid:
        questionary.print("\n[ERROR] One or more questions are invalid. Fix the YAML and try again.", style="bold red")
        sys.exit(1)

    # Create prompts
    prompts = []
    for q in questions:
        q_type = q["type"]
        name = q["name"]
        message = q["message"]
        choices = q.get("choices", [])

        if q_type == "select":
            question = questionary.select(message=message, choices=choices)
        else:
            question = questionary.confirm(message=message)

        question.name = name
        prompts.append(question)

    return prompts


def ask_questions_and_get_answers(questions):
    """
    Ask a list of questionary questions and collect answers.

    Args:
        questions (list[questionary.Question]): The prompts to ask.

    Returns:
        dict: A dictionary of answers.
    """
    answers = []

    for question in questions:
        answers.append(question.ask())
        
    return answers


def get_user_settings(settings_path):
    """
    Load questions from a YAML file, prompt the user, and return their responses.

    This function loads a list of validated 'select' or 'confirm' questions from the specified
    YAML file, prompts the user using questionary, and collects the answers.

    Args:
        settings_path (str): Path to the YAML file containing the question configuration.

    Returns:
        list: A list of user responses, in the same order as the questions in the YAML file.
    """
    questions = load_questions_from_yaml(settings_path)
    return ask_questions_and_get_answers(questions)


# Example usage
if __name__ == "__main__":
    answers = get_user_settings("config.yaml")
    print(answers)
