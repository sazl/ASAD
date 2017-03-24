from __future__ import print_function
import copy, io, math, os, os.path, uuid
import numpy as np
from pprint import pprint
from functools import reduce

#===============================================================================

class Math(object):

    @staticmethod
    def wavelength_interpolate_step(xs, interp=3, step=0.3):
        if interp == step:
            return xs

        sample_step = interp / step
        nsample     = int(2*sample_step - 1)
        result_num  = int((len(xs)/sample_step) - 1)
        result      = np.zeros([result_num])

        for i in range(result_num):
            tot = 0
            for k in range(nsample):
                tot += xs[i*sample_step + k]
            result[i] = tot / nsample

        return result

    @staticmethod
    def wavelength_interpolate_step_obsv(xs, interp=3, step=0.3):
        if interp == step:
            return xs

        sample_step = interp / step
        nsample     = int(2*sample_step - 1)
        result_num  = int((len(xs)/sample_step) - 3)
        result      = np.zeros([result_num])
        xs2         = xs[1:]

        for i in range(result_num):
            tot = 0
            for k in range(nsample):
                tot += xs2[i*sample_step + k]
            result[i] = tot / nsample

        return np.append(np.array([xs[0]]), result)

    @staticmethod
    def flux_interpolate_step(xss, interp, step):
        if interp == step:
            return xss

        sample_step  = interp / step
        nsample      = int(2*sample_step - 1)
        result_nrows = xss.shape[0]
        result_ncols = int((xss.shape[1] / sample_step) - 1)
        result       = np.zeros([result_nrows, result_ncols])

        for i in range(result_nrows):
            row = xss[i]
            for j in range(result_ncols):
                tot = 0
                num = j * sample_step
                sample = row[num:num+nsample]
                for k in range(nsample):
                    tot += sample[k]
                result[i, j] = tot / nsample

        return result

    @staticmethod
    def flux_interpolate_step_obsv(xss, interp, step):
        if interp == step:
            return xss

        sample_step     = interp / step
        nsample         = int(2*sample_step - 1)
        result_ncols    = int((xss.shape[1] / sample_step) - 3)
        result          = np.zeros([result_ncols])
        row             = xss[0]
        first, row_rest = row[0], row[1:]

        for i in range(result_ncols):
            tot = 0
            num = i * sample_step
            sample = row_rest[num:num+nsample]
            for k in range(nsample):
                tot += sample[k]
            result[i] = tot / nsample

        result = np.append(np.array([first]), result)
        return np.array([result])

#===============================================================================

class Statistics(object):

    STAT_TEST_NAMES = ['chi-squared', 'ks']

    @staticmethod
    def ks_2_sample_freq_test(xs, ys):
        csx = np.cumsum(xs)
        csy = np.cumsum(ys)
        cpx = csx / float(csx[-1])
        cpy = csy / float(csy[-1])
        return np.max(np.abs(cpx - cpy))

    @staticmethod
    def chi_squared_freq_test(xs, ys):
        return np.sum((xs - ys) ** 2)

#===============================================================================

class Base(object):

    def __init__(self, path=None, name=None):
        self._name            = name
        self._original_name   = name
        self._wavelength_step = 0
        self._wavelength      = np.array([])
        self._flux            = np.array([])
        self._var             = None
        self._var_start       = 0
        self._var_step        = 0
        if path:
            self.read_from_path(path)

    def format(self, header=''):
        out = io.StringIO()
        for i in range(self.num_wl):
            out.write(unicode(self.wavelength[i]))
            for j in range(self.num):
                out.write(unicode(' {:10.6g}'.format(self.flux[j][i])))
            out.write(u'\n')
        out.flush()
        header = '# ' + header
        return '\n'.join([header, out.getvalue()])

    def read_from_path(self, path, *args, **kwargs):
        mat = np.array(np.loadtxt(path).transpose())
        basename = os.path.basename(path)
        (name, ext) = os.path.splitext(basename)
        self.name = basename
        self.original_name = basename
        self.wavelength = mat[0]
        self.wavelength_step = self.wavelength[1] - self.wavelength[0]
        self.flux = mat[1:]

    def normalize(self, wavelength):
        result = copy.deepcopy(self)
        index = result.wavelength.searchsorted(wavelength)
        flux = result.flux.transpose()
        if index >= result.num_wl:
            return result
        flux[0:index] /= flux[index]
        flux[index+1:] /= flux[index]
        flux[index] = [1]
        result.name = self.name
        return result

    def normalize_average(self):    #Dividing the fluxes with their average.
        result = copy.deepcopy(self)
        flux = result.flux.transpose()
        averageFlux = reduce(lambda x,y: x + y, flux[:]) / len(flux)
        flux[:] /= averageFlux
        result.name = self.name
        return result
        

    def wavelength_str(self, start=None, end=None):
        wl = self.wavelength[start:end]
        if len(wl) <= 10:
            return str(wl)
        else:
            return "[{}, {}, {}, ..., {}]".format(wl[0], wl[1], wl[2], wl[-1])

    def wavelength_index(self, start, end):
        if start > end:
            raise(IndexError("start = {} is greater than end = {}".format(
                start, end)))

        if start < self.wavelength[0]:
            raise(IndexError("minimum allowed = {}, given = {}".format(
                self.wavelength[0], start)))
        else:
            index_start = np.searchsorted(self.wavelength, start)
        if end > self.wavelength[-1]:
            raise(IndexError("maximum allowed = {}, given = {}".format(
                self.wavelength[-1], end)))
        else:
            index_end = np.searchsorted(self.wavelength, end)

        return (index_start, index_end)

    def wavelength_range(self, start, end):
        (index_start, index_end) = self.wavelength_index(start, end)
        return self.wavelength[index_start:index_end]

    def flux_range(self, start, end):
        (index_start, index_end) = self.wavelength_index(start, end)
        return self.flux[:, index_start:index_end]

    def wavelength_set_index(self, start, end):
        result = copy.deepcopy(self)
        result.wavelength = self.wavelength[start:end]
        result.flux = self.flux[:, start:end]
        return result

    def wavelength_set_start(self, start):
        index_start = np.searchsorted(self.wavelength, start)
        return self.wavelength_set_index(index_start, None)

    def wavelength_set_end(self, end):
        index_end = np.searchsorted(self.wavelength, end)
        return self.wavelength_set_index(0, index_end+1)

    def restrict_wavelength_start(self, wavelength):
        index = np.searchsorted(self.wavelength, wavelength)
        self.wavelength = self.wavelength[index:]
        self.flux = self.flux[:, index:]

    def restrict_wavelength_start_by_interpolation_step(self, interp, wavelength):
        step = interp / self.wavelength_step
        wl = self.wavelength[step:]
        wl_indices = np.where(np.isclose((wavelength - wl) % interp, 0.0))[0]
        wl_start_index = wl_indices[0]
        wl_start = self.wavelength[wl_start_index + 1]
        self.restrict_wavelength_start(wl_start)
        return wl_start

    def wavelength_set_range(self, start, end):
        (index_start, index_end) = self.wavelength_index(start, end)
        return self.wavelength_set_index(index_start, index_end+1)

    def smoothen(self, interp, name='', step=0):
        if step <= 0:
            step = self.wavelength_step
        result = copy.deepcopy(self)
        result.name = name
        result.wavelength = Math.wavelength_interpolate_step(
            self.wavelength, interp, step)
        result.flux = Math.flux_interpolate_step(self.flux, interp, step)
        return result

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        self._name = name

    @property
    def original_name(self):
        return self._original_name
    @original_name.setter
    def original_name(self, original_name):
        self._original_name = original_name

    @property
    def wavelength_step(self):
        return self.wavelength[1] - self.wavelength[0]
    @wavelength_step.setter
    def wavelength_step(self, wavelength_step):
        self._wavelength_step = wavelength_step

    @property
    def num(self):
        return self.flux.shape[0]

    @property
    def num_wl(self):
        return self.wavelength.shape[0]

    @property
    def wavelength(self):
        return self._wavelength
    @wavelength.setter
    def wavelength(self, wavelength):
        self._wavelength = wavelength

    @property
    def flux(self):
        return self._flux
    @flux.setter
    def flux(self, flux):
        self._flux = flux

    @property
    def var_start(self):
        return self._var_start
    @var_start.setter
    def var_start(self, var_start):
        self._var_start = var_start

    @property
    def var_step(self):
        return self._var_step
    @var_step.setter
    def var_step(self, var_step):
        self._var_step = var_step

    @property
    def var(self):
        if not self._var is None:
            return self._var
        else:
            return np.arange(self.var_start,
                             self.var_start + (self.var_step * self.num),
                             self.var_step)[:self.num]
    @var.setter
    def var(self, var):
        self._var = var

#===============================================================================

class Model(Base):

    PADOVA_WL_START     = 3322
    PADOVA_WL_END       = 9300
    PADOVA_ROUND_DIGITS = 2
    PADOVA_AGE_START    = 6.2
    PADOVA_AGE_END      = 10.10
    MODEL_FORMATS       = ['DELGADO', 'GALAXEV', 'MILES', 'INTERMEDIATE']

    def __init__(self,
                 age_start=6.6,
                 age_step=0.05,
                 path=None,
                 format=None,
                 *args, **kwargs):
        super(Model, self).__init__(path=None, *args, **kwargs)
        self.age_start = age_start
        self.age_step = age_step
        if not path is None:
            self.read_from_path(path, format=format)

    def format(self):
        ages_str = ', '.join(map(str, self.age))
        return super(Model, self).format(header=ages_str)

    def read_from_path(self, path, format='DELGADO'):
        if format == 'DELGADO':
            self.read_del_gado_model(path)
        elif format == 'GALAXEV':
            self.read_galaxev_model(path)
        elif format == 'MILES':
            self.read_miles_model(path)
        elif format == 'INTERMEDIATE':
            self.read_intermediate_model(path)
        else:
            super(Model, self).read_from_path(path)

    def read_intermediate_model(self, path):
        from StringIO import StringIO
        with open(path) as f:
            try:
              header = f.readline()
              age = map(float, header.strip('# ').split(','))
              self.age = age
              self.age_start = self.age[0]
              self.age_step = self.age[1] - self.age[0]
            except:
              raise ValueError('Model has no age header specified')
        super(Model, self).read_from_path(path)

    def read_del_gado_model(self, path):
        super(Model, self).read_from_path(path)
        model_indices = np.arange(0, 220, 3)
        self.flux = self.flux[model_indices]
        self.age = np.arange(self.age_start,
            self.age_start + self.age_step*self.num)

    def read_galaxev_model(self, path):
        f = open(path, 'r')
        read_float_line = lambda: map(float, f.readline().split())
        spectra_hd = read_float_line()
        num_spectra, spectra = int(spectra_hd[0]), [spectra_hd[1:]]
        num_spectra_left = num_spectra - len(spectra[0])

        while num_spectra_left > 0:
            spectra_line = read_float_line()
            spectra.append(spectra_line)
            num_spectra_left -= len(spectra_line)

        for i in range(6):
            f.readline()

        wl_hd = read_float_line()
        num_wl, wavelength = int(wl_hd[0]), wl_hd[1:]
        num_wl_left = num_wl - len(wavelength)

        while num_wl_left > 0:
            wl_line = read_float_line()
            wavelength += wl_line
            num_wl_left -= len(wl_line)

        total_flux = []
        contents = iter(f.read().split())
        for i in range(num_spectra):
            flux = []
            num_flux = int(next(contents))
            for j in range(num_flux):
                flux.append(float(next(contents)))

            num_skip = int(next(contents))
            for k in range(num_skip):
                next(contents)
            total_flux.append(flux)

        f.close()
        basename = os.path.basename(path)
        (name, ext) = os.path.splitext(basename)
        self.name = basename
        self.original_name = basename
        self.wavelength = np.array(wavelength)

        # Skip Age Zero
        spectra = reduce(lambda x,y: x+y, spectra)[1:]
        age = map(lambda x: round(math.log10(x), Model.PADOVA_ROUND_DIGITS), spectra)
        age_start_index = np.searchsorted(age, Model.PADOVA_AGE_START)
        age_end_index = np.searchsorted(age, Model.PADOVA_AGE_END)+1
        if len(age) > 1:
            age_step = age[1] - age[0]
        self.age = np.array(age[age_start_index:age_end_index])
        self.age_start = age[0]
        self.age_step = age_step

        # Skip Age Zero
        total_flux = total_flux[1:]
        self.flux = np.array(total_flux[age_start_index:age_end_index])
        result = self.wavelength_set_range(
            Model.PADOVA_WL_START, Model.PADOVA_WL_END)
        self.wavelength = result.wavelength
        self.wavelength_step = result.wavelength_step
        self.flux = result.flux

    def read_miles_model(self, path):
        super(Model, self).read_from_path(path)
        with open(path) as f:
            try:
                header = f.readline().lstrip('#')
                self.age = np.array([float(x) for x in line.split(',')])

                # Not sure why we rounded here before
                # self.age = np.round(self.age, Model.PADOVA_ROUND_DIGITS)
            except:
                self.age = np.linspace(
                    Model.PADOVA_AGE_START,
                    Model.PADOVA_AGE_END,
                    num=self.num
                )
            self.age_start = self.age[0]
            if len(self.age) > 1:
                self.age_step = self.age[1] - self.age[0]

    @property
    def age_start(self):
        return self.var_start
    @age_start.setter
    def age_start(self, age_start):
        self.var_start = age_start

    @property
    def age_step(self):
        return self.var_step
    @age_step.setter
    def age_step(self, age_step):
        self.var_step = age_step

    @property
    def age(self):
        return self.var
    @age.setter
    def age(self, age):
        self.var = age

#===============================================================================

class Observation(Base):

    def __init__(self,
                 reddening_start = 0,
                 reddening_step = 0.01,
                 *args, **kwargs):
        super(Observation, self).__init__(*args, **kwargs)
        self.reddening_start = reddening_start
        self.reddening_step = reddening_step

    def wl_scale(self, wavelength):
        WL_SCALE = 1e-4
        WL_EXPT  = -1
        WL_ADD   = -1.82
        b = wavelength * WL_SCALE
        a = (b ** WL_EXPT) + WL_ADD
        return a

    def calculate_A(self):
        return np.array([self.wl_scale(w) for w in self.wavelength])

    def find_xyz(self):
        A = self.calculate_A()
        X = 1 + 0.17699*A - 0.50447*(A**2) - 0.02427*(A**3) + 0.72085*(A**4) + \
            0.01979*(A**5) - 0.77530*(A**6) + 0.32999*(A**7)
        Y = 1.41338*A + 2.28305*(A**2) + 1.07233*(A**3) - 5.38434*(A**4) - \
            0.62251*(A**5) + 5.30260*(A**6) - 2.09002*(A**7)
        Z = X + (Y / 3.2)
        return np.array([X, Y, Z])

    def find_flux(self, start, end, step):
        flux_initial = self.flux[0]
        Z = self.find_xyz()[2]
        R = np.arange(start, end+step, step)
        flux = np.array([
            (10**(0.4*3.2*Z[i]*R)) * flux_initial[i] for i in range(len(Z))
        ])
        return flux.transpose()

    def find_single_flux(self, start):  #Single Reddening
        flux_initial = self.flux[0]
        Z = self.find_xyz()[2]
        R = start
        flux = np.array([
            (10**(0.4*3.2*Z[i]*R)) * flux_initial[i] for i in range(len(Z))
        ])
        return flux.transpose()

    def reddening_shift(self, start, end, step):
        result = copy.deepcopy(self)
        result.reddening_start = start
        result.reddening_step = step
        result.flux = self.find_flux(start, end, step)
        return result

    def single_reddening_shift(self, start):    #Single Reddening
        result = copy.deepcopy(self)
        result.reddening_start = start
        result.flux = self.find_single_flux(start)
        return result

    def smoothen(self, interp, name='', step=0):
        if step <= 0:
            step = self.wavelength_step
        result = copy.deepcopy(self)
        result.name = name
        result.wavelength = Math.wavelength_interpolate_step_obsv(
            self.wavelength, interp, step)
        result.flux = Math.flux_interpolate_step_obsv(self.flux, interp, step)
        return result

    @property
    def reddening_start(self):
        return self.var_start
    @reddening_start.setter
    def reddening_start(self, red_start):
        self.var_start = red_start

    @property
    def reddening_step(self):
        return self.var_step
    @reddening_step.setter
    def reddening_step(self, reddening_step):
        self.var_step = reddening_step

    @property
    def reddening(self):
        return self.var
    @reddening.setter
    def reddening(self, reddening):
        self.var = reddening

#===============================================================================

class Asad(object):

    ROUND_DIGITS = 2

    @staticmethod
    def from_observation_model(observation, model):
        obj = Asad()
        obj.name = observation.name + '_' + model.name
        obj.observation = observation
        obj.model = model
        return obj

    def __init__(self,
                 name      = None,
                 stat_test = Statistics.chi_squared_freq_test,
                 path      = None,
                 read      = True,
                 calculate = False):
        self._name            = name
        self._observation     = Observation()
        self._model           = Model()
        self._stat_test       = stat_test
        self._path            = path
        self._min_stat        = 0
        self._min_observation = 0
        self._min_model       = 0

        if self.path:
            if name is None:
                self.name = os.path.basename(self.path)
            if read:
                self.read_from_path(os.path.abspath(self.path))
                if calculate:
                    self.calculate_chosen_model()

    def read_from_path(self, path, num_observation=51):
        mat = np.array(np.loadtxt(path).transpose())
        self.observation            = Observation()
        self.observation.wavelength = mat[0]
        self.observation.flux       = mat[1:num_observation+1]
        self.model                  = Model()
        self.model.wavelength       = mat[num_observation+1]
        self.model.flux             = mat[num_observation+2:]

    def format(self):
        obsv_fmt = self.observation.format().split('\n')
        model_fmt = self.model.format().split('\n')
        obj_fmt = [x + (' '*10) + y for (x,y) in zip(obsv_fmt,model_fmt)]
        fmt_str = '\n'.join(obj_fmt)
        return unicode(fmt_str)

    def format_chosen(self):
        fmt = '{:<80} {:>8.6f} {:>10f}\nTest Statistic Value = {}\n'.format(
            self.name,
            self.min_age,
            self.min_reddening,
            self.min_stat
        )
        return unicode(fmt)

    def normalize(self, wavelength):
        result = copy.deepcopy(self)
        result.observation = result.observation.normalize(wavelength)
        result.model = result.model.normalize(wavelength)
        return result

    def calculate_stat(self):
        self.stat = np.zeros([self.num_observation, self.num_model])
        for i in range(self.num_observation):
            for j in range(self.num_model):
                self.stat[i,j] = self.stat_test(
                    self.observation.flux[i], self.model.flux[j])
        return self.stat

    def calculate_chosen_model(self):
        self.calculate_stat()
        self.min_observation = np.argmin(np.min(self.stat, axis=1))
        self.min_model = np.argmin(self.stat[self.min_observation])
        self.chosen_model = np.argmin(self.stat, axis=1)
        self.min_stat = self.stat[self.min_observation, self.min_model]
        return self.chosen_model

    def calculate_stat_delta_level(self, delta=1.0):
        error = (np.abs(self.stat - self.min_stat) < delta)
        reddening_index = np.where([np.any(e) for e in error])[0]
        age_index = np.concatenate(np.array(
            [np.where(e)[0] for e in error]).flatten())
        self.error_reddening = self.observation.reddening[reddening_index]
        self.error_age = np.array([self.model.age[i] for i in age_index])
        self.error_stat = np.array(
            [self.stat[ri, ai] for ri, ai in zip(reddening_index, age_index)])

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        self._name = name

    @property
    def observation(self):
        return self._observation
    @observation.setter
    def observation(self, observation):
        self._observation = observation

    @property
    def model(self):
        return self._model
    @model.setter
    def model(self, model):
        self._model = model

    @property
    def stat_test(self):
        return self._stat_test
    @stat_test.setter
    def stat_test(self, stat_test):
        self._stat_test = stat_test

    @property
    def path(self):
        return self._path
    @path.setter
    def path(self, path):
        self._path = path

    @property
    def num_observation(self):
        return self.observation.num

    @property
    def num_model(self):
        return self.model.num

    @property
    def min_stat(self):
        return self._min_stat
    @min_stat.setter
    def min_stat(self, min_stat):
        self._min_stat = min_stat

    @property
    def min_observation(self):
        return self._min_observation
    @min_observation.setter
    def min_observation(self, min_observation):
        self._min_observation = min_observation

    @property
    def min_model(self):
        return self._min_model
    @min_model.setter
    def min_model(self, min_model):
        self._min_model = min_model

    @property
    def min_reddening(self):
        return self.observation.reddening[self.min_observation]

    @property
    def min_age(self):
        return self.model.age[self.min_model]

    @property
    def stat(self):
        return self._stat
    def stat(self, stat):
        self._stat = stat

    @property
    def chosen_model(self):
        return self._chosen_model
    @chosen_model.setter
    def chosen_model(self, chosen_model):
        self._chosen_model = chosen_model

    @property
    def error(self):
        return self._error
    @error.setter
    def error(self, value):
        self._error = value


#===============================================================================
