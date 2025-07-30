# harvest_automation/overlap.py
from dataclasses import replace

from .models import EventBlock


def split_overlaps(blocks:  list[EventBlock]) ->  list[EventBlock]:
    """Split partially-overlapping EventBlock intervals so none overlap."""
    # Sort by start time
    blocks.sort(key=lambda b: b.begin)
    result: list[EventBlock] = []

    for blk in blocks:
        # While there’s overlap with the last kept block, split the current one
        while result and blk.begin < result[-1].end:
            cut = result[-1].end
            # Left piece: same begin, trimmed to cut
            left = replace(blk, end=cut)
            # Right piece: start at cut, same end
            right = replace(blk, begin=cut)
            result.append(left)
            blk = right
        result.append(blk)

    return result
