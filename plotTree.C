///usage: root -l -q `ls *root` plotTree.C
///usage:
///usage: plot kinematical variables in 3 different regimes:
///usage: index 1 -- unweighted, index 2 -- weighted ,index 3 -- weighted with wider bins


#include <cstdlib>
#include <iostream>
#include <map>
#include <string>
#include <algorithm>
#include <vector>


#include "TFile.h"
#include "TTree.h"
#include "TString.h"


void plotTree()
{


///Suppoused name of tree
TString treeName="KinVars";
TTree *tree=0;

std::vector<std::string> variables;


for (Int_t j=0;j<gROOT->GetListOfFiles()->GetEntries();j++)
{
         ((TFile*) gROOT->GetListOfFiles()->At(j))->cd();
        if (!TString(gFile->GetName()).Contains("TMVA")) break;
}
// ((TFile*) gROOT->GetListOfFiles()->At(1))->cd();

   tree = (TTree *)gFile->Get(treeName);

	if (!tree) {std::cout<<"Can't extract tree from "<<gFile->GetName()<<std::endl; return ;}


	 TObjArray *branches = tree->GetListOfBranches();

///Let's fill variables_to_use
        for (Int_t jjj=0;jjj<tree->GetListOfBranches()->GetSize();jjj++)
        {
                TObject * obj = tree->GetListOfBranches()->At(jjj);
                if (obj) {
                std::string str(obj->GetName());
                variables.push_back(str);
                }
        }


int num=0;	

for (Int_t j=0;j<gROOT->GetListOfFiles()->GetEntries();j++)
{
         ((TFile*) gROOT->GetListOfFiles()->At(j))->cd();
	TString _fileName = gFile->GetName();
         if (TString(gFile->GetName()).Contains("TMVA")) continue;

	 tree = (TTree *)gFile->Get(treeName);
        if (!tree) continue;


	for (Int_t k=0;k<variables.size();k++)
	{
/*
		num++;
		if (num>1) break;
*/
		TString _cmd(variables[k]);

		if (_cmd.Contains("weight")) continue;


		_cmd+=TString(">>tmpth1");

		 tree->Draw(_cmd.Data());

		Float_t var;
		Float_t weight;
		 TH1F * tmpth1 =  (TH1F*)gDirectory->Get("tmpth1");

///Plotting the variable 
///Unweighted
TCanvas * canv1 = new TCanvas(Form("_can_%s_1",variables[k].c_str()),Form("_can_%s_1",variables[k].c_str()));
canv1->cd();
TString _nameHist = Form("_cp_%s_1",variables[k].c_str());
TH1F * tmpth1_1 = new TH1F(_nameHist,_nameHist,tmpth1->GetNbinsX(),tmpth1->GetXaxis()->GetXmin(),tmpth1->GetXaxis()->GetXmax());
_cmd=variables[k].c_str();
_cmd+=TString(">>")+_nameHist;
tree->Draw(_cmd);
tmpth1 =  (TH1F*)gDirectory->Get(_nameHist);
tmpth1->Draw();
canv1->SaveAs(TString(canv1->GetName())+TString(".eps"));

//delete tmpth1_1;

///Weighted 
TCanvas * canv2 = new TCanvas(Form("_can_%s_2",variables[k].c_str()),Form("_can_%s_2",variables[k].c_str()));
canv2->cd();
_nameHist = Form("_cp_%s_2",variables[k].c_str());
 tmpth1_1 = new TH1F(_nameHist,_nameHist,tmpth1->GetNbinsX(),tmpth1->GetXaxis()->GetXmin(),tmpth1->GetXaxis()->GetXmax());
_cmd=variables[k].c_str();
_cmd+=TString(">>")+_nameHist;
tree->Draw(_cmd,"weight");
tmpth1 =  (TH1F*)gDirectory->Get(_nameHist);
tmpth1->Draw();
canv2->SaveAs(TString(canv2->GetName())+TString(".eps"));

//delete tmpth1_1;


///Weighted, large binning
TCanvas * canv3 = new TCanvas(Form("_can_%s_3",variables[k].c_str()),Form("_can_%s_3",variables[k].c_str()));
canv3->cd();
_nameHist = Form("_cp_%s_3",variables[k].c_str());
 tmpth1_1 = new TH1F(_nameHist,_nameHist,tmpth1->GetNbinsX()/3,tmpth1->GetXaxis()->GetXmin(),tmpth1->GetXaxis()->GetXmax());
_cmd=variables[k].c_str();
_cmd+=TString(">>")+_nameHist;
tree->Draw(_cmd,"weight");
tmpth1 =  (TH1F*)gDirectory->Get(_nameHist);
tmpth1->Draw();
canv3->SaveAs(TString(canv3->GetName())+TString(".eps"));

//delete tmpth1_1;

	}
	

}


return;
}
