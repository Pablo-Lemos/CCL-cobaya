import numpy as np
import pyccl as ccl

cosmo = ccl.Cosmology(
    Omega_c=0.27, Omega_b=0.045, h=0.67, A_s=2.1e-9, n_s=0.965,
    transfer_function='bbks')

lens1 = ccl.CMBLensingTracer(cosmo, z_source=1100.)
ell = np.logspace(np.log10(2), np.log10(2000), 50, dtype=int)
ell = np.unique(ell)
cls = ccl.angular_cl(cosmo, lens1, lens1, ell)
dcls = 0.1*cls

# Add some noise
noise = np.random.normal(loc=0.0, scale=0.1, size=len(ell))
cls *= (1 + noise)

np.save("./data/cls.npy", cls)
np.save("./data/dcls.npy", dcls)
np.save("./data/ell.npy", ell)
