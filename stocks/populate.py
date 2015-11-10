import logging
import imp
import tempfile
import atexit
import os

logger = logging.getLogger(__name__)


def populate_index(index, outfile=None, count=None):
    """
    Import the necessary populator.  Remove the outfile
    at program exit if it's not passed.
    """

    if not outfile:
        f = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        outfile = f.name
        f.close()
        atexit.register(os.unlink, outfile)

    populator_name = "populator_%s" % index

    try:
        mod_details = imp.find_module(populator_name, ["stocks/populators"])
        module = imp.load_module(populator_name, *mod_details)
    except ImportError as e:
        logger.error("Could not import module '%s'" % populator_name)
        raise

    if count:
        populator = module.IndexPopulator(outfile, count)
    else:
        populator = module.IndexPopulator(outfile)

    populator.run()
    return outfile
