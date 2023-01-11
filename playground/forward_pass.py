#!/usr/bin/env python3

from classy import Class
from functools import partial

#%%
LambdaCDM = Class()


@partial(partial, cosmo_class=LambdaCDM)
def forward(
    parameters: dict,
    *,
    cosmo_constants: dict = {
        "lensing": "yes",
        "P_k_max_1/Mpc": 3.0
    },
    cl_constants: dict = {"lmax": 2500},
    cosmo_class
) -> float:
    cosmo_class.empty()  # Reset parameters

    # Parameters of interest (LambdaCDM cosmology parameters)
    cosmo_class.set(parameters)

    # Specify the output parameters of CLASS which are used in the cost function
    ps_output = {'output': 'tCl,pCl,lCl,mPk'}
    cosmo_class.set(cosmo_constants | ps_output)

    # NOTE, please take all of the following with a huge grain of salt since I
    # am not deep into the weeds of CLASS.
    #
    # Do the actual work. In essence this call parses the above input and
    # invokes all required tasks to compute the final results (the final result
    # here being some cosmological power spectra). If you take a deeper look
    # into `python/classy.pyx::Class.compute` you'll notice a `level` keyword.
    # This keyword indicates the tasks that need to be performed in
    # `Class.compute`. However these tasks have dependencies, see
    # `LambdaCDM._check_task_dependency(["distortions"])` which eventually lead
    # to all tasks/`level`s in `Class.compute` being run.
    #
    # The reference tree of the invoked functions usually first lead to
    # `python/cclassy.pyd` before eventually ending up in some C code like
    # `source/distortions.c` or `source/perturbations.c` According to a friend
    # in Cosmology. The solver in C that does most of the work should be within
    # `source/perturbations.c` in particular the
    # `source/perturbations.c::perturbations_init` function is very expensive.
    #
    # Subsequently we only retrieve values via wrapper functions of
    # `python/classy.pyx::lensing_cl_at_l`.
    cosmo_class.compute()

    # Retrieve the results
    cls = cosmo_class.lensed_cl(cl_constants["lmax"])  # or `raw_cl`
    h = cosmo_class.h()
    # ll = cls['ell'][2:]
    clTT = cls['tt'][2:]
    # clEE = cls['ee'][2:]
    # clPP = cls['pp'][2:]

    # Placeholder for a real cost function which would munge the output of
    # `Class.lensed_cl` and `Class.h`
    return (clTT * h).sum()


# %%
# More details about the parameters can be found in
# `include/background.h::background`
parameters = {
    'omega_b': 0.0223828,
    'omega_cdm': 0.1201075,
    'h': 0.67810,
    'A_s': 2.100549e-09,
    'n_s': 0.9660499,
    'tau_reio': 0.05430842
}

forward(parameters)
