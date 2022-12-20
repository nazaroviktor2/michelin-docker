"""File with bold function."""


def stars_to_highlight(string):
    """Function replaces * to <b> and </b>.

    Args:
        string: str - string with stars.

    Returns:
        str - string with tegs <b>.
    """
    cnt = 0
    for sym in string:
        if cnt == 1 and sym == '*':
            string = string.replace(sym, '</b>', 1)
            cnt = 0
        elif sym == '*':
            string = string.replace(sym, '<b>', 1)
            cnt += 1
    return string


