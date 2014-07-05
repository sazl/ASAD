#include <cstddef>
using std::size_t;

#include <asad/math.h>

namespace asad
{

arma::vec wavelength_interpolate_step(arma::vec wavelength, double interp,
                                      double step)
{
    double sample_step = interp / step;
    size_t nsample     = static_cast<size_t>((2*sample_step) - 1);
    size_t result_num  = static_cast<size_t>((wavelength.n_elem/sample_step) - 1);
    arma::vec result(result_num);
    
    for (size_t i = 0; i < result_num; i++) {
        double total = 0.0;
        for (size_t k = 0; k < nsample; k++) {
            total += wavelength(i*sample_step + k);
        }
        result(i) = total / nsample;
    }
    return result;
}

arma::mat flux_interpolate_step(arma::mat flux, double interp, double step)
{
    double sample_step  = interp / step;
    size_t nsample      = static_cast<size_t>(2*sample_step - 1);
    size_t result_nrows = flux.n_rows;
    size_t result_ncols = flux.n_cols;
    arma::mat result(result_nrows, result_ncols);

    for (size_t i = 0; i < result_nrows; i++) {
        arma::vec row = flux.row(i);
        for (size_t j = 0; j < result_ncols; j++) {
            double total = 0.0;
            size_t num   = j * sample_step;
            arma::vec sample = row.subvec(num, num+nsample);
            for (size_t k = 0; k < nsample; k++) {
                total += sample(k);
            }
            result(i, j) = total / nsample;
        }
    }
    return result;    
}

double chi_squared_frequency_test(arma::vec xs, arma::vec ys)
{
    arma::vec diff = xs - ys;
    arma::vec pow  = arma::pow(diff, 2.0);
    return arma::accu(pow);
}

unsigned int search_sorted(arma::vec xs, double value)
{
    arma::uvec indices = arma::find(xs < value, 1);
    if (indices.n_elem == 0)
        return xs.n_elem;
    return indices(0);
}

}
