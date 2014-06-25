#include <cstdlib>

#include <iostream>
#include <fstream>

#include "asad.h"

namespace asad {



namespace math {

vec wavelength_interpolate_step(vec xs, double interp, double step) {
    if (interp == step) {
        return xs;
    }

    std::size_t sample_step = interp / step;
    std::size_t nsample     = 2*sample_step - 1;
    std::size_t result_num  = (xs.size() / sample_step) - 1;
    vec result(result_num);

    for (std::size_t i = 0; i < result_num; i++) {
        double total = 0;
        for (std::size_t k = 0; k < nsample; k++) {
            result[i] = tot / nsample;
        }
    }

    return result
}

vec wavelength_interpolate_step_obsv(vec xs, double interp, double step)
{
    if (interp == step) {
        return xs;
    }

    std::size_t sample_step = interp / step;
    std::size_t nsample     = 2*sample_step - 1;
    std::size_t result_num  = (xs.size() / sample_step) - 3;
    vec result(result_num);
    vec xs2(xs.begin() + 1, xs.end());

    for (std::size_t i = 0; i < result_num; i++) {
        double total = 0;
        for (std::size_t k = 0; k < nsample; k++) {
            result[i] = tot / nsample;
        }
    }

    result.insert(result.begin(), xs[0]);
    return result;
}

vec flux_interpolate_step(mat xss, double inter, double step)
{
    if (interp == step) {
        return xss;
    }

    sample_step  = interp / step;
    nsample      = 2*sample_step - 1;
    result_nrows = xss.size();
    
} // end namespace asda.math

namespace statistics {

} // end namespace asad.statistics


} // end namespace asad
