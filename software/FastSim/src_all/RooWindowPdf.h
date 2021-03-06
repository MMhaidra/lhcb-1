/*****************************************************************************
 * Project: RooFit                                                           *
 *                                                                           *
  * This code was autogenerated by RooClassFactory                            * 
 *****************************************************************************/

#ifndef ROOWINDOWPDF
#define ROOWINDOWPDF

#include "RooAbsPdf.h"
#include "RooRealProxy.h"
#include "RooCategoryProxy.h"
#include "RooAbsReal.h"
#include "RooAbsCategory.h"
 
class RooWindowPdf : public RooAbsPdf {
public:
  RooWindowPdf() {} ; 
  RooWindowPdf(const char *name, const char *title,
	      RooAbsReal& _x,
	      RooAbsReal& _hi,
	      RooAbsReal& _low);
  RooWindowPdf(const RooWindowPdf& other, const char* name=0) ;
  virtual TObject* clone(const char* newname) const { return new RooWindowPdf(*this,newname); }
  inline virtual ~RooWindowPdf() { }

protected:

  RooRealProxy x ;
  RooRealProxy hi ;
  RooRealProxy low ;
  
  Double_t evaluate() const ;

private:

  ClassDef(RooWindowPdf,1) // Your description goes here...
};
 
#endif
