import numpy as np
import pyccl as ccl
from cobaya.likelihood import Likelihood
from ccl_cobaya.ccl_camb_wrapper import CCL_CAMB_Wrapper
import os

os.environ['KMP_DUPLICATE_LIB_OK']='True'

class CCL_Likelihood(Likelihood):

    def initialize(self):
        self.ell = np.load(self.ell_file)
        self.cls = np.load(self.cls_file)
        self.dcls = np.load(self.dcls_file)

        self.wrapper = CCL_CAMB_Wrapper()

    def get_requirements(self):
        # Create array of redshifts for interpolation
        logz = np.linspace(-1, 3.1, 50)
        zarr = 10**logz
        zarr[0] = 0

        return {
            "Pk_grid": {
                "z": zarr, "k_max": 10., "nonlinear": True,
                "vars_pairs": ([("delta_tot", "delta_tot")])},
            "comoving_radial_distance": {"z": zarr},
            "Hubble": {"z": zarr},
            #"H0": None,
        }

    def logp(self, **params_values):
        kh, z, PK = self.provider.get_Pk_grid(("delta_tot", "delta_tot"), nonlinear=True)
        self.wrapper.chi = self.provider.get_comoving_radial_distance(z)
        self.wrapper.hubble = self.provider.get_Hubble(z)
        H0 = self.wrapper.hubble[0]
        h = H0/100.
        self.wrapper.z = z
        self.wrapper.k = kh*h
        self.wrapper.pk = PK/h**3.
        self.wrapper.start_ccl()

        lens = ccl.CMBLensingTracer(self.wrapper.cosmo_ccl, z_source=1100.)
        cls_theory = ccl.angular_cl(self.wrapper.cosmo_ccl, lens, lens, self.ell)#, p_of_k_a=pk2d)

        chi2 = (self.cls - cls_theory) ** 2. / self.dcls ** 2.

        return -0.5 * np.sum(chi2)
