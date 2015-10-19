import logging
import imp

logger = logging.getLogger(__name__)


def populate_index(index, outfile=None):
    """
    Import the necessary populator
    """

    if not outfile:
        outfile = "%s.new.csv" % index

    populator_name = "populator_%s" % index

    try:
        mod_details = imp.find_module(populator_name, ["stocks/populators"])
        module = imp.load_module(populator_name, *mod_details)
    except ImportError as e:
        logger.error("Could not import module '%s'" % populator_name)
        return None

    populator = module.IndexPopulator(outfile)
    populator.run()
