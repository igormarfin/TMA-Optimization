///run me
/// FindSection.C(TString arg1,TString arg2,TString arg3)


#include "TString.h"
#include "TSystem.h"
#include <iostream>


TString FindSection(TString arg1,TString arg2,TString arg3){
TString cmd=TString("source utils.sh; ");
cmd+=TString(FindSection );
cmd+=TString(' ')+arg1+TString(' ');
cmd+=TString(' ')+arg2+TString(' ');
cmd+=TString(' ')+arg3+TString(' ');
TString res =gSystem->GetFromPipe(cmd.Data()) ;
std::cout<<res<<std::endl;
return res;}
