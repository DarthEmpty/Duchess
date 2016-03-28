def ask(question, options, reject_note=""):
    """Asks the user a question continuously, accepting and returning only certain options
    and displaying a rejection notification if none of the options are correct.
    There is no 'reject_note' by default.
    'question' must be a string.
    'options' can be any, iterable type.
    'reject_note' must be a string."""

    choice = None
    while not choice:
        choice = input(question)
        if choice not in options:
            if reject_note:
                notify(reject_note)
            choice = None
    return choice


def notify(message):
    """Displays a message to the user and waits for their input to continue.
    'message' should be a string."""

    print(message)
    input("\nPress Enter to continue")


def prepareOptions(iterable):
    """Creates a string of numbers using the different sections of an iterable object.
    'iterable' must be of an iterable type."""

    options = ""

    for i in range(1, len(iterable) + 1):
        options += str(i)

    return options


def readRules():
    """Returns a list of the different sections of 'rules.txt' - the document
    of rules for Duchess."""

    sections = [""]
    n = 0
    line = " "  # So that, to begin with, bool(line) == True
    rules = open("rules.txt")

    while line:
        line = rules.readline()
        if line == "\n":  # Counting the number of "\n"s since the last block of text
            n += 1
        else:
            sections[-1] += line
            if n:  # line may just be a space between parts of a section
                n = 0

        if n >= 2:  # Each section is separated by "\n\n" in "rules.txt"
            sections.append("")
            n = 0

    rules.close()
    return sections
