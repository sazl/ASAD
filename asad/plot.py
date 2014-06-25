import os.path, re, sys

import numpy              as np
import matplotlib         as mpl
mpl.use('Agg')

import matplotlib.cm      as cm
import matplotlib.pyplot  as plt
import matplotlib.markers as markers

options = {
    'xtick.major.size'        : 20,
    'xtick.major.width'       : 1,
    'xtick.minor.size'        : 10,
    'xtick.minor.width'       : 0.5,
    'ytick.major.size'        : 20,
    'ytick.major.width'       : 1,
    'ytick.minor.size'        : 10,
    'ytick.minor.width'       : 0.5,
    'figure.max_open_warning' : 100
}

font = {
    'fontname' : 'Sans',
    'fontsize' : 22
}

def model_name_format(model_name):
    m = re.match('\.z(\d{3})', model_name)
    if not m:
        return model_name
    else:
        return 'z=%s' % m.group(1)

def title_format(obj):
    model_name = obj.model.name
    observation_name = obj.observation.name
    return '[ {} with {} ]'.format(observation_name, model_name)

def surface(obj, levels=15, outdir="",
            fname='',
            format='eps',
            labels=False,
            save=False,
            show=False,
            *args, **kwargs):
    mpl.rcParams = dict(mpl.rcParams, **options)
    NL = levels
    x  = obj.model.age
    y  = obj.observation.reddening
    z  = 1.0 / np.array(obj.stat)

    fig = plt.figure(figsize=(16,10))
    border_width = 0.10
    border_height = 0.07
    ax_size = [0+border_width, 0+border_height,
               1-0.5*border_width, 1-2*border_height]
    ax = fig.add_axes(ax_size)

    C  = plt.contour(x, y, z, NL, colors=['k'], linewidths=0.10)
    if labels: plt.clabel(C, inline=1, fontsize=10, linewidths=0.10)
    CF = plt.contourf(x, y, z, NL, alpha=0.85, cmap=cm.jet)
    CF.cmap.set_under('k')
    CF.cmap.set_over('w')
    cb = fig.colorbar(CF)
    cb.set_label("Inverse Chi-Squared Statistic")
    plt.scatter([obj.min_age], [obj.min_reddening], c='w', s=350, marker="*")

    plt.xlim([obj.model.age[0], obj.model.age[-1]])
    plt.ylim([obj.observation.reddening[0], obj.observation.reddening[-1]])

    plt.title(title_format(obj), **font)
    plt.xlabel("log(Age/Year)", **font)
    plt.ylabel("Reddening", **font)

    plt.minorticks_on()
    plt.grid(which='both')

    file_name = fname or ("surface_" + obj.name)
    if save:
        plt.savefig(
            os.path.abspath(os.path.join(outdir, file_name)) + "." + format,
            format=format,
            bbox_inches=0
        )

    if show:
        plt.show()
    plt.close()

def scatter(obj, ages=[], reddenings=[], outdir='',
            fname='',
            format='eps',
            title='',
            xlabel='',
            ylabel='',
            save=False,
            show=False,
            *args, **kwargs):
    fig, ax = plt.subplots()
    model = obj.model
    obsv = obj.observation

    def find_indices(values, target):
        return np.searchsorted(values, target)

    model_index = find_indices(model.age, ages)-1
    if len(model_index) == 0: model_index = [obj.min_model]
    obsv_index = find_indices(obsv.reddening, reddenings)
    if len(obsv_index) == 0: obsv_index = [obj.min_observation]

    for mi in model_index:
        model_label = 'Model: age=%s' % (model.age[mi])
        plt.plot(model.wavelength, model.flux[mi],
                label=model_label, linewidth=0.5)

    for oi in obsv_index:
        obsv_label = 'Observation: reddening=%s' % (obsv.reddening[oi])
        plt.plot(obsv.wavelength, obsv.flux[oi],
                 label=obsv_label, linewidth=0.5)

    plt.title('Flux vs Wavelength\n' + title_format(obj))
    plt.xlabel("Wavelength (Angstroms)")
    plt.ylabel("Normalized Flux")
    plt.legend(loc='upper right', shadow=False, prop={'size':8})

    file_name = fname or ("best_spectra_match_" + obj.name)
    if save:
        plt.savefig(
            os.path.abspath(os.path.join(outdir, file_name)) + "." + format,
            format=format
        )

    if show:
        plt.show()
    plt.close()

def residual(obj, outdir='',
            fname='',
            format='eps',
            title='',
            xlabel='',
            ylabel='',
            save=False,
            show=False,
            *args, **kwargs):
    model = obj.model
    obsv = obj.observation
    flux = model.flux[obj.min_model] - obsv.flux[obj.min_observation]
    f, (ax1, ax2, ax3, ax4) = plt.subplots(4, sharex=True, sharey=True)

    ax1.plot(model.wavelength, model.flux[obj.min_model],
             label="Model Flux", linewidth=0.5)
    ax1.set_title('Normalized Flux vs Wavelength\n' + title_format(obj))
    ax1.tick_params(which='major', labelsize=8)
    ax1.legend(loc='upper right', shadow=False, prop={'size':7})

    ax2.plot(obsv.wavelength, obsv.flux[obj.min_observation],
             label="Observation Flux", linewidth=0.5)
    ax2.set_ylabel("Normalized Flux")
    ax2.legend(loc='upper right', shadow=False, prop={'size':7})
    ax2.tick_params(which='major', labelsize=8)

    ax3.plot(model.wavelength, model.flux[obj.min_model], linewidth=0.5)
    ax3.plot(obsv.wavelength, obsv.flux[obj.min_observation], linewidth=0.5)
    ax3.tick_params(which='major', labelsize=8)

    ax4.axhline(0, color='black', linewidth=1)
    ax4.set_xlim(obsv.wavelength[0], obsv.wavelength[-1])
    ax4.plot(obsv.wavelength, flux, label="Residual Flux", linewidth=0.5)
    ax4.set_xlabel("Wavelength (Angstroms)")

    ax4.legend(loc='upper right', shadow=False, prop={'size':7})
    ax4.tick_params(axis='y', which='major', labelsize=8)

    file_name = fname or ("residual_" + obj.name)
    if save:
        plt.savefig(
            os.path.abspath(os.path.join(outdir, file_name)) + "." + format,
            format=format
        )

    if show:
        plt.show()
    plt.close()

def surface_error(obj, levels=15, outdir='',
            fname='',
            format='eps',
            labels=False,
            title='',
            xlabel='',
            ylabel='',
            save=False,
            show=False,
            *args, **kwargs):
    mpl.rcParams = dict(mpl.rcParams, **options)
    NL = levels
    x  = obj.model.age
    y  = obj.observation.reddening
    z  = 1.0 / np.array(obj.stat)

    fig = plt.figure(figsize=(16,10))
    border_width = 0.10
    border_height = 0.07
    ax_size = [0+border_width, 0+border_height,
               1-0.5*border_width, 1-2*border_height]
    ax = fig.add_axes(ax_size)

    C  = plt.contour(x, y, z, NL, colors=['k'], linewidths=0.10)
    if labels: plt.clabel(C, inline=1, fontsize=10, linewidths=0.10)
    CF = plt.contourf(x, y, z, NL, alpha=0.85, cmap=cm.jet)
    CF.cmap.set_under('k')
    CF.cmap.set_over('w')
    cb = fig.colorbar(CF)
    cb.set_label("Inverse Chi-Squared Statistic")
    plt.scatter([obj.min_age], [obj.min_reddening], c='w', s=350, marker="*")
    for error_age, error_reddening, error_stat in zip(obj.error_age, obj.error_reddening, obj.error_stat):
        plt.plot([error_age], [error_reddening], 'ro')

    plt.xlim([obj.model.age[0], obj.model.age[-1]])
    plt.ylim([obj.observation.reddening[0], obj.observation.reddening[-1]])

    plt.title(title_format(obj), **font)
    plt.xlabel("log(Age/Year)", **font)
    plt.ylabel("Reddening", **font)

    plt.minorticks_on()
    plt.grid(which='both')

    file_name = fname or ("surface_error_" + obj.name)
    if save:
        plt.savefig(
            os.path.abspath(os.path.join(outdir, file_name)) + "." + format,
            bbox_inches=0
        )

    if show:
        plt.show()
    plt.close()
