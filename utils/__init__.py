import os


def path(base: str, resource: str):
    return os.path.join(os.path.dirname(base), resource)
