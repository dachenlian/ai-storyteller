import re

# Verbose regex pattern with comments:
PATTERN_VERBOSE = r"""
^               # Start of the line (due to re.MULTILINE)
\[              # Match the literal opening square bracket '['
\d{2}           # Match exactly two digits (minutes 'mm')
:               # Match the literal colon ':'
\d{2}           # Match exactly two digits (seconds 'ss')
\.              # Match the literal dot '.' (needs escape)
\d{2}           # Match exactly two digits (hundredths 'xx')
\]              # Match the literal closing square bracket ']'
.* # Match any character (except newline) zero or more times (the lyric text)
$               # End of the line (due to re.MULTILINE)
"""


def clean_lyric_lines(lyrics: str | None) -> list[str]:
    """
    Cleans the lyrics by removing lines that do not match the specified pattern.

    Args:
        lyrics (str): The lyrics to be cleaned.

    Returns:
        list[str]: A list of cleaned lyric lines.
    """
    # Compile the regex pattern with re.VERBOSE for better readability
    pattern_verbose = re.compile(PATTERN_VERBOSE, re.MULTILINE | re.VERBOSE)
    # Use re.findall with re.MULTILINE and re.VERBOSE flags combined
    # Use the bitwise OR operator '|' to combine flags
    valid_lyric_lines = re.findall(
        pattern_verbose,
        lyrics or "",  # Use an empty string if lyrics is None
    )
    valid_lyric_lines = [
        cleaned_line
        for line in valid_lyric_lines
        if (cleaned_line := line.strip()) != ""
    ]
    return valid_lyric_lines
