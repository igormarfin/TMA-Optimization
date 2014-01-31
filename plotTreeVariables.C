
///usage
///usage  simple way to plot some variable with weight (default value of variable is -1e10, that's why Pt1_b>-1e9)
///usage	
///usage	 TTree *tree1 = (TTree *)_file0->Get("KinVars1");
///usage	 tree1->Draw("Pt1_b","weight*(Pt1_b>-1e9)")
///usage
///usage
///usage
///usage
///usage: root -l -q `ls *root` plotTreeVariables.C
///usage: root -l readtribn.root 'plotTreeVariables.C("KinVars0","plot.xml",kTRUE,"E1 Sumw2")'
///usage
///usage   root -l theMergeList-pythia_bEnriched_150_v2.root theMergeList-pythia_bEnriched_30_50_v2.root theMergeList-pythia_bEnriched_50_150_v2.root  theMergeList-SUSYBBHToBB_M-120_7TeV-pythia6-tauola.root 'plotTreeVariables.C("KinVars0","plot2.xml",kTRUE)'
///usage
///usage Test btag-offline (tree #2) weight
///usage  root -l readtribn.root 'plotTreeVariables.C("KinVars2","plot2.xml",kTRUE,"NoLegend-Sumw2|BOX","2dplot.xml")'

///usage: how to plot combined qcd, signal and data:
///usage: root -l `ls the*bEnr*root` `ls the*SUSY*M-120*root` `ls *data*root` 'plotTreeVariables.C("KinVars5","plot.xml",kFALSE,"Sumw2 NoLegend| |0,1,2","")'
///usage:
///usage:
///usage:
#define SUMW2 "Sumw2" ///usage: optionns of ploting
#define NOLEGEND "NoLegend" ///usage: optionns of ploting
#define STANDALONELEGEND "StandAloneLegend" ///usage: optionns of ploting

#define WEIGHT_BINS 100 ///usage: options to plot weight 2d histograms
#define WEIGHT_MIN 0 ///usage: options to plot weight 2d histograms
//#define WEIGHT_MAX 0.0004 ///usage: options to plot weight 2d histograms
//#define WEIGHT_MAX 0.004 ///usage: options to plot weight 2d histograms
#define WEIGHT_MAX 0.6 ///usage: options to plot weight 2d histograms


///usage: 
///usage: How to combine (merge) different contributions?
///usage: 
///usage: TChain a(a);
///usage: a.Add(theMergeList-pythia_bEnriched_30_50_v2.root/KinVars0)
///usage: a.Add(theMergeList-pythia_bEnriched_50_150_v2.root/KinVars0)
///usage: a.Add(theMergeList-pythia_bEnriched_150_v2.root/KinVars0)
///usage: TH1F * pt2B = new TH1F(pt2B,pt2B,100,0,200)
///usage: TH1F * pt2S = new TH1F(pt2S,pt2S,100,0,200)
///usage: TFile *file0 = TFile::Open(theMergeList-SUSYBBHToBB_M-120_7TeV-pythia6-tauola.root)
///usage: TTree *tree0 = (TTree *) file0->Get(KinVars0); /// Sgn
///usage: a.Draw(Pt2>>pt2B,weight*(Pt2>-1e9));
///usage: Double_t intPt2 = pt2B->Integral();
///usage: tree0->Draw(Pt2>>pt2S,weight*(Pt2>-1e9))
///usage: Double_t intPt2S = pt2S->Integral()
///usage: pt2B->SetLineColor(kRed) 
///usage: pt2S->SetLineColor(kBlue)
///usage: pt2B->Draw()
///usage: pt2S->Draw(same)
///usage: Double_t intPt2 = pt2B->Integral()
///usage: Double_t intPt2S = pt2S->Integral()
///usage: pt2B->Scale(1e0/intPt2)
///usage: pt2S->Scale(1e0/intPt2S)
///usage: pt2B->Draw()
///usage: pt2S->Draw(same)

#include <cstdlib>
#include <iostream>
#include <map>
#include <string>
#include <algorithm>
#include <vector>
#include <fstream>

#include "TFile.h"
#include "TTree.h"
#include "TString.h"
#include "TH1F.h"
#include "TObjArray.h"

///from utils.h --> text processing support
#include "field.C.h"
#include "findLine.C.h"


#include <map>
#include <string>


int colors [] =
{
        kRed,
        kGreen,
        kMagenta,
        kBlue,
        kRed-2,
        kGreen-2,
        kMagenta-2,
        kYellow-2,
        kRed+3,
        kGreen+3,
        kMagenta+3,
        kYellow+3,
	kSpring+3,
	kSpring-9,
	kCyan +1,
	kCyan -7,
	kViolet-2,
	kViolet+4,
	kOrange+1,
	kOrange-2,
	kPink-9


};


 TH2F *_hist2=0;

///usage: options carries several values:
///usage: 1st -- options for plotTreeVariables script 
///usage: 2nd -- options for Draw method 
///usage: 3rd  -- options to combine
///usage:  
///usage: second position in aaa|bbb|ccc --> Sumw2|E1 histname|1,2,3 5,7,8
///usage: 3rd | --- 1,2,3 root ntuples will be combined, 5,7,8 -- will be combined


///usage: 
///usage: Example of combining:
///usage:  root -l theMergeList-pythia_bEnriched_150_v2.root theMergeList-pythia_bEnriched_30_50_v2.root  theMergeList-SUSYBBHToBB_M-120_7TeV-pythia6-tauola.root theMergeList-SUSYBBHToBB_M-90_7TeV-pythia6-tauola.root 
///usage: 'plotTreeVariables.C("KinVars4","plot22.xml",kFALSE,"Sumw2|E1|0,1 2,3")'
///usage: 
///usage: 
///usage: 
///usage: Example of combining for 2d histograms:
///usage: root -l theMergeList-pythia_bEnriched_150_v2.root theMergeList-pythia_bEnriched_30_50_v2.root  theMergeList-SUSYBBHToBB_M-120_7TeV-pythia6-tauola.root theMergeList-SUSYBBHToBB_M-90_7TeV-pythia6-tauola.root 
///usage: 'plotTreeVariables.C("KinVars4","plot22.xml",kFALSE,"Sumw2|LEGO|0,1 2,3","2dplot23.xml")'
///usage: 
///usage: 
///usage: How to plot at different canvases:
///usage: root -l `ls the*bEnr*root` `ls the*SUSY*M-120*root` 'plotTreeVariables.C("KinVars1","plot.xml",kFALSE,"Sumw2 | Hist |0,1,2","",kTRUE)'
///usage: 
///usage:  How to plot distributions for different flavor composition
///usage:  root -l `ls the*bEnr*root`  'plotTreeVariables.C("KinVars1","plot2.xml",kFALSE,"Sumw2 StandAloneLegend| Hist |0,1,2","",kFALSE,"qq")'
///usage: 
///usage:  How to plot THStack, indx is a key word indicating index of histogram. For example,all histograms with   "indx>0" will be combined in THStack
///usage:  root -l `ls the*bEnr*root`  'plotTreeVariables.C("KinVars1","plot2.xml",kFALSE,"Sumw2 StandAloneLegend| Hist |0,1,2","",kFALSE,"qq"," indx>0")'
///usage: 
///usage: how to plot data, and MC stack
///usage: root -l `ls the*bEnr*root` `ls the*SUSY*M-*root` `ls the*data*root` 'plotTreeVariables.C("KinVars5","plot2.xml",kFALSE,"Sumw2 StandAloneLegend| Hist |0,1,2","",kFALSE,"","indx>-1 && indx<4","")'
///usage: 
///usage: how to write to root file
///usage:  root -l `ls the*bEnr*root` `ls the*SUSY*M-*root`  'plotTreeVariables.C("KinVars6","plot2.xml",kTRUE,"Sumw2 StandAloneLegend| Hist |0,1,2","",kFALSE,"","","out.root")'

///usage: rescent example:
///usage: hadd bEnrichQCD.root `find ../trees_for_training -iname "*update*" | grep "QCD"`
///usage: hadd SUSY.root `find ../trees_for_training -iname "*update*" | egrep  ".*M-100.*|.*M-140.*|.*M-300.*"`
///usage: root -l bEnrichQCD.root SUSY.root 'plotTreeVariables.C("KinVarsBDT","plot.xml",kTRUE, "Sumw2 StandAloneLegend| Hist ")'



///usage: decomposition function : 'bbb' --> 0 etc

TString  _FlavInt2Content(int flav) ///usage:
{

std::map<std::string,int> _codes2;

_codes2["b"] = 0;
_codes2["c"] = 1;
_codes2["q"] = 2;

      TString _res="";

  for (std::map<std::string,int>::iterator it1 =  _codes2.begin(); it1 != _codes2.end(); it1++)
{
  for (std::map<std::string,int>::iterator it2 = _codes2.begin(); it2 != _codes2.end(); it2++)
{
  for (std::map<std::string,int>::iterator it3 =  _codes2.begin(); it3 != _codes2.end(); it3++)
{


   TString      _str=TString(it1->first)+TString(it2->first)+TString(it3->first);

	
        int _code = 3*3*it1->second + 3*it2->second + 1*it3->second;

	if (_code == flav) {
	 _res = _str ;

	}

}
}
}

return _res;
}



///usage: some function to convert name of the flavor content to numeric code:
///usage: bbb --> 000, bbc --> 1, bbq --> 2 etc
///usage: might be called to obtain a list of combinations:
///usage:  echo "gROOT->ProcessLine(\" .L plotTreeVariables.C \");  _FlavContent2Int(\"qq\")" | root -l  | head -1

///usage: flav might be 'bbb', 'qq','c' etc 
std::vector<int> _FlavContent2Int(TString flav) ///usage: 
{ 

std::vector<int> res;
if (flav.Length() ==0 ) return res;


std::map<std::string,int> _codes;

_codes["b"] = 0;
_codes["c"] = 1;
_codes["q"] = 2;

TString _resstr="";


  for (std::map<std::string,int>::iterator it1 =  _codes.begin(); it1 != _codes.end(); it1++) 
{
  for (std::map<std::string,int>::iterator it2 = _codes.begin(); it2 != _codes.end(); it2++) 
{
  for (std::map<std::string,int>::iterator it3 =  _codes.begin(); it3 != _codes.end(); it3++) 
{

	TString _str="";
	_str=TString(it1->first)+TString(it2->first)+TString(it3->first);

	int _code = 3*3*it1->second + 3*it2->second + 1*it3->second;





bool _isFound = false;
TString _str2 = _str;

	 if (_str2.Contains(flav)) _isFound=true;
	 if (flav.Length()==2)
	{
		for (int ii=0;ii<flav.Length();ii++) {

		int indx = _str2.Index(flav[ii]);


		if (indx <0) break;
	        _str2.Replace(_str2.Index(flav[ii]),1,"");
		}

		if (_str2.Length()==1) _isFound=true;


	}



	if (_isFound) {

	_resstr += Form("%d,",_code);
	res.push_back(_code);

	}



}
}
}

 
_resstr.Chop();

cout<<_resstr<<endl;


return res;

}



///usage:    
void plotTreeVariables(TString treeName="KinVars1",TString what_to_plot="",Bool_t norm=kTRUE,TString options="E1 Sumw2",TString plot2D="",Bool_t _isManyCanvas=kFALSE, TString _flavCompos="", TString _stack="",TString _save2root="") ///usage:

{

TTree *tree=0;
std::vector<std::string> variables;
std::vector<int> bins;
std::vector<double> maxs;
std::vector<double> mins;
std::vector<std::string> names;


///Support for combinning

TList *_allcombin=0x0;
TList *_currentcombin=0x0;
std::vector<int> _flavs = _FlavContent2Int(_flavCompos);
TList * _flavsTH1=0x0;
//if (_flavs.size()>0) _flavsTH1 = new TList();



TObjArray * _opt_2 = options.Tokenize(TString('|'));
if (_opt_2->GetEntries()>2) {
TString _opt_str_2 = _opt_2->At(2)->GetName(); ///3rd position in aaa|bbb|ccc --> Sumw2|E1 histname|1,2,3 4,5,6

TObjArray * _opt_3 = _opt_str_2.Tokenize(TString(' '));
for (Int_t ii=0;ii<_opt_3->GetEntries();ii++)
{
	TString _opt_str_3 = _opt_3->At(ii)->GetName();
	TObjArray * _opt_4 = _opt_str_3.Tokenize(TString(','));
	if (_opt_4->GetEntries()>1) {
		_currentcombin = new TList(); _currentcombin->SetOwner(kTRUE);
		for (Int_t jj=0;jj<_opt_4->GetEntries();jj++){
			TString strNum = _opt_4->At(jj)->GetName();
			_currentcombin->Add(new TObjString(((TFile*) gROOT->GetListOfFiles()->At(strNum.Atoi()))->GetName()));

		} //jj


if (_allcombin==0 ) _allcombin = new TList();

	} //if >1

if (_currentcombin && _allcombin) _allcombin->Add(_currentcombin);
if (_currentcombin) _currentcombin=0x0;


} ///ii

} //if opt_2

if (_currentcombin) _currentcombin->SetOwner(kTRUE);

if (gROOT->GetListOfFiles()->GetEntries()==0) return;

for (Int_t j=0;j<gROOT->GetListOfFiles()->GetEntries();j++)
{
         ((TFile*) gROOT->GetListOfFiles()->At(j))->cd();
	TString _name = gFile->GetName();
	_name.ReplaceAll(".root","");
	_name.ReplaceAll("theMergeList-","");
	_name.ReplaceAll("_v2","");
	_name.ReplaceAll("-pythia6-tauola","");
	_name.ReplaceAll("_7TeV","");
	

	 names.push_back(std::string(_name.Data()));

}

std::vector<std::string> variables1;
std::vector<std::string> variables2;


///Support  for 2D plotting 
if ( plot2D.Length()>0)
{

ifstream f(plot2D);

TString str;
str.ReadLine(f);
while (str.Length()>0 )
{
TObjArray * arr1 = str.Tokenize(TString('|'));
if (arr1->GetEntries()==2) {
variables1.push_back(std::string(arr1->At(0)->GetName()));
variables2.push_back(std::string(arr1->At(1)->GetName()));

//cout<<arr1->At(0)->GetName()<<"\n";
//cout<<arr1->At(1)->GetName()<<"\n";


}
str.ReadLine(f);
}


}



/**

if (plot_together.Length()>0)
{
ifstream f(plot_together);
TString str;
str.ReadLine(f);

while (str.Length()>0 )

}

**/

if (what_to_plot.Length()>0)
{
/*
ifstream f(what_to_plot);

///Read first line
str.ReadLine(f);


while (str.Length()>0 )
variables.push_back( std::string(str.Data()));
*/

TString Path_="";
TObjArray* arr = what_to_plot.Tokenize("/");
for(int i=0;i<arr->GetEntries()-1;i++) Path_+=TString("/")+arr->At(i)->GetName();

if (Path_.Length()==0) Path_=".";
TString res=findLine("Variable","NVar",what_to_plot,TString(Path_) + "/");
res.ReplaceAll("<"," ");  res.ReplaceAll("="," ");
res.ReplaceAll(">"," "); res.ReplaceAll("\""," ");
res=field(TString("\"")+res+TString("\""),"3",TString(Path_) + "/");
Int_t nVars=res.Atoi();


TString name=findLine("Variable","VarIndex",what_to_plot,TString(Path_) + "/");
name.ReplaceAll("<"," ");  name.ReplaceAll("="," ");  name.ReplaceAll(">"," ");
name.ReplaceAll("\""," ");
name=field(TString("\"")+name+TString("\""),"5",TString(Path_) + "/");
name.ReplaceAll("\n"," ");



TString max=findLine("Variable","VarIndex",what_to_plot,TString(Path_) + "/");
max.ReplaceAll("<"," ");  max.ReplaceAll("="," ");  max.ReplaceAll(">"," ");
max.ReplaceAll("\""," ");
max=field(TString("\"")+max+TString("\""),"13",TString(Path_) + "/");
max.ReplaceAll("\n"," ");

TString min=findLine("Variable","VarIndex",what_to_plot,TString(Path_) + "/");
min.ReplaceAll("<"," ");  min.ReplaceAll("="," ");  min.ReplaceAll(">"," ");
min.ReplaceAll("\""," ");
min=field(TString("\"")+min+TString("\""),"11",TString(Path_) + "/");
min.ReplaceAll("\n"," ");

TString bin=findLine("Variable","VarIndex",what_to_plot,TString(Path_) + "/");
bin.ReplaceAll("<"," ");  bin.ReplaceAll("="," ");  bin.ReplaceAll(">"," ");
bin.ReplaceAll("\""," ");
bin=field(TString("\"")+bin+TString("\""),"9",TString(Path_) + "/");
bin.ReplaceAll("\n"," ");

for (int i=0;i<nVars;i++)
{
TString varNum=Form("%d",i+1);
TString name2=name;	
TString max2=max;	
TString min2=min;	
TString bin2=bin;	


min2=field(TString("\"")+min2+TString("\""),varNum,Path_ + "/");
max2=field(TString("\"")+max2+TString("\""),varNum,Path_ + "/");
bin2=field(TString("\"")+bin2+TString("\""),varNum,Path_ + "/");
name2=field(TString("\"")+name2+TString("\""),varNum,Path_ + "/");



variables.push_back( std::string(name2.Data()));
bins.push_back(bin2.Atoi());
maxs.push_back(max2.Atof());
mins.push_back(min2.Atof());





}

}
else {


	gFile->cd();
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
		cout<<"varaible = "<<variables.back()<<endl;
                }
        }


}


if (plot2D.Length()==0)
for (Int_t k=0;k<variables.size();k++)
{

		

	 TString _cmd(variables[k]);
         if (_cmd.Contains("weight")) continue;

	
	      Float_t * var =new Float_t();
              Float_t weight;
	      Float_t _flavor;

bool mm=true;
TList * lst = new TList();
TGraph _combined;

Int_t nfiles = gROOT->GetListOfFiles()->GetEntries();
Int_t nCount=0;

for (Int_t j=0;j<nfiles;j++)
{

//cout<<"j="<<j<<endl;

TString _histName;
tree =0;

bool _isFound=false;

///Check if it's merged with other ntuples

	if (_allcombin) {

bool _doTChain=false;


	for (Int_t ii=0;ii<_allcombin->GetEntries();ii++) {
	TList * _currentcombin = (TList*) _allcombin->At(ii);
	TString currentFile = ((TFile*) gROOT->GetListOfFiles()->At(j))->GetName();
//	cout<<"currentFile = "<<currentFile<<endl;
	TObjString * isFileHere = (TObjString *) _currentcombin->FindObject(currentFile);
	if (isFileHere) {
		_isFound=true;
		Int_t _indx = _currentcombin->IndexOf(isFileHere);
//		cout<<"Indx = "<<_indx<<endl;
		if (_indx==0) _doTChain=true;	

	} ///if isFileHere  

if (_doTChain) {
_histName = _cmd + TString("_")+TString(names[j]);
//	cout<<"_histName = "<<_histName<<endl;
	TChain * a = new TChain("a");
	for (Int_t jj=0;jj<_currentcombin->GetEntries();jj++) {
		TObjString * _ntupleName = (TObjString *) _currentcombin->At(jj);
		TString _dir = _ntupleName->GetName();
		_dir+=TString("/")+treeName;
		a->Add(_dir);

		cout<<"I'm adding "<<_dir<<endl;

		} //for jj

	tree = a;
//	cout<<"tree0 = "<<tree<<endl;

	_doTChain=false;

} //if doTChain	

	} //for ii

	} //if  _allcombin




if (tree==0 && !_isFound) {
	 ((TFile*) gROOT->GetListOfFiles()->At(j))->cd();	
	tree = (TTree *)gFile->Get(treeName);
	 _histName=_cmd + TString("_")+TString(names[j]);

}
      
if (tree==0) continue;

	tree->SetBranchAddress(variables[k].c_str(),var);
	tree->SetBranchAddress("weight",&weight);

if (_flavs.size()>0) tree->SetBranchAddress("flav_cont", &_flavor);

	TH1F * _hist=0;

//cout<<"tree2 = "<<tree<<endl;



	if ( bins.size()>0 ) 
	{
//		cout<<_histName<<endl;
//		cout<<maxs[k]<<endl;
		_hist= new TH1F(_histName,_histName,bins[k],mins[k],maxs[k]);	


if (_flavs.size()>0)
{
_flavsTH1 = new TList();

for (int ijk = 0; ijk<_flavs.size();ijk++) {
TString _contFlav = _FlavInt2Content(_flavs[ijk]);
_flavsTH1->Add(  new TH1F(Form("%s_%s",_histName.Data(),_contFlav.Data()), Form("%s_%s",_histName.Data(),_contFlav.Data()) ,bins[k],mins[k],maxs[k]) );

}
}





	} else {
		TString _tmpName= TString("tmpth")+Form("%d",j);

		TString _cmd2 =_cmd+TString(">>")+_tmpName;
		  tree->Draw(_cmd2.Data());
		  TH1F * tmpth1 =  (TH1F*)gDirectory->Get(_tmpName);
					
		if (tmpth1)
		_hist = new TH1F(_histName,_histName,tmpth1->GetNbinsX(),tmpth1->GetXaxis()->GetXmin(),tmpth1->GetXaxis()->GetXmax());


	}

if (options.Contains(SUMW2)) 
if (_hist) _hist->Sumw2();

	
for (int k2=0;k2<tree->GetEntries();k2++) {
tree->GetEntry(k2);
if (_hist) _hist->Fill(*var,weight);

if (_flavsTH1) {
for (int ijk =0; ijk<_flavsTH1->GetEntries();ijk++) {

TH1 * _hist_fl = (TH1 *)_flavsTH1->At(ijk);

int indx1 =_flavs[ijk];
int indx2 =_flavor;

if (indx1 == indx2) _hist_fl->Fill(*var,weight);



} ///for ijk
} ///if 

}	

if (_hist) {

if (norm) if (_hist->Integral()>0) _hist->Scale(1e0/_hist->Integral());
lst->Add(_hist) ;

_combined.SetPoint(nCount,nCount,_hist->GetMaximum());
//cout<<"!!!!!! "<<j<<" !!! "<<_hist->GetName()<<" "<<_hist->GetMaximum()<<endl;
nCount++;


}


if (_flavsTH1) 
for (int ijk =0; ijk<_flavsTH1->GetEntries();ijk++) {

TH1 * _hist_fl = (TH1 *)_flavsTH1->At(ijk);


if (norm) if (_hist_fl->Integral()>0) _hist_fl->Scale(1e0/_hist_fl->Integral());
lst->Add(_hist_fl) ;

_combined.SetPoint(nCount,nCount,_hist_fl->GetMaximum());
//cout<<"!!!!!! "<<j<<" !!! "<<_hist->GetName()<<" "<<_hist->GetMaximum()<<endl;
nCount++;

}


if (_hist) _hist->SetLineColor(colors[j]);
if (_hist && TString(_hist->GetName()).Contains("data")) _hist->SetLineColor(kBlack);

if (_flavsTH1)
for (int ijk =0; ijk<_flavsTH1->GetEntries();ijk++) {
TH1 * _hist_fl = (TH1 *)_flavsTH1->At(ijk);

 _hist_fl->SetLineColor(colors[nCount - ijk]);

}


/*
if (mm) {
_hist->Draw();
mm=false;
} else _hist->Draw("same");
*/

///leg->AddEntry(_hist,names[j].c_str(),"l");

} ///for  over files

///Make Sorting
_combined.Sort(&TGraph::CompareY,kFALSE); ///descending on Y
Double_t * templPos = _combined.GetX();



TObjArray * _opt = options.Tokenize(TString('|'));
TString _opt_str = _opt->At(1)->GetName(); ///second position in aaa|bbb|ccc --> Sumw2|E1 histname

Int_t CanvNum=0;

THStack * _stck = 0x0;

if (_stack.Length()>0) {
_stck = new THStack(Form("_stack_%s_%d",variables[k].c_str(),CanvNum),Form("%s",variables[k].c_str()) );
for (int ii=0; ii<_combined.GetN();ii++) {

int indx = (int) templPos[ii];

TString _tmpString1 = _stack;
TString _tmpString2 =Form("%d",indx);
_tmpString1.ReplaceAll("indx",_tmpString2.Data());


bool _isgood = (bool) gROOT->ProcessLine(_tmpString1.Data());

if (_isgood) {

cout<<"I'm adding to stack:  "<<lst->At(indx)->GetName()<<endl;
((TH1*)lst->At(indx))->SetFillColor(((TH1 *)lst->At(indx))->GetLineColor());
 _stck->Add((TH1*) lst->At(indx));

} ///if

} ///for


} //if


TCanvas * canv = new TCanvas(Form("_can_%s_%d",variables[k].c_str(),CanvNum),Form("_can_%s",variables[k].c_str()));
TLegend * leg = new TLegend(0.4,0.6,0.89,0.89);
canv->cd();


TH1 * dataHist=0x0;




if ( TString(lst->At(templPos[0])->GetName()).Contains("data")) {

dataHist = (TH1*) lst->At(templPos[0]);

TString optt="E1";
if (!_stck || !_stck->GetHists()->FindObject(lst->At(templPos[0])))
lst->At(templPos[0])->Draw(optt);
else 
_stck->Draw(optt);
} else  {
if (!_stck || !_stck->GetHists()->FindObject(lst->At(templPos[0])))
lst->At(templPos[0])->Draw(_opt_str);
else
_stck->Draw(_opt_str);
 }

leg->AddEntry(lst->At(templPos[0]),lst->At(templPos[0])->GetName(),"l");

if (_save2root.Length()>0 ){
TFile * _outroot =  TFile::Open(_save2root.Data(),"UPDATE");
lst->At(templPos[0])->Write(treeName+TString(lst->At(templPos[0])->GetName()));
_outroot->Close();
}


canv->Update();
canv->Modified();


if (_isManyCanvas)
{
if (!( options.Contains(NOLEGEND) || options.Contains(STANDALONELEGEND) )) leg->Draw();
canv->SaveAs(TString(canv->GetName())+TString(".eps"));
}



cout<<"_combined.GetN()= "<<_combined.GetN()<<endl;

for (int ii=1; ii<_combined.GetN();ii++) {

TString _same=" same ";

if (_isManyCanvas)
{
CanvNum++;
canv = new TCanvas(Form("_can_%s_%d",variables[k].c_str(),CanvNum),Form("_can_%s",variables[k].c_str()));
leg = new TLegend(0.4,0.6,0.89,0.89);
canv->cd();

_same="";
}


cout<<"templPos[ii] = "<<templPos[ii]<<endl;

if ( TString(lst->At(templPos[ii])->GetName()).Contains("data")) {


dataHist = (TH1*) lst->At(templPos[ii]);


TString optt="E1";
if (!_stck || !_stck->GetHists()->FindObject(lst->At(templPos[ii])) ) lst->At(templPos[ii])->Draw(optt+_same);
else  _stck->Draw(optt+_same);

} else {


if (!_stck || !_stck->GetHists()->FindObject(lst->At(templPos[ii]))) lst->At(templPos[ii])->Draw(_opt_str+_same);
else  _stck->Draw(_opt_str+_same);

}

leg->AddEntry(lst->At(templPos[ii]),lst->At(templPos[ii])->GetName(),"l");



if (_save2root.Length()>0 ){
TFile * _outroot =  TFile::Open(_save2root.Data(),"UPDATE");
lst->At(templPos[ii])->Write(treeName+TString(lst->At(templPos[ii])->GetName()));
_outroot->Close();
}




canv->Update();
canv->Modified();

if (_isManyCanvas)
{

if (!( options.Contains("NoLegend") || options.Contains("StandAloneLegend") )) leg->Draw();
canv->SaveAs(TString(canv->GetName())+TString(".eps"));

}





}


if (dataHist) dataHist->Draw("E1 same");

if (!_isManyCanvas)
{

if (!( options.Contains(NOLEGEND) || options.Contains(STANDALONELEGEND) )) leg->Draw();

canv->SaveAs(TString(canv->GetName())+TString(".eps"));
//canv->SaveAs(TString(canv->GetName())+TString(".jpg"));
}


if (options.Contains(STANDALONELEGEND)) 
{
canv = new TCanvas(Form("_legend_%s_%d",variables[k].c_str()),"Legend");
leg->Draw();
canv->SaveAs(TString(canv->GetName())+TString(".eps"));	
}

} ///for over variables




///2D plotting
if (plot2D.Length()>0)
for (Int_t k=0;k<variables1.size();k++)
{

std::string _strvar1 = variables1[k];
std::string _strvar2 = variables2[k];



///Try to find var1 and var2 in variables
std::vector<std::string>::iterator it1;
std::vector<std::string>::iterator it2;
it1 = std::find(variables.begin(),variables.end(),_strvar1);

int pos1 = -1;
int pos2 = -1;


if (it1 == variables.end()) {
if (!(TString(_strvar1).Contains("weight") ) ) {
cout<<endl;
continue;
} 
} else   pos1 = it1-variables.begin();


it2 = std::find(variables.begin(),variables.end(),_strvar2);


if (it2 == variables.end()) {
if (!(TString(_strvar2).Contains("weight")) ) {
cout<<endl;
continue;
} 
} else   pos2 = it2-variables.begin();







// Float_t * _var1 =new Float_t();
// Float_t * _var2 =new Float_t();

Float_t  _var1;
Float_t  _var2;



TList * lst = new TList();
TGraph _combined;

 Float_t weight=1e0;

TString _cmd = TString(_strvar1) + "_" + TString(_strvar2);
///cout<<_cmd<<endl;


Int_t nfiles = gROOT->GetListOfFiles()->GetEntries();
Int_t nCount=0;


///One canvas per file
TCanvas * canv = new TCanvas(Form("_can_%s_%s",_strvar1.c_str(),_strvar2.c_str()),Form("_can_%s_%s",_strvar1.c_str(),_strvar2.c_str()));
TLegend * leg = new TLegend(0.4,0.6,0.89,0.89);
canv->cd();




for (Int_t j=0;j<nfiles;j++)
{

//cout<<"j= "<<j<<endl;

TString _histName;
tree =0;
bool _isFound=false;

        if (_allcombin) {

bool _doTChain=false;


        for (Int_t ii=0;ii<_allcombin->GetEntries();ii++) {
        TList * _currentcombin = (TList*) _allcombin->At(ii);
        TString currentFile = ((TFile*) gROOT->GetListOfFiles()->At(j))->GetName();
//      cout<<"currentFile = "<<currentFile<<endl;
        TObjString * isFileHere = (TObjString *) _currentcombin->FindObject(currentFile);
        if (isFileHere) {
                _isFound=true;
                Int_t _indx = _currentcombin->IndexOf(isFileHere);
//              cout<<"Indx = "<<_indx<<endl;
                if (_indx==0) _doTChain=true;   

        } ///if isFileHere  


if (_doTChain) {
_histName = _cmd + TString("_")+TString(names[j]);
//      cout<<"_histName = "<<_histName<<endl;
        TChain * a = new TChain("a");
        for (Int_t jj=0;jj<_currentcombin->GetEntries();jj++) {
                TObjString * _ntupleName = (TObjString *) _currentcombin->At(jj);
                TString _dir = _ntupleName->GetName();
                _dir+=TString("/")+treeName;
                a->Add(_dir);

//            cout<<"I'm adding "<<_dir<<endl;

                } //for jj

        tree = a;
	
      cout<<"tree : nEntries() = "<<tree->GetEntries()<<endl;

        _doTChain=false;

} //if doTChain 

        } //for ii

        } //if  _allcombin

if (tree==0 && !_isFound) {


  ((TFile*) gROOT->GetListOfFiles()->At(j))->cd();       
        tree = (TTree *)gFile->Get(treeName);
         _histName=_cmd + TString("_")+TString(names[j]);

}

      
if (tree==0) continue;

        tree->SetBranchAddress(_strvar1.c_str(),&_var1);
        tree->SetBranchAddress(_strvar2.c_str(),&_var2);
	if ( !(TString(_strvar1).Contains("weight") || TString(_strvar2).Contains("weight")) )
        tree->SetBranchAddress("weight",&weight);


	///variables must be in plot.xml



	cout<<_histName<<endl;

double maxweight = tree->GetMaximum("weight");
double minweight = tree->GetMinimum("weight");
double maximumVar=0.0;

	_hist2=0;
	if (pos1 >=0 && pos2>=0) {
	_hist2 = new TH2F(_histName,_histName,bins[pos1],mins[pos1],maxs[pos1],bins[pos2],mins[pos2],maxs[pos2]);
	maximumVar = tree->GetMaximum(_strvar2.c_str());
	}

	else if (pos1 >=0 &&  pos2<0) {
//	_hist2 = new TH2F(_histName,_histName,bins[pos1],mins[pos1],maxs[pos1],WEIGHT_BINS,WEIGHT_MIN,WEIGHT_MAX);
	_hist2 = new TH2F(_histName,_histName,bins[pos1],mins[pos1],maxs[pos1],WEIGHT_BINS,WEIGHT_MIN,maxweight*1.2);
	maximumVar = tree->GetMaximum("weight");

	}
	else if (pos2 >=0 &&  pos1<0) {
	_hist2 = new TH2F(_histName,_histName,WEIGHT_BINS,WEIGHT_MIN,maxweight*1.2,bins[pos2],mins[pos2],maxs[pos2]);
	maximumVar = tree->GetMaximum(_strvar2.c_str());

	}
	else continue;


if (options.Contains(SUMW2)) 
if (_hist2) _hist2->Sumw2();

for (int k2=0;k2<tree->GetEntries();k2++) {
tree->GetEntry(k2);
if (_hist2) {
/*
cout<<"var1 = "<<_var1<<endl;
cout<<"var2 = "<<_var2<<endl;
cout<<"weight = "<<weight<<endl;
*/

Double_t xmin = _hist2->GetXaxis()->GetXmin();
Double_t xmax = _hist2->GetXaxis()->GetXmax();
Double_t ymin = _hist2->GetYaxis()->GetXmin();
Double_t ymax = _hist2->GetYaxis()->GetXmax();

if (_var1 >= xmin && _var1<=xmax)
if (_var2 >= ymin && _var2<=ymax)
{
//cout<<"var1 = "<<_var1<<endl;
//cout<<"var2 = "<<_var2<<endl;
//cout<<"weight = "<<weight<<endl;
_hist2->Fill(_var1,_var2,weight);
} ///if var

} //if _hist2

} ///for k2


if (_hist2) {
 _hist2->SetLineColor(colors[j]);
leg->AddEntry(_hist2,names[j].c_str(),"l");

lst->Add(_hist2) ;
//cout<<"nCount,nCount,maximumVar ="<<nCount<<","<<maximumVar<<endl;
_combined.SetPoint(nCount,nCount,maximumVar);
nCount++;

}

/*
if (_hist2) {
_hist2->SetLineColor(colors[j]);
leg->AddEntry(_hist2,names[j].c_str(),"l");

TObjArray * _opt = options.Tokenize(TString('|'));
TString _opt_str = _opt->At(1)->GetName(); ///second position in aaa|bbb|ccc --> Sumw2|E1 histname
_hist2->Draw(_opt_str);
}


if (!options.Contains(NOLEGEND)) leg->Draw();
canv->SaveAs(TString(canv->GetName())+TString(".eps"));

*/
//delete _var1;
//delete _var2;


}/// over files

///Make Sorting
_combined.Sort(&TGraph::CompareY,kFALSE); ///descending on Y
Double_t * templPos = _combined.GetX();

TObjArray * _opt = options.Tokenize(TString('|'));
TString _opt_str = _opt->At(1)->GetName(); ///second position in aaa|bbb|ccc --> Sumw2|E1 histname

lst->At(templPos[0])->Draw(_opt_str);

//cout<<"GetN() "<<_combined.GetN()<<endl;
for (int ii=1; ii<_combined.GetN();ii++) {
//cout<<"templPos[ii] = "<<templPos[ii]<<endl;
lst->At(templPos[ii])->Draw(_opt_str+TString("same"));
}


if (!options.Contains("NoLegend")) leg->Draw();
canv->SaveAs(TString(canv->GetName())+TString(".eps"));
canv->SaveAs(TString(canv->GetName())+TString(".jpg"));


} ///over variables


return;
}

