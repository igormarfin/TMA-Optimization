#include <vector>
#include <string>
#include <iostream>

#include "TMVA/Factory.h"
#include "TMVA/Tools.h"

#include "TString.h"


//void test(std::vector<char *> & strs, int & a)
void test(std::vector<std::string>  & strs, int  & a, double & dbl, std::vector<std::string>  & strs2)
{

a=strs.size();
std::cout<<"a = "<<a<<std::endl;
a=10;
dbl=4.5;
strs2.push_back(std::string("aaa"));
strs2.push_back(std::string("bbb"));

TString outfileName=TString("test.root");
TFile* outputFile = TFile::Open( outfileName, "RECREATE" );

TMVA::Factory *factory = new TMVA::Factory( "TMVAClass", outputFile,
                                               "!V:!Silent:Color:DrawProgressBar:Transformations=I;D;P;G,D" );
//fac=factory;

TPython::Bind(factory,"factory");
return;

}
