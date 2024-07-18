import re
from datetime import datetime

def tune_text(text):
    # Replace comma with two dots in text
    text = text.replace(",", ".. …")
    text = text.replace("?!", "??")

    # Find any single period at the end of sentence followed by a space
    pattern = r"([a-zA-Z])\. "
    text = re.sub(pattern, r"\1.. ", text)
    # Same with exclamation mark
    pattern = r"([a-zA-Z])\! "
    text = re.sub(pattern, r"\1!!.. ", text)
    # Same with question mark
    pattern = r"([a-zA-Z])\? "
    text = re.sub(pattern, r"\1??.. ", text)

    # Remove specific phrases
    # For example for Rick
    patterns_to_remove = [
        r"\*burps loudly\*",
        r"\*belches\*",
        r"\*burps\*",
        r"\*Burp\*",
        r"\*burp\*",
        r"\*laughs maniacally\*",
        r"\*takes a swig from flask\*",
        r"<response>",
        r"</response>"
    ]

    for pattern in patterns_to_remove:
        text = re.sub(pattern, "", text)

    # Remove everything between <inner_monologue> and </inner_monologue>
    text = re.sub(r"<inner_monologue>.*?</inner_monologue>", "", text, flags=re.DOTALL)

    return text

def convert_timestamp_to_date(timestamp):
    if timestamp:
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
    return None
