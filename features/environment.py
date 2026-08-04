"""What behave needs to know before it runs anything.

The board's button runs one feature file from wherever the board happens to be, so the
repository root goes on the path here rather than being assumed to be the working
directory.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def before_all(context):
    """Say once why the suite cannot run, instead of sixty times.

    A checkout whose packages will not import reports every scenario as broken and none
    of them as the reason. Importing them here turns that into one error with a
    traceback in it.
    """
    import fieldnote          # noqa: F401
    import harbor            # noqa: F401
    import ledgerline        # noqa: F401
