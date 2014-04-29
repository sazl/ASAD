from ctypes import *
import numpy as np
import numpy.ctypeslib as npct

#===============================================================================

libstark = cdll.LoadLibrary("../C/libstark.so")

c_size_t_p   = POINTER(c_size_t)
c_double_p   = POINTER(c_double)
c_double_p_p = POINTER(c_double_p)

vector_s = npct.ndpointer(dtype=np.int, ndim=1, flags='C_CONTIGUOUS')
vector_d = npct.ndpointer(dtype=np.double, ndim=1, flags='C_CONTIGUOUS')
matrix_d = npct.ndpointer(dtype=np.double, ndim=2)

#===============================================================================

chi_squared_freq_test = libstark.stark_chi_squared_freq_test
chi_squared_freq_test.argtypes = [vector_d, c_size_t, vector_d, c_size_t]
chi_squared_freq_test.restype = c_double

ks_2_sample_freq_test = libstark.stark_ks_2_sample_freq_test
ks_2_sample_freq_test.argtypes = [vector_d, c_size_t, vector_d, c_size_t]
ks_2_sample_freq_test.restype = c_double

wavelength_interpolate_step = libstark.stark_wavelength_interpolate_step
wavelength_interpolate_step.argtypes = [vector_d, c_size_t,
                                        c_double, c_double,
                                        c_size_t_p]
wavelength_interpolate_step.restype = c_double_p

flux_interpolate_step = libstark.stark_flux_interpolate_step
flux_interpolate_step.argtypes = [matrix_d,
                                  c_size_t, c_size_t,
                                  c_double, c_double,
                                  c_size_t_p, c_size_t_p]
flux_interpolate_step.restype = c_double_p_p

#===============================================================================

StatTestNames= [
    'ChiSquaredFreq',
    'KsFreq',
    'Ks',
    'Cramer',
    'ShapiroWilk',
    'Akaike',
    'HosmerLemeshow'
]

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

StatTestType = enum(*StatTestNames)

#===============================================================================

class C_StarkBase(Structure):
    _fields_ = [
        ("num",                 c_size_t),
        ("num_wl",              c_size_t),
        ("min_wavelength",      c_double),
        ("max_wavelength",      c_double),
        ("wavelength",          c_double_p),
        ("flux",                c_double_p_p)
    ]

c_StarkBase_p = POINTER(C_StarkBase)

#-------------------------------------------------------------------------------

base_new = libstark.stark_base_new
base_new.argtypes = []
base_new.restype = c_StarkBase_p

base_free = libstark.stark_base_free
base_free.argtypes = [c_StarkBase_p]
base_free.restype = None

base_read_path = libstark.stark_base_read_from_path
base_read_path.argtypes = [c_StarkBase_p, c_char_p]
base_read_path.restype = None

base_normalize = libstark.stark_base_normalize
base_normalize.argtypes = [c_StarkBase_p, c_double]
base_normalize.restype = c_StarkBase_p

#===============================================================================

class C_StarkModel(Structure):
    _fields_ = [
        ("interpolation", c_double),
        ("step",          c_double),
        ("age_start",     c_double),
        ("age_factor",    c_double),
        ("base",          c_StarkBase_p)
    ]

c_StarkModel_p = POINTER(C_StarkModel)

#-------------------------------------------------------------------------------

model_new = libstark.stark_model_new
model_new.argtypes = []
model_new.restype = c_StarkModel_p

model_free_no_base = libstark.stark_model_free_
model_free_no_base.argtypes = [c_StarkModel_p]
model_free_no_base.restype = None

model_free = libstark.stark_model_free
model_free.argtypes = [c_StarkModel_p]
model_free.restype = None

model_read_path = libstark.stark_model_read_from_path
model_read_path.argtypes = [c_StarkModel_p, c_char_p]
model_read_path.restype = c_int

model_smoothen = libstark.stark_model_smoothen
model_smoothen.argtypes = [c_StarkModel_p, c_double, c_double]
model_smoothen.restype = c_StarkModel_p

model_normalize = libstark.stark_model_normalize
model_normalize.argtypes = [c_StarkModel_p, c_double]
model_normalize.restype = c_StarkModel_p

#===============================================================================

class C_StarkObservation(Structure):
    _fields_ = [
        ("reddening_start",  c_double),
        ("reddening_factor", c_double),
        ("base",             c_StarkBase_p)
    ]

c_StarkObservation_p = POINTER(C_StarkObservation)

#-------------------------------------------------------------------------------

observation_new = libstark.stark_observation_new
observation_new.argtypes = []
observation_new.restype = c_StarkObservation_p

observation_free_no_base = libstark.stark_observation_free_
observation_free_no_base.argtypes = [c_StarkObservation_p]
observation_free_no_base.restype = None

observation_free = libstark.stark_observation_free
observation_free.argtypes = [c_StarkObservation_p]
observation_free.restype = None

observation_read_path = libstark.stark_observation_read_from_path
observation_read_path.argtypes = [c_StarkObservation_p, c_char_p]
observation_read_path.restype = None

observation_reddening_shift = libstark.stark_observation_reddening_shift
observation_reddening_shift.argtypes = [c_StarkObservation_p, c_double, c_double]
observation_reddening_shift.restype = c_StarkObservation_p

observation_normalize = libstark.stark_observation_normalize
observation_normalize.argtypes = [c_StarkObservation_p, c_double]
observation_normalize.restype = c_StarkObservation_p

#===============================================================================

class C_StarkObject(Structure):
    _fields_ = [
        ("precision",           c_size_t),
        ("min_obsv",            c_size_t),
        ("min_model",           c_size_t),
        ("min_stat",            c_double),
        ("min_reddening",       c_double),
        ("min_age",             c_double),
        ("num_obsv",            c_size_t),
        ("num_model",           c_size_t),
        ("chosen_model",        c_size_t_p),
        ("stat",                c_double_p_p),
        ("observation",         c_StarkObservation_p),
        ("model",               c_StarkModel_p),
        ("stat_test_function",  CFUNCTYPE(c_double_p,
                                          c_double_p, c_size_t,
                                          c_double_p, c_size_t))
    ]

c_StarkObject_p = POINTER(C_StarkObject)

#-------------------------------------------------------------------------------

object_new = libstark.stark_object_new
object_new.argtypes = [c_int]
object_new.restype = c_StarkObject_p

object_free_no_obsv_model = libstark.stark_object_free_
object_free_no_obsv_model.argtypes = [c_StarkObject_p]
object_free_no_obsv_model.restype = None

object_free = libstark.stark_object_free
object_free.argtypes = [c_StarkObject_p]
object_free.restype = None

object_read_path = libstark.stark_object_read_from_path
object_read_path.argtypes = [c_StarkObject_p, c_char_p, c_size_t]
object_read_path.restype = None

object_from_obsv_model = libstark.stark_object_from_obsv_model
object_from_obsv_model.argtypes = [c_int, c_StarkObservation_p, c_StarkModel_p]
object_from_obsv_model.restype = c_StarkObject_p

#-------------------------------------------------------------------------------

object_normalize = libstark.stark_object_normalize
object_normalize.argtypes = [c_StarkObject_p, c_double]
object_normalize.restype = c_StarkObject_p

object_calculate_stat = libstark.stark_object_calculate_stat
object_calculate_stat.argtypes = [c_StarkObject_p]
object_calculate_stat.restype = None

object_calculate_chosen_model = libstark.stark_object_calculate_chosen_model
object_calculate_chosen_model.argtypes = [c_StarkObject_p]
object_calculate_chosen_model.restype = None

object_calculate_factors = libstark.stark_object_calculate_factors
object_calculate_factors.argtypes = [c_StarkObject_p]
object_calculate_factors.restype = None

################################################################################
