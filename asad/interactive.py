from __future__ import print_function

import cmd
import contextlib
import io
import glob
import os
import re
import shlex
import sys

from StringIO import StringIO
from pprint import pprint
from colorama import Fore, Back, Style, init
init()

import pyasad
import plot
from config import GlobalConfig

#===============================================================================

def safe_input(s):
    return raw_input(s)

def safe_default_input(s, default=None):
    out = s + (" [%s]: " % default)
    arg = safe_input(out)
    return default if arg == '' else arg

def remove_quotes(text):
    return re.sub(r'^["\']|["\']$', '', text)

def split_args(arg):
    if os.name == 'nt':
        posix = False
    else:
        posix = True
    return shlex.split(arg, posix=posix)

def parse_args(arg, required=False, expected=0, type=unicode):
    args = [ type(remove_quotes(x)) for x in split_args(arg) ]
    if expected > len(args):
        raise ValueError("Expected {} args got {}".format(expected, len(args)))
    if required and expected != len(args):
        raise ValueError("Require {} args got {}".format(expected, len(args)))
    return args

def parse_tuple(arg, required=False, type=unicode, expected=0):
    args = arg.strip('()').split(',')
    args = tuple(type(arg) for arg in args if arg)
    if expected > len(args):
        raise ValueError("Expected {} args got {}".format(expected, len(args)))
    if required and expected != len(args):
        raise ValueError("Require {} args got {}".format(expected, len(args)))
    return args

def parse_tuple_int(arg, *args, **kwargs):
    return parse_tuple(arg, type=int, *args, **kwargs)

def parse_yn(arg, default=False):
    try:
        choice = parse_args(arg, required=True, expected=1)
        choice = choice[0].upper()[0]
        if choice == 'Y':
            return True
        elif choice == 'N':
            return False
        else:
            raise ValueError(
                'Unknown choice: %s Assuming: %s' % (choice, default))
    except Exception as err:
        error_print(unicode(err))
        return default

def parse_input_yn(question, default=False):
    yn = ['y', 'n']
    index = int(not default)
    yn[index] = yn[index].upper()
    marker = '? [%s/%s]: ' % tuple(yn)
    choice = safe_input(question + marker)
    return parse_yn(choice, default)

def color_print(text, color):
    print(color + text)
    print(Fore.RESET + Back.RESET + Style.RESET_ALL)

def error_print(text):
    color_print(text, Fore.RED)

def ok_print(text):
    color_print(text, Fore.GREEN)

def info_print(text):
    color_print(text, Fore.BLUE)

def list_files(directory, pattern=".*"):
    regex = re.compile(pattern)
    in_dir = os.path.abspath(directory)
    in_files = [
        os.path.join(in_dir, f)
        for f in os.listdir(in_dir)
        if re.match(regex, os.path.basename(f))
    ]
    return in_files

def base_command(type):
    def command(self, arg):
        try:
            args = parse_args(arg, expected=2)
            subcmd = args[0]
            args = args[1:]
            name = type.__name__
            name = name[len('do_'):] if name.startswith('do_') else name
            command = '_'.join([name, subcmd])
            cmd_arg = ' '.join(args)
            self.onecmd(command + ' ' + cmd_arg)
        except Exception as err:
            error_print(unicode(err))
    return command

#===============================================================================

class Shell(cmd.Cmd, object):

    def __init__(self, *args, **kwargs):
        self._values = list()
        cmd.Cmd.__init__(self, *args, **kwargs)

    def default(self, line):
        print("Unknown command " + line)

    @contextlib.contextmanager
    def mutate_values(self, index):
        temp = self.values
        if len(index) == 1:
            self.values = [self.values[index[0]]]
        elif len(index) == 2:
            self.values = list(self.values[index[0]:index[1]])

        yield

        if len(index) == 1:
            temp[index[0]] = self.values[0]
        elif len(index) == 2:
            temp[index[0]:index[1]] = self.values
        self.values = temp

    def do_index(self, arg):
        try:
            args = parse_args(arg, expected=2)
            index_arg = args[0]
            submcd = args[1:]
            index = parse_tuple(index_arg, type=int, expected=1)
            with self.mutate_values(index):
                self.onecmd(' '.join(subcmd))
        except Exception as err:
            error_print(unicode(err))

    @base_command
    def do_set(self, arg):
        pass

    @property
    def values(self):
        return self._values
    @values.setter
    def values(self, values):
        self._values = values

#===============================================================================

class Base_Shell(Shell):
    asad_type = pyasad.Base

    def do_help(self, arg):
        print('base [list | read | directory]')

    def do_list(self, arg):
        "List the current bases"
        if not self.values:
            print('Empty')
            return

        len_cols = (10, 20, 10, 10)
        ncols = len(len_cols)
        (col_str, sep_str) = ("{:^%d}|", "{:-^%d}+")
        fmt_col = '|' + (col_str * ncols) % len_cols
        sep = '+' + ((sep_str * ncols) % len_cols).format(*['']*ncols)

        print (sep)
        print(fmt_col.format('Index', 'Name', 'Num', 'Num_WL'))
        print(sep)
        for (i,m) in enumerate(self.values):
            print(fmt_col.format(i, m.name[:15], m.num, m.num_wl))
        print(sep)

    def do_read(self, arg):
        "Read from a file"
        try:
            path = os.path.abspath(parse_args(arg, expected=1)[0])
            base = self.asad_type(path=path)
            self.values.append(base)
            ok_print("Read OK: {}".format(path))
        except Exception as err:
            error_print("Failed to read file")
            error_print(unicode(err))
            raise err

    def do_directory(self, arg):
        "Read all the files in a directory"
        try:
            path = os.path.abspath(parse_args(arg, expected=1)[0])
            if not os.path.isdir(path):
                raise(RuntimeError('Must be a directory'))
            for f in list_files(path):
                obj = self.asad_type(path=f)
                self.values.append(obj)
                ok_print("Read OK: {}".format(f))
        except Exception as err:
            error_print('Directory read failed')
            error_print(unicode(err))
            raise err

    def do_read_file_directory(self, arg):
        "Read a file or a directory depending on the path"
        try:
            path = os.path.abspath(parse_args(arg, expected=1)[0])
            if os.path.isdir(path):
                self.do_directory(path)
            elif os.path.isfile(path):
                self.do_read(path)
            else:
                files = glob.glob(path)
                if not files:
                    raise ValueError('Invalid Path')
                for f in files:
                    obj = self.asad_type(path = f)
                    self.values.append(obj)
                    ok_print("Read OK: {}".format(f))
        except Exception as err:
            error_print('File or Directory Read Error')
            error_print(unicode(err))
            raise err

    def do_write(self, arg, prefix=''):
        "Write current bases to a directory"
        path = parse_args(arg, expected=1)[0]
        if not os.path.isdir(path):
            error_print('Must be a directory not a path: {}'.format(path))
            return

        for base in self.values:
            fpath = os.path.join(path, prefix + base.name)
            if os.path.exists(fpath):
                error_print('{} already exists, Skipping'.format(fpath))
                raise Exception('file already exists')
            else:
                print(base.format(), file=io.open(fpath, 'w'))
                ok_print('Wrote {} to path: {}'.format(base.name, fpath))

    def do_normalize(self, arg):
        "Normalize a base"
        wavelength = parse_args(arg, expected=1, type=float)[0]
        for (i, base) in enumerate(self.values):
            self.values[i] = base.normalize(wavelength)
            ok_print('Normalized: {}'.format(base.name))

    def do_name(self, arg):
        for base in self.values:
            pprint(base.name)

    def do_set_name(self, arg):
        name = parse_args(arg, expected=1)[0]
        for base in self.values:
            base.name = name
        ok_print('Name set to: {}'.format(name))

    def do_wavelength_index(self, arg):
        try:
            (start, end) = parse_tuple_int(arg, expected=2)
            if end == -1:
                end = None
            for base in self.values:
                print('{}: {}'.format(base.name, base.wavelength_str(start, end)))
            print('\n')
        except ValueError as value_error:
            error_print('wavelength index needs 2 args: (start, end)')
            raise value_error
        except IndexError as index_error:
            error_print('wavelength index error')
            error_print(str(index_error))
            raise index_error
        except TypeError as type_err:
            error_print('wavelength index must be an integer')
            raise type_error

    def do_wavelength_range(self, arg):
        try:
            (start, end) = parse_tuple(arg, expected=2, type=float)
            for base in self.values:
                pprint(base.wavelength_range(start, end))
        except ValueError as value_error:
            error_print('wavelength range (wl_start, wl_end)')
            raise value_error
        except IndexError as index_error:
            error_print('invalid wavelength range, choosing entire range')
            error_print(str(index_error))
            raise index_error
        except TypeError as type_error:
            error_print('wavelength range must be an integer')
            raise type_error

    def do_set_wavelength_index(self, arg):
        try:
            (start, end) = parse_tuple(arg, expected=2, type=int)
            for (i, base) in enumerate(self.values):
                self.values[i] = base.wavelength_set_index(start, end)
                ok_print('Wavelength index set: ({}, {})'.format(start, end))
        except ValueError as value_error:
            error_print('set_wavelength_index (start, end)')
            raise value_error

    def do_set_wavelength_start(self, arg):
        try:
            start = parse_tuple(arg, expected=1, type=float)[0]
            for (i, base) in enumerate(self.values):
                self.values[i] = base.wavelength_set_start(start)
                ok_print('Wavelength start set to: {}'.format(start))
        except ValueError as value_error:
            error_print('set_wavelength_start wl_start')
            raise value_error
        except IndexError as index_error:
            error_print('invalid wavelength start, wavelength start not set')
            error_print(str(index_error))
            pass
        except TypeError as type_error:
            error_print('wavelength start must be a float')
            raise type_error

    def do_set_wavelength_end(self, arg):
        try:
            end = parse_tuple(arg, expected=1, type=float)[0]
            for (i, base) in enumerate(self.values):
                self.values[i] = base.wavelength_set_end(end)
                ok_print('Wavelength end set to: {}'.format(end))
        except ValueError as value_error:
            error_print('set_wavelength_end wl_end')
            raise value_error
        except IndexError as index_error:
            error_print('invalid wavelength end, wavelength end not set')
            error_print(str(index_error))
            pass
        except TypeError as type_error:
            error_print('wavelength end must be a float')
            raise type_error
    
    def do_set_wavelength_range(self, arg):
        try:
            (start, end) = parse_tuple(arg, expected=2, type=float)
            for (i, base) in enumerate(self.values):
                self.values[i] = base.wavelength_set_range(start, end)
                ok_print('Wavelength range set: ({}, {})'.format(start, end))
        except ValueError as value_error:
            error_print('set_wavelength_range (wl_start, wl_end)')
            raise value_error
        except IndexError as index_error:
            error_print('invalid wavelength range, choosing entire range')
            error_print(str(index_error))
            pass
        except TypeError as type_error:
            error_print('wavelength range must be floats')
            raise type_error

    def do_flux(self, arg):
        try:
            args = parse_args(arg, expected=2)
            (s1, e1) = parse_tuple_int(args[0], expected=2)
            (s2, e2) = parse_tuple_int(args[1], expected=2)
            for base in self.values:
                pprint(base.flux[s1:e1, s2:e2])
        except ValueError as value_error:
            error_print('flux needs 5 args: index (start, end) (wl_start, wl_end)')
            raise value_error
        except IndexError as index_error:
            error_print('flux index error')
            raise index_error
        except TypeError as type_error:
            error_print('flux index and range must be integers')
            raise type_error

    def do_interpolation_wavelength_start(self, arg):
        args = parse_args(arg, expected=2, type=float)
        interp = args[0]
        wavelength = args[1]
        for base in self.values:
            wl_start = base.restrict_wavelength_start_by_interpolation_step(interp, wavelength)
            ok_print('{}: set starting wavelength to: {} using interpolation step: {}'.format(
                 base.name, wl_start, interp))
            
    def do_smoothen(self, arg):
        try:
            args = parse_args(arg, expected=1)
            interp = float(args[0])
            for (i, base) in enumerate(self.values):
                self.values[i] = base.smoothen(
                    interp,
                    name="smoothed_" + base.name,
                    step=base.wavelength_step)
                ok_print('Smoothed: {}'.format(base.name))
        except ValueError as value_error:
            error_print('Interpolation step needed')
            raise value_error
        except TypeError as type_error:
            error_print('Interpolation step must be a float')
            raise type_error

#===============================================================================

class Model_Shell(Base_Shell):
    asad_type = pyasad.Model

    def do_set_age_factor(self, arg):
        age_factor = parse_args(arg, expected=1, type=float)[0]
        for model in self.values:
            model.age_factor = age_factor

    def do_set_age_start(self, arg):
        age_start = parse_args(arg, expected=1, type=float)[0]
        for model in self.values:
            model.age_start = age_start

#===============================================================================

class Observation_Shell(Base_Shell):
    asad_type = pyasad.Observation

    def do_set_reddening_step(self, arg):
        reddening_step = parse_args(arg, expected=1, type=float)[0]
        for obsv in self.values:
            obsv.reddening_step = reddening_step

    def do_set_reddening_start(self, arg):
        reddening_start = parse_args(arg, expected=1, type=float)[0]
        for obsv in self.values:
            obsv.reddening_start = reddening_start

    def do_redshift(self, arg):
        try:
            [start, end, step] = parse_args(arg, expected=3, type=float)
            for (i, observation) in enumerate(self.values):
                self.values[i] = observation.reddening_shift(end, step)
                ok_print('Reddening Corrected: {}'.format(observation.name))
        except ValueError as value_error:
            error_print('Redshift: start end step needed')
            raise value_error
        except TypeError as type_error:
            error_print('Redshift: start, end and step must be floats')
            raise type_error

#===============================================================================

class Plot_Shell(Shell):
    pass

#===============================================================================

class Object_Shell(Base_Shell):
    asad_type = pyasad.Asad

    def __init__(self, *args, **kwargs):
        self._base = Base_Shell()
        self._model = Model_Shell()
        self._observation = Observation_Shell()
        super(Object_Shell, self).__init__(*args, **kwargs)

    def do_new(self, arg):
        args = parse_args(arg, expected=2)
        index = [parse_tuple(x, expected=2, type=int) for x in args]
        (ms, me) = index[0]
        (os, oe) = index[1]
        me = None if me == (-1) else me
        oe = None if oe == (-1) else oe
        for model in self.model.values[ms:me]:
            for obsv in self.observation.values[os:oe]:
                obj = pyasad.Asad.from_observation_model(obsv, model)
                self.values.append(obj)

    def do_list(self, arg):
        for obj in self.values:
            pprint(obj.name)

    def do_calculate_chosen_model(self, arg):
        try:
            for obj in self.values:
                if len(obj.model.wavelength) != len(obj.model.wavelength):
                    raise Exception(
                        ('Number of rows in observation: {} and model: {} not equal' +
                         'Observation : {} Model : {}').format(
                             obj.observation.name, obj.model.name,
                             obj.num_observation, obj.num_model
                         ))
                obj.calculate_chosen_model()
                ok_print('Calculated Min Age and Reddening: %s' % obj.name)
        except Exception as err:
            error_print('Error calculating chosen model')
            error_print(unicode(err))
            raise err

    def do_chosen(self, arg):
        if not self.values:
            print('Empty')
            return

        len_cols = (5, 15, 10, 10)
        ncols = len(len_cols)
        (col_str, sep_str) = ("{:^%d}|", "{:-^%d}+")
        fmt_col = '|' + (col_str * ncols) % len_cols
        sep = '+' + ((sep_str * ncols) % len_cols).format(*['']*ncols)

        print (sep)
        print(fmt_col.format('Index', 'Name', 'Min_Age', 'Min_Reddening'))
        print(sep)
        for (i, obj) in enumerate(self.values):
            print(fmt_col.format(
                i, obj.name[:15], obj.min_age, obj.min_reddening))
        print(sep)

    def do_write_chosen(self, arg, config=None):
        path = os.path.abspath(parse_args(arg, expected=1)[0])
        if os.path.isdir(path):
            for obj in self.values:
                fpath = os.path.join(path, 'result_of_%s' % obj.name)
                with io.open(fpath, 'w') as f:
                    f.write(obj.format_chosen())
                    if config:
                        buff = StringIO()
                        buff.write(unicode('\n'))
                        config.write(buff)
                        f.write(unicode(buff.getvalue()))
                ok_print('Wrote %s to %s' % (obj.name, fpath))
        elif os.path.isfile(path):
            with io.open(path, 'w') as f:
                for obj in self.values:
                    f.write(obj.format_chosen())
                if config:
                    buff = StringIO()
                    buff.write(unicode('\n'))
                    config.write(buff)
                    f.write(unicode(buff.getvalue()))
            ok_print('Wrote %s to %s' % (obj.name, path))

    @base_command
    def do_plot(self, arg):
        pass

    def do_plot_surface(self, arg, format=''):
        try:
            path = os.path.abspath(parse_args(arg, expected=1)[0])
            if not os.path.isdir(path):
                raise RuntimeError('Must be a directory')
            for obj in self.values:
                plot.surface(obj, outdir=path, save=True, format=format)
                ok_print('Plotted surface %s to %s' % (obj.name, path))
        except Exception as err:
            error_print(unicode(err))
            raise err

    def do_plot_scatter(self, arg, ages=[], reddenings=[], format=''):
        try:
            path = os.path.abspath(parse_args(arg, expected=1)[0])
            if not os.path.isdir(path):
                raise RuntimeError('Must be a directory')
            for obj in self.values:
                plot.scatter(obj, ages=ages, reddenings=reddenings,
                             outdir=path, save=True, format=format)
                ok_print('Plotted scatter %s to %s' % (obj.name, path))
        except Exception as err:
            error_print(unicode(err))
            raise err

    def do_plot_residual(self, arg, format=''):
        try:
            path = os.path.abspath(parse_args(arg, expected=1)[0])
            if not os.path.isdir(path):
                raise RuntimeError('Must be a directory')
            for obj in self.values:
                plot.residual(obj, outdir=path, save=True, format=format)
                ok_print('Plotted residual %s to %s' % (obj.name, path))
        except Exception as err:
            error_print(unicode(err))
            raise err

    def do_plot_surface_error(self, arg, format=''):
        try:
            path = os.path.abspath(parse_args(arg, expected=1)[0])
            if not os.path.isdir(path):
                raise RuntimeError('Must be a directory')
            for obj in self.values:
                obj.calculate_stat_delta_level()
                plot.surface_error(obj, outdir=path, save=True, format=format)
                ok_print('Plotted surface error %s to %s' % (obj.name, path))
        except Exception as err:
            error_print(unicode(err))
            raise err

    def do_plot_scatter_tile(self, arg, format=''):
        try:
            path = os.path.abspath(parse_args(arg, expected=1)[0])
            if not os.path.isdir(path):
                raise RuntimeError('Must be a directory')
            obj_len = len(self.values)
            ncols = 3
            nrows = obj_len / ncols
            plot.scatter_tile(self.values, nrows, ncols, outdir=path, save=True, format=format)
            ok_print('Plotted scatter tile %s' % path)
        except Exception as err:
            error_print(unicode(err))
            raise err        

    @property
    def base(self):
        return self._base

    @property
    def model(self):
        return self._model

    @property
    def observation(self):
        return self._observation

#===============================================================================

def prompt_command_2(func):
    def prompt_function(self):
        while True:
            try:
                func(self)
            except Exception as err:
                error_print(unicode(err))
                continue
            break
    return prompt_function

def prompt_command(func):
    def prompt_function(self):
        try:
            func(self)
        except Exception as err:
            error_print(unicode(err))
            raise err
    return prompt_function


#-------------------------------------------------------------------------------

class Run_Shell(Object_Shell):

    def __init__(self, *args, **kwargs):
        self.object = Object_Shell()
        self.config = GlobalConfig()
        super(Run_Shell, self).__init__(*args, **kwargs)

    def update_config(self):
        self.config.write_config_file()

    @prompt_command
    def model_read(self):
        self.config['model_input_directory'] = safe_default_input(
            'Model path',
            self.config['model_input_directory'])
        self.model.do_read_file_directory(self.config['model_input_directory'])

    @prompt_command
    def model_interpolation_wavelength_start(self):
        self.config['model_interpolation_wavelength_start'] = self.config['observation_interpolation_wavelength_start']
        self.model.do_interpolation_wavelength_start(
            self.config['model_interpolation_wavelength_start'])

    @prompt_command
    def model_interpolation_wavelength_start_2(self):
        self.model.do_interpolation_wavelength_start('{} {}'.format(
            self.config['observation_interpolation_step'],
            self.config['observation_wavelength_start']))

    @prompt_command
    def model_smoothen(self):
        self.config['model_interpolation_step'] = self.config['observation_interpolation_step']
        self.model.do_smoothen(self.config['observation_interpolation_step'])

    @prompt_command
    def model_wavelength_range(self):
        print('Current Wavelength Range: ')
        self.model.do_wavelength_index('(0, -1)')
        self.config['model_wavelength_start'] = self.config['observation_wavelength_start']
        self.config['model_wavelength_end'] = self.config['observation_wavelength_end']
        self.model.do_set_wavelength_range('(%s, %s)' % (
            self.config['observation_wavelength_start'],
            self.config['observation_wavelength_end']))

    @prompt_command
    def model_normalize_wavelength(self):
        self.config['model_normalize_wavelength'] = self.config['observation_normalize_wavelength']
        self.model.do_normalize(self.config['observation_normalize_wavelength'])

    @prompt_command
    def model_output(self):
        self.config['model_output_directory'] = safe_default_input(
            'Output directory',
            self.config['model_output_directory'])
        self.model.do_write(self.config['model_output_directory'])

    @prompt_command
    def observation_read(self):
        self.config['observation_input_directory'] = safe_default_input(
            'Observation path or directory',
            self.config['observation_input_directory'])
        self.observation.do_read_file_directory(
            self.config['observation_input_directory'])

    @prompt_command
    def observation_smoothen(self):
        self.config['observation_interpolation_step'] = safe_default_input(
            'Interpolation Step',
            self.config['observation_interpolation_step'])
        self.observation.do_smoothen(self.config['observation_interpolation_step'])

    @prompt_command
    def observation_smoothen_output(self):
        self.config['observation_smoothen_output_directory'] = safe_default_input(
            'Smoothed Output directory',
            self.config['observation_smoothen_output_directory'])
        self.observation.do_write(
            self.config['observation_smoothen_output_directory'],
            prefix='smoothed_')

    @prompt_command
    def observation_reddening(self):
        self.config['observation_reddening_start'] = safe_default_input(
            'Reddening Start',
            self.config['observation_reddening_start'])
        self.config['observation_reddening_step'] = safe_default_input(
            'Reddening Step',
            self.config['observation_reddening_step'])
        self.config['observation_reddening'] = safe_default_input(
            'Reddening',
            self.config['observation_reddening'])
        self.observation.do_redshift(' '.join([
            self.config['observation_reddening_start'],
            self.config['observation_reddening'],
            self.config['observation_reddening_step']]))

    @prompt_command
    def observation_wavelength_start(self):
        print('Current Wavelength Range: ')
        self.observation.do_wavelength_index('(0, -1)')
        self.config['observation_wavelength_start'] = safe_default_input(
            'Wavelength Start (Angstroms)',
            self.config['observation_wavelength_start'])
        self.observation.do_set_wavelength_start(
            self.config['observation_wavelength_start'])

    @prompt_command
    def observation_wavelength_end(self):
        print('Current Wavelength Range: ')
        self.observation.do_wavelength_index('(0, -1)')
        self.config['observation_wavelength_end'] = safe_default_input(
            'Wavelength End (Angstroms)',
            self.config['observation_wavelength_end'])
        self.observation.do_set_wavelength_end(
            self.config['observation_wavelength_end'])
    
    @prompt_command
    def observation_wavelength_range(self):
        print('Current Wavelength Range: ')
        self.observation.do_wavelength_index('(0, -1)')
        self.config['observation_wavelength_start'] = safe_default_input(
            'Wavelength Start (Angstroms)',
            self.config['observation_wavelength_start'])
        self.config['observation_wavelength_end'] = safe_default_input(
            'Wavelength End (Angstroms)',
            self.config['observation_wavelength_end'])
        self.observation.do_set_wavelength_range('(%s, %s)' % (
            self.config['observation_wavelength_start'],
            self.config['observation_wavelength_end']))

    @prompt_command
    def observation_normalize_wavelength(self):
        self.config['observation_normalize_wavelength'] = safe_default_input(
            'Wavelength (Angstroms)',
            self.config['observation_normalize_wavelength'])
        self.observation.do_normalize(self.config['observation_normalize_wavelength'])

    @prompt_command
    def observation_output(self):
        self.config['observation_output_directory'] = safe_default_input(
            'Output directory',
            self.config['observation_output_directory'])
        self.observation.do_write(
            self.config['observation_output_directory'],
            prefix='normalized_')

    def object_generate(self):
        print('Generating object files...')
        for model in self.model.values:
            for obsv in self.observation.values:
                obj = pyasad.Asad.from_observation_model(obsv, model)
                self.object.values.append(obj)
                ok_print('Done. Model: %s Observation: %s' % \
                         (model.name, obsv.name))

    @prompt_command
    def object_output(self):
        self.config['object_output_directory'] = safe_default_input(
            'Object directory',
            self.config['object_output_directory'])
        self.object.do_write(self.config['object_output_directory'])

    def object_calculate_chosen(self):
        print('Calculating best match of age and reddening (chi-squared)...')
        self.object.do_calculate_chosen_model('')

    @prompt_command
    def object_output_chosen(self):
        self.config['object_chosen_directory'] = safe_default_input(
            'Output file or directory',
            self.config['object_chosen_directory'])
        self.object.do_write_chosen(self.config['object_chosen_directory'],
                                    self.config)

    @prompt_command
    def plot_output_format(self):
        self.config['plot_output_format'] = safe_default_input(
            'Plot output format',
            self.config['plot_output_format'])

    @prompt_command
    def plot_surface_output(self):
        self.config['plot_surface_directory'] = safe_default_input(
            'Output directory',
            self.config['plot_surface_directory'])
        self.object.do_plot_surface(self.config['plot_surface_directory'],
                                    format=self.config['plot_output_format'])

    @prompt_command
    def plot_scatter_output(self):
        self.config['plot_scatter_directory'] = safe_default_input(
            'Output directory',
            self.config['plot_scatter_directory'])
        reddenings, ages = [], []
        if parse_input_yn('Custom age and reddening pairs?'):
            ages = [float(a) for a in safe_input('Ages: ').split(' ')]
            reddenings = [float(r) for r in safe_input('Reddenings: ').split(' ')]
            if len(reddenings) != len(ages):
                raise ValueError(
                    "Must select an equal number of reddenings and ages")
        self.object.do_plot_scatter(self.config['plot_scatter_directory'],
                                    ages=ages, reddenings=reddenings,
                                    format=self.config['plot_output_format'])

    @prompt_command
    def plot_scatter_output_aux(self):
        self.config['plot_scatter_directory'] = safe_default_input(
            'Output directory',
            self.config['plot_scatter_directory'])
        reddenings, ages = [], []
        self.object.do_plot_scatter(self.config['plot_scatter_directory'],
                                    ages=ages, reddenings=reddenings,
                                    format=self.config['plot_output_format'])

    @prompt_command
    def plot_residual_output(self):
        self.config['plot_residual_directory'] = safe_default_input(
            'Output directory',
            self.config['plot_residual_directory'])
        self.object.do_plot_residual(self.config['plot_residual_directory'],
                                     format=self.config['plot_output_format'])

    @prompt_command
    def plot_surface_error_output(self):
        self.config['plot_surface_error_directory'] = safe_default_input(
            'Output directory',
            self.config['plot_surface_error_directory'])
        self.object.do_plot_surface_error(self.config['plot_surface_error_directory'],
                                          format=self.config['plot_output_format'])

    @prompt_command
    def plot_scatter_tile_output(self):
        self.object.do_plot_scatter_tile(self.config['plot_surface_error_directory'],
                                         format=self.config['plot_output_format'])
    
    def cmdloop(self):
        info_print("Assistant mode.")

        self.observation_read()
        if parse_input_yn('Observation set wavelength start (Angstroms)', default=True):
            self.observation_wavelength_start()
        if parse_input_yn('Smooth the observation', default=True):
            self.observation_smoothen()
        if parse_input_yn('Observation set wavelength end (Angstroms)', default=True):
            self.observation_wavelength_end()
        if parse_input_yn('Output smoothed observations'):
            self.observation_smoothen_output()
        if parse_input_yn('Observation reddening correction', default=True):
            self.observation_reddening()

        if parse_input_yn('Observation normalize wavelength', default=True):
            self.observation_normalize_wavelength()
        if parse_input_yn('Output observations'):
            self.observation_output()

        self.update_config()
        
        self.model_read()
        self.model_interpolation_wavelength_start_2()
        self.model_smoothen()
        self.model_wavelength_range()
        self.model_normalize_wavelength()
        if parse_input_yn('Output models'):
            self.model_output()

        self.update_config()
        
        self.object_generate()
        if parse_input_yn('Output object files'):
            self.object_output()
        self.object_calculate_chosen()
        if parse_input_yn('Output chosen'):
            self.object_output_chosen()
        self.plot_output_format()
        if parse_input_yn('Output surface plots'):
            self.plot_surface_output()
        if parse_input_yn('Output best spectra match plots'):
            self.plot_scatter_output()
        if parse_input_yn('Output residual plots'):
            self.plot_residual_output()
        if parse_input_yn('Output surface error plots'):
            self.plot_surface_error_output()
        if parse_input_yn('Output scatter tile plot'):
            self.plot_scatter_tile_output()
        self.update_config()

#==============================================================================

class Main_Shell(cmd.Cmd):
    intro = "Welcome. Type ? for help."
    prompt = "<pyasad> "

    def __init__(self, *args, **kwargs):
        self._object = Object_Shell()
        cmd.Cmd.__init__(self, *args, **kwargs)

    def execute(self, path):
        "Execute a command script"
        with io.open(os.path.abspath(path), 'r') as f:
            for line in f.readlines():
                self.onecmd(line)

    def emptyline(self):
        pass

    @property
    def base(self):
        return self.object._base
    @property
    def model(self):
        return self.object._model
    @property
    def observation(self):
        return self.object._observation

    @property
    def object(self):
        return self._object
    @object.setter
    def object(self, obj):
        self._object = obj

    def do_base(self, arg):
        return self.base.onecmd(arg)
    def do_model(self, arg):
        return self.model.onecmd(arg)
    def do_observation(self, arg):
        return self.observation.onecmd(arg)
    def do_object(self, arg):
        return self.object.onecmd(arg)
    def do_run(self, arg):
        return Run_Shell().cmdloop()
    def do_quit(self, arg):
        print('Quitting')
        sys.exit(0)

#==============================================================================

def override_safe_default_input(s, default=None):
    return default

def override_prompt_command(func):
    return func

def set_not_interactive():
    global safe_default_input
    safe_default_input = override_safe_default_input

#===============================================================================
