import re
from typing import Callable
from string_processing import \
    find_indices, indices_to_slices, replace_outside_slices

SUSSIES = {
    # max length string: min length string
    'among us!': 'among us',
    'amongus': 'amongus',
    'amogus': 'amogus',
    'sus!': 'sus',
}
CENSORS = re.compile(r'\b' + '|'.join(['among', 'us', 'amogus', 'sus']) + r'\b', re.I)
# This should not:
# 1. Be an ending tag
# 2. Be part of a real comment
# 3. Contain any of the SUSSIES
NIMS = '\0' * 10 + '\1'

def reddit_spoiler(s: str) -> str:
    """Mark text as a spoiler on Reddit.

    >>> reddit_spoiler('amongus')
    '>!amongus!<'
    """
    return f'>!{s}!<'

def amongusify(text: str, spoiler: Callable[[str], str] = reddit_spoiler) -> str:
    """Amongus.

    >>> text = 'Are you smelting ore on Good Friday with us?'
    >>> amongusify(text)
    'A>!re you s!<m>!elting !<o>!re o!<n>! !<G>!ood!< >!Friday with !<us>!?!<'
    """
    # spoilers can't span multiple lines
    if '\n' in text:
        return '\n'.join(amongusify(line, spoiler) for line in text.splitlines())
    # Find closing tag of spoiler
    # This assumes spoilers have closing tags;
    # if they don't our job is much harder anyway
    spoilered = spoiler(NIMS)
    ending = spoilered[spoilered.index(NIMS) + len(NIMS):]
    # Store processed text so that we don't double-spoiler stuff
    processed = ''
    while text:
        for long, short in SUSSIES.items():
            left, sep, text = text.rpartition(ending)
            processed += left + sep # no-op if tag not found
            if not text:
                break
            indices = find_indices(long, text.casefold())
            if len(indices) < len(short):
                continue
            text = replace_outside_slices(text, indices_to_slices(indices), spoiler)
        else:
            left, sep, text = text.rpartition(ending)
            if sep:  # tag found, text has already been updated
                processed += left + sep
            else:
                processed, text = text, ''
            break
    return processed

def amongusify_censored(text: str, spoiler: Callable[[str], str] = reddit_spoiler) -> str:
    """Amongus, without those words.

    >>> text = 'Are you moping about among us undersea?'
    >>> amongusify(text)
    'A>!re you !<mo>!pi!<ng >!abo!<u>!t among u!<s>! undersea?!<'
    >>> amongusify_censored(text)
    'A>!re you !<mo>!pi!<ng >!abo!<u>!t among us under!<s>!ea?!<'
    """
    matches = CENSORS.findall(text)
    censored = CENSORS.sub(NIMS, text)
    censored = amongusify(censored, spoiler)
    text = censored
    # put censored pieces back into text
    for match in matches:
        text = text.replace(NIMS, match, 1)
    return text

if __name__ == '__main__':
    import doctest
    failures, _ = doctest.testmod()
    if not failures:
        try:
            while text := input():
                print(amongusify(text))
                print(amongusify_censored(text))
        except EOFError:
            pass
