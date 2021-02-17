import numpy as np
import pyccl as ccl
from ccl_cobaya.ccl_camb_wrapper import *

wrapper = CCL_CAMB_Wrapper()
wrapper.get_camb_pk()
wrapper.get_camb_background()
wrapper.start_ccl()

#cosmo = ccl.Cosmology(
#    Omega_c=0.27, Omega_b=0.045, h=0.67, A_s=2.1e-9, n_s=0.965,
#    transfer_function='bbks')

lens1 = ccl.CMBLensingTracer(wrapper.cosmo_ccl, z_source=1100.)
ell = np.logspace(np.log10(2), np.log10(2000), 50, dtype=int)
ell = np.unique(ell)
cls = ccl.angular_cl(wrapper.cosmo_ccl, lens1, lens1, ell)
dcls = 0.1*cls

# Add some noise
noise = np.random.normal(loc=0.0, scale=0.1, size=len(ell))
#cls *= (1 + noise)

np.save("./ccl_cobaya/data/cls.npy", cls)
np.save("./ccl_cobaya/data/dcls.npy", dcls)
np.save("./ccl_cobaya/data/ell.npy", ell)
