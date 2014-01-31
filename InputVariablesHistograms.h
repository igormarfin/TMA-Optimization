#ifndef InputVariablesHistograms_H
#define InputVariablesHistograms_H

///from utils.h --> text processing support
#include "field.C.h"
#include "findLine.C.h"

#include "MathRoot.h"
#include "TtSemiLepSignalSel.h"


#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <iostream>



#include "TH1F.h"
#include "TNamed.h"

class InputVariablesHistograms : public TNamed {

public:

InputVariablesHistograms():TNamed("InputVariablesHistograms","InputVariablesHistograms")
{ 
	_histos = 0;
	isOk_=false;	
}


InputVariablesHistograms(TString name, TString title, std::string & mvaPath, std::vector<std::string> & mvaMethod):TNamed(name,title),isOk_(true)
{
	mvaPath_ = mvaPath;
	mvaMethod_ = mvaMethod;
	_histos=0;
if  (mvaPath_.empty() || mvaMethod_.size() ==0 ) { std::cout<<"Please, provide me proper settings, return"<<std::endl; isOk_=false ;}
if (!isOk_) return;

///Extract all variables used by MVA!
/**
        idea of parsing *.weights.xml
        1) read section

        <Variables >    </Variables>

Example :

 <Variables NVar="6">
    <Variable VarIndex="0" Expression="detajet2jet3" Label="detajet2jet3" Title="detajet2jet3" Unit="F" Internal="detajet2jet3" Type="F" Min="2.13906e-05$
    <Variable VarIndex="1" Expression="detajet3jet4" Label="detajet3jet4" Title="detajet3jet4" Unit="F" Internal="detajet3jet4" Type="F" Min="3.42131e-05$
    <Variable VarIndex="2" Expression="dphiMETlepton" Label="dphiMETlepton" Title="dphiMETlepton" Unit="F" Internal="dphiMETlepton" Type="F" Min="6.91414$
    <Variable VarIndex="3" Expression="lepeta" Label="lepeta" Title="lepeta" Unit="F" Internal="lepeta" Type="F" Min="3.16916e-05" Max="2.49505"/>
    <Variable VarIndex="4" Expression="maxdijetmass" Label="maxdijetmass" Title="maxdijetmass" Unit="F" Internal="maxdijetmass" Type="F" Min="0.00531079"$
    <Variable VarIndex="5" Expression="mindijetmass" Label="mindijetmass" Title="mindijetmass" Unit="F" Internal="mindijetmass" Type="F" Min="0.00186576"$
  </Variables>


2) extract from section: NVars, VarIndex && Expression

        It can be done with a help of utilites from utils.h --> findLine && field

        So, do it : #include "findLine.C.h";
                     #include "field.C.h"
                this *.h can be made by calling function createCPPcode 'findLine' or  createCPPcode 'field' from utils.h



**/


TString prefix;
TString   methodName;
TString weightfile;

///read all variables from first mvaMethod

   std::vector<std::string>::const_iterator it2 = mvaMethod_.begin();
   prefix = "TMVAClassification";
   methodName = TString(*it2)+TString(" method");
   weightfile = TString(mvaPath_) + TString("/") + prefix + TString("_") +  TString(*it2) + TString(".weights.xml");



TString res=findLine("Variable","NVar",weightfile,TString(mvaPath_) + "/");
res.ReplaceAll("<"," ");  res.ReplaceAll("="," ");
res.ReplaceAll(">"," "); res.ReplaceAll("\""," ");
res=field(TString("\"")+res+TString("\""),"3",TString(mvaPath_) + "/");
int nVars=res.Atoi();

TString vars=findLine("Variable","VarIndex",weightfile,TString(mvaPath_) + "/");
vars.ReplaceAll("<"," ");  vars.ReplaceAll("="," ");  vars.ReplaceAll(">"," ");
vars.ReplaceAll("\""," ");
vars=field(TString("\"")+vars+TString("\""),"5",TString(mvaPath_) + "/");
vars.ReplaceAll("\n"," ");

//cout<<"vars!"<<endl;
//cout<<vars<<endl;


TString mins=findLine("Variable","VarIndex",weightfile,TString(mvaPath_) + "/");
mins.ReplaceAll("<"," ");  mins.ReplaceAll("="," ");  mins.ReplaceAll(">"," ");
mins.ReplaceAll("\""," ");
mins=field(TString("\"")+mins+TString("\""),"17",TString(mvaPath_) + "/");
mins.ReplaceAll("\n"," ");

//cout<<"mins!"<<endl;
//cout<<mins<<endl;


TString maxes=findLine("Variable","VarIndex",weightfile,TString(mvaPath_) + "/");
maxes.ReplaceAll("<"," ");  maxes.ReplaceAll("="," ");  maxes.ReplaceAll(">"," ");
maxes.ReplaceAll("\""," ");
maxes=field(TString("\"")+maxes+TString("\""),"19",TString(mvaPath_) + "/");
maxes.ReplaceAll("\n"," ");


//cout<<"maxes!"<<endl;
//cout<<maxes<<endl;


_histos = new TList();



for (int i=0;i<nVars;i++)
{

TString vars2=vars;
TString varNum=Form("%d",i+1);

vars2=field(TString("\"")+vars2+TString("\""),varNum,TString(mvaPath_) + "/");



TString mins2=mins;
mins2=field(TString("\"")+mins2+TString("\""),varNum,TString(mvaPath_) + "/");

TString maxes2=maxes;
maxes2=field(TString("\"")+maxes2+TString("\""),varNum,TString(mvaPath_) + "/");

//std::cout<<"maxes = "<<maxes2<<std::endl;
//std::cout<<"mins = "<<mins2<<std::endl;


_histos->Add( new TH1F(TString("_cp_")+ vars2 + TString("_") + TString(GetName()), vars2  , 100, mins2.Atof(), maxes2.Atof() ));


//std::cout<<"my var is "<<vars2<<std::endl;

vars_[vars2.Data()]=new float(-1e10);
varindexes_[vars2.Data()] = i;

}




}

~InputVariablesHistograms()
{
	if (_histos!=0) delete _histos;
}

void FillHistograms(std::vector<math::XYZTLorentzVector> & jets_,double weight=1e0)
{

if (!isOk_ ) {std::cout <<"Something wrong with initiallization, return"<<std::endl; return;}
if (jets_.size() == 0 ) {
///std::cout <<"Something wrong with jets, return"<<std::endl;
return;
}

TtSemiLepSignalSel KinVars("KinVars","KinVars",jets_);

///to store all available current kinematic variables
std::map<std::string,float> vals_;



        vals_["sumEt"]=KinVars.sumEt();
        vals_["Et1"]=KinVars.Et1();
        vals_["lepeta"]=KinVars.lepeta();
        vals_["MET"]=KinVars.MET();
        vals_["dphiMETlepton"]=KinVars.dphiMETlepton();
        vals_["detajet2jet3"]=KinVars.detajet2jet3();
        vals_["detajet3jet4"]=KinVars.detajet3jet4();
        vals_["mindijetmass"]=KinVars.mindijetmass();
        vals_["maxdijetmass"]=KinVars.maxdijetmass();
        vals_["sphericity"]=KinVars.sphericity();
        vals_["aplanarity"]=KinVars.aplanarity();
        vals_["Et2"]=KinVars.Et2();
        vals_["Et3"]=KinVars.Et3();
        vals_["Eta1"]=KinVars.Eta1();
        vals_["Eta2"]=KinVars.Eta2();
        vals_["Eta3"]=KinVars.Eta3();
        vals_["dptjet1jet2"]=KinVars.dptjet1jet2();
        vals_["dptjet1jet3"]=KinVars.dptjet1jet3();
        vals_["djet1jet2pt"]=KinVars.djet1jet2pt();
        vals_["detajet1jet2"]=KinVars.detajet1jet2();
        vals_["dthetajet1jet2_boost"]=KinVars.dthetajet1jet2_boost();
        vals_["dphijet1jet2_boost"]=KinVars.dphijet1jet2_boost();
        vals_["dphijet1jet2"]=KinVars.dphijet1jet2();
        vals_["dphijet2jet3"]=KinVars.dphijet2jet3();
        vals_["dphijet1jet3"]=KinVars.dphijet1jet3();
        vals_["Et2byEt1"]=KinVars.Et2byEt1();
        vals_["Et3byEt2"]=KinVars.Et3byEt2();
        vals_["Et3byEt1"]=KinVars.Et3byEt1();
        vals_["sphericity_boost"]=KinVars.sphericity_boost();


std::map<std::string,float *>::iterator it;

//cout<<"I'm "<<GetName()<<endl; 
for ( it=vars_.begin() ; it != vars_.end(); it++ )
{
std::string _variableName = (*it).first;
float * _variableVal = (*it).second;

* _variableVal = vals_[_variableName];

TH1 * _hist = 0;

if (_histos!=0)  _hist =  (TH1F* ) _histos->At(varindexes_[_variableName]);
if (_hist!=0){
 _hist->Fill(* _variableVal ,weight);
//std::cout<<"#"<<varindexes_[_variableName]<<" "<<_variableName<<" = "<< * _variableVal<<std::endl;

}


}

return;
}

TList * GetHistograms() { return _histos;}
void WriteHistograms() { if ( _histos!=0) _histos->Write();}

private:

TList * _histos;
std::string  mvaPath_ ;
std::vector<std::string>  mvaMethod_;

///to carry var values
std::map<std::string,float * > vars_;
///to carry var's index
std::map<std::string,int > varindexes_;

bool isOk_;

public:
        ClassDef(InputVariablesHistograms,2)


};

#endif

