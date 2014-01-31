///run me
/// field.C.C()


#include "TString.h"
#include "TSystem.h"
#include <iostream>


TString field.C(){
TString cmd=TString("source utils.sh; ");
cmd+=TString("field.C " );
TString res =gSystem->GetFromPipe(cmd.Data()) ;
std::cout<<res<<std::endl;
return res;}
