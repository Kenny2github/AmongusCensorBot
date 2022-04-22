from typing import Callable, Optional

def find_indices(source: str, text: str) -> list[int]:
    """Find the indices of each character from `source` in `text`,
    where each index must be greater than the last.

    >>> text = 'Are you smelting ore on Good Friday with us?'
    >>> find_indices('amongus', text.casefold())
    [0, 9, 17, 22, 24, 41, 42]
    >>> find_indices('amongus', 'How about... hmm, maybe not.'.casefold())
    [4, 14, 25]
    """
    indices = []
    index = -1 # so that index + 1 is 0 initially
    for letter in source:
        index = text.find(letter, index + 1)
        if index == -1:
            break
        indices.append(index)
    return indices

def find_all_indices(source: str, text: str) -> Optional[list[int]]:
    """Same as `find_indices`, but returns `None`
    if not all characters are found.

    >>> text = 'Are you smelting ore on Good Friday with us?'
    >>> find_all_indices('amongus', text.casefold())
    [0, 9, 17, 22, 24, 41, 42]
    >>> find_all_indices('amongus', 'How about... hmm, maybe not.'.casefold())
    >>> # None

    """
    indices = find_indices(source, text)
    if len(indices) < len(source):
        return None
    return indices

def indices_to_slices(indices: list[int]) -> list[slice]:
    """Convert a list of indices to a list of contiguous slices.

    >>> indices_to_slices([0, 9, 10, 11, 30, 31, 40])
    [slice(0, 1, 1), slice(9, 12, 1), slice(30, 32, 1), slice(40, 41, 1)]
    """
    start = end = indices[0]
    slices = []
    for index in indices[1:]:
        if index == end + 1:
            end = index # extend contiguous slice
        else:
            slices.append(slice(start, end + 1, 1))
            start = end = index
    # handle last slice
    slices.append(slice(start, end + 1, 1))
    return slices

def _qq(a, b):
    """Nullish coalescing function."""
    if a is None:
        return b
    return a

def replace_by_slices(text: str, slices: list[slice],
                      replacement: Callable[[str], str]) -> str:
    """Replace all `slices` of `text` with the `replacement` function.
    Each slice must be

    >>> slices = [slice(2), slice(11, 13)]
    >>> text = 'It must be so hard.'
    >>> replace_by_slices(text, slices, lambda s: f'({s})')
    '(It) must be (so) hard.'
    >>> slices = [slice(3, 7), slice(18, None)] # until end
    >>> replace_by_slices(text, slices, lambda s: f'({s})')
    'It (must) be so hard(.)'
    """
    last_slice = slice(0) # last slice starts at start of string
    pieces = []
    for sl in slices:
        # piece in between last slice and this one
        pieces.append(text[_qq(last_slice.stop, len(text)):_qq(sl.start, 0)])
        # transform actual sliced piece
        pieces.append(replacement(text[sl]))
        last_slice = sl
    pieces.append(text[_qq(last_slice.stop, len(text)):])
    return ''.join(pieces)

def replace_outside_slices(text: str, slices: list[slice],
                           replacement: Callable[[str], str]) -> str:
    """Replace all `slices` of `text` with the `replacement` function.
    Each slice must be

    >>> slices = [slice(2), slice(11, 13)]
    >>> text = 'It must be so hard.'
    >>> replace_outside_slices(text, slices, lambda s: f'({s})')
    'It( must be )so( hard.)'
    >>> slices = [slice(3, 7), slice(18, None)] # until end
    >>> replace_outside_slices(text, slices, lambda s: f'({s})')
    '(It )must( be so hard).'
    """
    last_slice = slice(0) # last slice starts at start of string
    pieces = []
    for sl in slices:
        # transform piece in between last slice and this one
        pieces.append(replacement(
            text[_qq(last_slice.stop, len(text)):_qq(sl.start, 0)]))
        # leave actual sliced piece alone
        pieces.append(text[sl])
        last_slice = sl
    pieces.append(replacement(
        text[_qq(last_slice.stop, len(text)):]))
    return ''.join(pieces).replace(replacement(''), '')

if __name__ == '__main__':
    import doctest
    doctest.testmod()
