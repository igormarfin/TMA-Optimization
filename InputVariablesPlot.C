///usage:  ini ROOT528
///usage:  root -l -q  readtribn1.root readtribn2.root  InputVariablesPlot.C

///usage:
///usgae: plot normalized histograms of input variables
///usage:
///usage: the code is unsafe: all pointers are not released. This code works only as standalone code.
///usage: (must be not called by other functions or programs!)


#include "TCanvas.h"
#include "TH1.h"
#include "TList.h"
#include "TLegend.h"
#include "TGraph.h"
#include "TString.h"
#include "TSeqCollection.h"

TCanvas * canv=0;
TLegend * leg=0;
TList * lst=0;

int colors [] =
{
        kRed,
        kGreen,
        kMagenta,
        kYellow,
        kRed-2,
        kGreen-2,
        kMagenta-2,
        kYellow-2,

        kRed-7,
        kGreen-7,
        kMagenta-7,
        kYellow-7,

        kPink,
        kBlue,
        kCyan,
        kAzure,

        kPink-4,
        kBlue-4,
        kCyan-4,
        kAzure-4,
        kGreen+6,
        kMagenta+6
};

void DrawOdered(TCanvas * _canv, TLegend * _leg, TList * _lst, TGraph  _comb)
{
if (!(_canv && _leg && _lst)) return;

_canv->cd();


///Make Sorting
_comb.Sort(&TGraph::CompareY,kFALSE); ///descending on Y


Double_t * templPos = _comb.GetX();
bool _isOk=true; ///flag the histogram with the highest GetMaximum()

//cout<<"_comb.GetN() = "<<_comb.GetN()<<endl;


for (int k=0; k<_comb.GetN();k++)
{


TH1* _hist = (TH1*) _lst->At(templPos[k]);

if (_hist!=0) {
	
	if (_isOk) {
		_hist->Draw();
                _isOk=false;
	}
	
	  else            _hist->Draw("same");

}

_leg->Draw();

}

return;
}


void InputVariablesPlot()
{

TList * _files = gROOT->GetListOfFiles();

if (_files->GetSize()==0) return;

TFile * file0=0;
file0 = (TFile*)_files->At(0);

///prepare the list of what to print
///We suppouse that the 0 file contains some histograms and 
/// the sturctures of all files are the sames

TList * _keys =0;
if (file0) _keys =  file0->GetListOfKeys();

///Contains all histograms from file0
TList * _histos = new TList();


if (_keys)
for (int i=0; i<_keys->GetSize();i++)
{
//	cout<<_keys->At(i)->GetName()<<endl;
	TObject * _obj =  file0->Get(_keys->At(i)->GetName());
	if (_obj && _obj->IsA()->InheritsFrom(TH1::Class()) && TString(_keys->At(i)->GetName()).Contains("_cp_")) {
		_histos->Add(_obj);

	}


}



///contains only similar 'flavor/type' histos from all files
lst = new TList();


if (_histos->GetSize()>0)
///Loop over histos
for(int i=0; i<_histos->GetSize();i++) {

TGraph combined;

TH1 * _hist = 0;
//cout<<"# i "<<i<<endl;
_hist = (TH1 *)  _histos->At(i);
TString _oldname = _hist->GetName();


lst->Clear();

canv = new TCanvas(TString("canv_")+_oldname,TString("canv_")+_oldname);
leg = new TLegend(0.42,0.75,0.77,0.99);

TFile * _file =0;
_file = (TFile*) _files->At(0);



TString _label = _file->GetName();
_label.ReplaceAll(".root","");

///treatment of file0

_hist->SetLineColor((Color_t)colors[0]);
_hist->SetName( (_oldname + _label).Data());
if (_hist->Integral()!=0) _hist->Scale(1e0/_hist->Integral());

//cout<<"New name "<<_hist->GetName()<<endl;

combined.SetPoint(0,0,_hist->GetMaximum());
lst->Add(_hist);
leg->AddEntry(_hist,_label,"l");



///Loop over files exept first one
for(int j=1; j<_files->GetSize();j++)
{
//	cout<<"Size of list"<<lst->GetEntries() <<endl;

	 _file = (TFile*) _files->At(j);
	_label = _file->GetName();
	_label.ReplaceAll(".root","");
	_hist = (TH1 *)_file->Get(_oldname);

//cout<<"_label "<<_label<<endl;

	if (_hist) {

		_hist->SetName(_oldname + _label);
		_hist->SetLineColor(colors[j]);
		if (_hist->Integral()!=0) _hist->Scale(1e0/_hist->Integral());

//		cout<<"_hist->GetMaximum() = "<<_hist->GetMaximum()<<endl;
		combined.SetPoint(j,j,_hist->GetMaximum());
		lst->Add(_hist);
		leg->AddEntry(_hist,_label,"l");


	}
	
	


} /// for j

DrawOdered(canv, leg, lst, combined);


} ///for i


TSeqCollection * canvs = 0;
canvs = gROOT->GetListOfCanvases();

///Save figures
if (canvs)
for (int i=0; i<canvs->GetEntries(); i++) 
((TCanvas*)canvs->At(i))->SaveAs(TString(canvs->At(i)->GetName())+TString(".eps"));



return;
}
