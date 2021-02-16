import numpy as np
import pyccl as ccl
import camb

''' Actually, what I probably need is a function that takes a CAMB instance, 
calculates the PK, chi and D, and passes it to CCL
'''

class CCL_CAMB_Wrapper: 
    def __init__(self, pars={}):
        if 'H0' not in pars:
            pars['H0'] = 67.5
        if 'ombh2' not in pars:
            pars['ombh2'] = 0.022
        if 'omch2' not in pars:
            pars['omch2'] = 0.122
        if 'tau' not in pars:
            pars['tau'] = 0.06
        if 'As' not in pars:
            pars['As'] = 2e-9
        if 'ns' not in pars:
            pars['ns'] = 0.965
        if 'mnu' not in pars:
            pars['mnu'] = 0.06

        pars['h'] = pars['H0']/100.
        pars['omegab'] = pars['ombh2']/(pars['h']**2.)
        pars['omegac'] = pars['omch2']/(pars['h']**2.)
        
        self.pars = pars
    
    def start_camb(self): 
        zmax = 4
        kmax = 10.

        self.cambpars = camb.CAMBparams()
        self.cambpars.set_cosmology(H0=self.pars['H0'], ombh2=self.pars['ombh2'], 
                        omch2=self.pars['omch2'], tau=self.pars['tau'], 
                        mnu=self.pars['mnu'])
        self.cambpars.InitPower.set_params(ns=self.pars['ns'], 
                                        As=self.pars['As'])
    
    def get_camb_pk(self, zmax=1200., kmin = 1e-4, kmax=10., numz = 50, numk = 200, 
                    nonlinear = True):
        try:
            self.cambparams
        except:
            print('Starting CAMB')
            self.start_camb()

        logz = np.linspace(-1, np.log10(zmax), numz)
        self.z = 10**logz
        self.z[0] = 0


        self.cambpars.set_matter_power(redshifts=self.z, kmax=kmax)
        if nonlinear:
            self.cambpars.NonLinear = camb.model.NonLinear_both
        else:
            self.cambpars.NonLinear = camb.model.NonLinear_none

        self.results = camb.get_results(self.cambpars)
        kh, _, pk = self.results.get_matter_power_spectrum(
                                                    minkh=kmin/self.pars['h'], 
                                                    maxkh=kmax/self.pars['h'], 
                                                    npoints = numk)

        self.k = kh*self.pars['h']
        self.pk = pk/self.pars['h']**3.
        #PK = camb.get_matter_power_interpolator(pars, nonlinear=True, 
            #hubble_units=False,k_hunit=False, kmax=kmax,
            #var1=camb.model.Transfer_nonu,var2=camb.model.Transfer_nonu, 
                                                #zmax=zmax)        

    def get_camb_background(self, zmax=1200., numz = 50):
        try:
            self.z
        except:
            print('z array has not been defined, using z_max = ', zmax)
            self.z = np.linspace(0,zmax, numz)

        try: 
            self.results
        except:
            self.results = camb.get_results(self.cambpars)
        
        self.chi = self.results.comoving_radial_distance(self.z)
        self.hubble = self.results.hubble_parameter(self.z)

    def start_ccl(self):
        try: 
            self.pk
        except:
            print('Calculating CAMB power spectrum (with default values)')
            self.get_camb_pk()
        
        try:
            self.chi, self.hubble
        except:
            print('Calculating CAMB background')
            self.get_camb_background()


        # CCL uses an array of a, not z, so need to flip everything
        aarr = 1. / (1. + self.z)
        aarr = np.sort(aarr)
        pk = np.flip(self.pk, axis=0)
        chi = np.flip(self.chi)
        h = self.hubble/self.hubble[0]
        h = np.flip(h)

        self.cosmo_ccl = ccl.CosmologyCalculator(
            Omega_b=self.pars['omegab'],
            Omega_c=self.pars['omegac'],
            h=self.pars['h'],
            n_s=self.pars['ns'],
            A_s=self.pars['As'],
            m_nu=self.pars['mnu'],
            background={'a': aarr,
                       'chi': chi,
                       'h_over_h0': h},
            pk_nonlin={'a': aarr,
                       'k': self.k,
                       'delta_matter:delta_matter': pk}
        )