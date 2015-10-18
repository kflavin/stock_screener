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
    mod_details = imp.find_module(populator_name, ["stocks/populators"])
    module = imp.load_module(populator_name, *mod_details)

    if index == "sp500":
        populator = module.IndexPopulator(outfile)
    else:
        populator = module.IndexPopulator(outfile)
        logger.error("Do not recognize index '%s'" % index)
        return None

    populator.run()
