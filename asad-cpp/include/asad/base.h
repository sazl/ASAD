#ifndef ASAD_BASE_H_
#define ASAD_BASE_H_

#include <string>

#include <armadillo>

namespace asad {
namespace base {

class Base
{
  public:
    Base();
    Base(const Base& base);
    Base(const arma::vec wavelength, const arma::mat flux);
    virtual ~Base();

    arma::vec wavelength();
    arma::mat flux();

    void set_wavelength(arma::vec wavelength);
    void set_flux(arma::mat flux);
        
  private:
    double    wavelength_step_;
    arma::vec wavelength_;
    arma::mat flux_;
};

Base        read_from_path(std::string path);
Base        normalize(Base base);
std::string format(Base base);


} // namespace base
} // namespace asad

#endif
