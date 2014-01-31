///run me
/// findLine.C.C()


#include "TString.h"
#include "TSystem.h"
#include <iostream>


TString findLine.C(){
TString cmd=TString("source utils.sh; ");
cmd+=TString("findLine.C " );
TString res =gSystem->GetFromPipe(cmd.Data()) ;
std::cout<<res<<std::endl;
return res;}
