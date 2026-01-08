from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("tagrefsorter")
except PackageNotFoundError:
    # package is not installed
    pass
