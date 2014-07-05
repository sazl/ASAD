#ifndef ASAD_MATH_H_
#define ASAD_MATH_H_

#include <armadillo>

namespace asad {

arma::vec
wavelength_interpolate_step(arma::vec wavelength, double interp, double step);

arma::mat
flux_interpolate_step(arma::mat flux, double interp, double step);

double
chi_squared_frequency_test(arma::vec xs, arma::vec ys);

unsigned int
search_sorted(arma::vec xs, double value);

}

#endif
