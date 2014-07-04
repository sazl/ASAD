#include <cmath>
#include <cstdlib>

#include <iostream>
#include <fstream>
#include <string>

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
            result[i] = total / nsample;
        }
    }

    return result;
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
            result[i] = total / nsample;
        }
    }

    result.insert(result.begin(), xs[0]);
    return result;
}

mat flux_interpolate_step(mat xss, double interp, double step)
{
    return mat();
}

} // end namespace asda.math



namespace statistics {

const std::string STAT_TEST_NAMES[] = {"chi-squared", "ks2"};

vec chi_squared_freq_test(vec xs, vec ys)
{
    size_t rsize = xs.size();
    vec result(rsize);
    for (size_t i = 0; i < rsize; i++)
        result[i] = pow(xs[i] - ys[i], 2.0);
    return result;
}

} // end namespace asad.statistics

} // end namespace asad
