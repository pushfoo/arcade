from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Type, cast


from .vfs import VirtualFile, Vfs, F


__all__ = (
    'ensure_pattern',
    'get_module_path',
    'EMPTY_TUPLE',
    'F',
    'ParseKind',
    'SharedPaths',
    'NotExcludedBy',
    'VirtualFile',
    'Vfs'
)


EMPTY_TUPLE = tuple()


class SharedPaths:
    """These are often used to set up a Vfs and open files."""
    REPO_UTILS_DIR = Path(__file__).parent.parent.resolve()
    REPO_ROOT = REPO_UTILS_DIR.parent
    ARCADE_ROOT = REPO_ROOT / "arcade"
    DOC_ROOT = REPO_ROOT / "doc"
    API_DOC_ROOT = DOC_ROOT / "api_docs"


def is_iterable(item) -> bool:
    try:
        iter(item)
    except Exception as _:
        return False

    return True


class NotExcludedBy:
    """Helper predicate for exclusion.

    This is here because we may eventually define excludes at per-module
    level in our config below instead of a single list.
    """
    def __init__(self, collection: Iterable):
        self.items = set(collection)

    def __call__(self, item) -> bool:
        return item not in self.items


_VALID_MODULE_SEGMENT = re.compile(r"[_a-zA-Z][_a-z0-9]*")


def get_module_path(module: str, root = SharedPaths.REPO_ROOT) -> Path:
    """Quick-n-dirty module path estimation relative to the repo root.

    :param module: A module path in the project.
    :raises ValueError: When a can't be computed.
    :return: A
    """
    # Convert module.name.here to module/name/here
    current = root
    for index, part in enumerate(module.split('.')):
        if not _VALID_MODULE_SEGMENT.fullmatch(part):
            raise ValueError(
                f'Invalid module segment at index {index}: {part!r}')
        # else:
        #   print(current, part)
        current /= part

    # Account for the two kinds of modules:
    # 1. arcade/module.py
    # 2. arcade/module/__init__.py
    as_package = current / "__init__.py"
    have_package = as_package.is_file()
    as_file = current.with_suffix('.py')
    have_file = as_file.is_file()

    # TODO: When 3.10 becomes our min Python, make this a match-case?
    if have_package and have_file:
        raise ValueError(
            f"Module conflict between {as_package} and {as_file}")
    elif have_package:
        current = as_package
    elif have_file:
        current = as_file
    else:
        raise ValueError(
            f"No folder package or file module detected for "
            f"{module}")

    return current


def ensure_pattern(pattern: str | re.Pattern) -> re.Pattern:
    if isinstance(pattern, re.Pattern):
        return pattern
    elif isinstance(pattern, str):
        return re.compile(pattern)
    raise TypeError(
        f"Expected a str or re.Pattern, not a {type(pattern)}"
        f" of value {pattern}")


def _auto_name(cls: type, autodir: str) -> str:
    return f"auto{autodir or cls.__name__.lower()}"

def _crossref(cls: type, name: str) -> str:
    return f"{name or ':py:' + cls.__name__.lower() + ':'}:"


class ParseKind:
    """Per-script parsing helpers.

    1. Subclass to auto-add to the kind_to_sphinx_auto_directive table
    2. for kind, autodoc_directive in ParseKind.kind_to_sphinx_directive.items():
    """
    pattern: re.Pattern
    crossref_directive: str
    autodoc_directive: str


    def __init_subclass__(
            cls,
            pattern: re.Pattern | str | None = None,
            crossref_directive: str | None = None,
            autodoc_directive: str | None = None,
            **kwargs
    ):
        super().__init_subclass__(**kwargs)
        cls.pattern = ensure_pattern(pattern)
        cls.crossref_directive = _crossref(cls, crossref_directive)
        cls.autodoc_directive = _auto_name(cls, autodoc_directive)

    def __init__(self, name: str):
        if type(self) is ParseKind:
            raise TypeError("Base ParseKind is abstract, subclass it")
        self.name: str = name

    @classmethod
    def findall(cls, s: str) -> list[Self]:
        return [cls(item) for item in cls.pattern.findall(s)]

    @classmethod
    def new(
            cls,
            name: str,
            pattern: str | re.Pattern,
            crossref_directive: str | None = None,
            autodoc_directive: str | None = None
    ) -> Type[ParseKind]:
        """Shorthand for class syntax.

        Args:
             name:
                the class name to use
             pattern:
                a regex string or re.Pattern to search with
             autodoc_directive:
                use this instead of autogenerating in the form of
                f"auto{name.lower()}" to enter into the table.
        """
        return cast(Type[ParseKind], type(
            name.capitalize(), cls.__mro__,
            {k:v for k, v in cls.__dict__.items() if not k.startswith('_')},
            pattern=pattern,
            crossref_directive=crossref_directive,
            autodoc_directive=autodoc_directive))
