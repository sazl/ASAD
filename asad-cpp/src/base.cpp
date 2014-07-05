#include <asad/base.h>
#include <asad/math.h>

namespace asad {
namespace base {

Base::Base()
    : wavelength_step_(0.0)
{}

Base::Base(const Base &base)
    : wavelength_step_(base.wavelength_step_),
      wavelength_(base.wavelength_),
      flux_(base.flux)
{}

Base::Base(const arma::vec wavelength, const arma::mat flux)
{
    this->set_wavelength(wavelength);
    this->set_flux(flux);
}

Base::~Base()
{}

arma::vec Base::wavelength()
{
    return wavelength_;
}

arma::mat Base::flux()
{
    return flux_;
}

void Base::set_wavelength(arma::vec wavelength)
{
    wavelength_ = wavelength;
    wavelength_step_ = wavelength(1) - wavelength(0);
}

void Base::set_flux(arma::mat flux)
{
    flux_ = flux;
}


Base read_from_path(std::string path)
{
    Base result;
    arma::mat mat;
    mat.load(path, arma::arma_ascii);
    result.set_wavelength(mat.row(0));
    result.set_flux(mat.rows(1, mat.n_rows - 1));
    return result;
}

Base normalize(Base base, double wavelength)
{
    Base result(base);
    unsigned int index = asad::search_sorted(result.wavelength(), wavelength);
    arma::mat flux = arma::trans(result.flux());
    if (index >= result.wavelength().n_elem)
        return result;
    flux.rows(0, index) /= flux.row(index);
    flux.rows(index+1, flux.n_rows-1) /= flux.row(index);
    flux.row(index) = arma::ones<arma::vec>(flux.n_cols);
    result.set_flux(flux);
    return result;
}

} // namespace base
} // namespace asad
