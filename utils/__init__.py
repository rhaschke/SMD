import os
import numpy as np
from collections import deque
from typing import Iterable


def path(base: str, resource: str):
    return os.path.join(os.path.dirname(base), resource)


def rotate(items: Iterable, amount: int):
    items = deque(items)
    items.rotate(amount)
    return items


# string used to represent that no team runs on a specific track
no_team_str = "---"
