import ROOT
from AnalysisPython.PyRoot import *
from AnalysisPython.PyRoUts import *
from AnalysisPython.Utils import timing
from AnalysisPython.Utils import rooSilent
from AnalysisPython.Logger import getLogger

from cuts import h1
from cuts import m_Bu, nbin_Bu
from cuts import cuts_Bu, prntCuts

from model import model_Bu

from data_Bc import tSelection6 as tBu6

from Selectors import SBT


logger = getLogger(__name__)



# Fill control B+  histogram (takes some time)
with timing():
    tBu6.Project(h1.GetName(), 'DTFm_b', cuts_Bu)


# Fit Bc+ & B+ histogram (check the model)
with rooSilent():
    r, f = model_Bu.fitHisto(h1)


sel_Bu = SBT(m_Bu, cuts_Bu)


# Build RooFit dataset for B+ , it could take as long as 3-5 minutes
tBu6.process(sel_Bu)

ds_Bu = sel_Bu.dataset()
ds_Bu.Print('v')


with rooSilent():
    logger.info('Make unbinned fit for B+')

    model_Bu.s.setMax(1.2 * len(ds_Bu))
    ru, fu = model_Bu.fitTo(ds_Bu, draw=False, nbins=nbin_Bu)

    model_Bu.signal.sigma.release()
    model_Bu.signal.mean.release()

    ru, fu = model_Bu.fitTo(ds_Bu, draw=True, nbins=nbin_Bu)

# print 'FIT#2 results for B+  ', ru(model_Bu.s_name)[0]
# print 'FIT#2 precision:', ru("SBu")[0].prec()


logger.info('running sPlot')
model_Bu.sPlot(ds_Bu)

def count_significance():
    global ds_Bu, nbin_Bu, model_Bu
    from math import sqrt

    vals = [
        model_Bu.s,
        model_Bu.s2,
        model_Bu.s3,
        model_Bu.b,
        model_Bu.background.tau,
        model_Bu.signal.aL,
        model_Bu.signal.aR,
        model_Bu.signal.nL,
        model_Bu.signal.nR,
        model_Bu.signal.mean,
        model_Bu.signal.sigma
    ]

    for x in vals:
        x.fix(x.getVal())

    ru, fu = model_Bu.fitTo(ds_Bu, draw=False, nbins=nbin_Bu)
    Lfixed = ru.minNll()

    model_Bu.s.fix(0)

    ru, fu = model_Bu.fitTo(ds_Bu, draw=False, nbins=nbin_Bu)
    Ls0 = ru.minNll()
    return sqrt(2 * (Ls0 - Lfixed))


logger.info('=' * 20)
logger.info("Selection 6\n\n")
logger.info(ru)

logger.info("Signficance6 is " + str(count_significance()))
logger.info('=' * 20)

