#include <iostream>
#include <iomanip>
using std::cout;
using std::endl;

#include "tmvaglob.C"

#include "RQ_OBJECT.h"

#include "TH1.h"
#include "TROOT.h"
#include "TList.h"
#include "TIterator.h"
#include "TStyle.h"
#include "TPad.h"
#include "TCanvas.h"
#include "TLatex.h"
#include "TLegend.h"
#include "TLine.h"
#include "TH2.h"
#include "TFormula.h"
#include "TFile.h"
#include "TApplication.h"
#include "TKey.h"
#include "TClass.h"
#include "TGaxis.h"

#include "TGWindow.h"
#include "TGButton.h"
#include "TGLabel.h"
#include "TGNumberEntry.h"

#include "TMarker.h"

// this macro plots the signal and background efficiencies
// as a function of the MVA cut.

enum PlotType { EffPurity = 0 };

class MethodInfo : public TNamed {
public:
   MethodInfo() :
      methodName(""),
      methodTitle(""),
      sig(0),
      bgd(0),
      origSigE(0),
      origBgdE(0),
      sigE(0),
      bgdE(0),
      purS(0),
      purB(0),
//      sSig(0),
//      effpurS(0),
//      effpurB(0),
      canvas(0),
      line1(0),
      line2(0),
      rightAxis(0),
      maxSignificance(0),
	purB_(-1e0),
	_markersB(0),
	_textsB(0),
	_markersS(0),
	_textsS(0),
	effBdivS(0)
   {}
   virtual ~MethodInfo();

   TString  methodName;
   TString  methodTitle;
   TH1*     sig;
   TH1*     bgd;
   TH1*     origSigE;
   TH1*     origBgdE;
   TH1*     sigE;
   TH1*     bgdE;
   TH1*     purS, *purB;
   TH1*     purEffS, *purEffB;
   TList * _markersB;
   TList * _textsB;
   TList * _markersS;
   TList * _textsS;
   TH1 * effBdivS;
	
   
//   TH1*     sSig;    
//   TH1*     effpurS, *effpurB;
   TCanvas* canvas;
   TLatex*  line1;
   TLatex*  line2;
   TGaxis*  rightAxis;
   Double_t maxSignificance; 
   double purB_;	

   void SetResultHists() 
   {
      TString pname    = "purS_"         + methodTitle;
      TString epname   = "effpurS_"      + methodTitle;
      TString pnameB    = "purB_"         + methodTitle;
      TString epnameB   = "effpurB_"      + methodTitle;
      TString ssigname = "significance_" + methodTitle;

      TString pename    = "purEffS_"         + methodTitle;
      TString penameB    = "purEffB_"         + methodTitle;
      TString penameBS    = "EffBS_"         + methodTitle;


      sigE = (TH1*)origSigE->Clone("sigEffi");
      bgdE = (TH1*)origBgdE->Clone("bgdEffi");

///Calculate 'before-cut' efficiencies

  TH1 *    sigEUnity = (TH1*)origSigE->Clone("sigEffiUnity");
  TH1 *    bgdEUnity = (TH1*)origBgdE->Clone("bgdEffiUnity");

for (Int_t i=1; i<=sigEUnity->GetNbinsX();i++)sigEUnity->SetBinContent(i,1e0);
for (Int_t i=1; i<=bgdEUnity->GetNbinsX();i++)bgdEUnity->SetBinContent(i,1e0);


      TH1 * sigETemp = (TH1*)origSigE->Clone("sigEffiTemp");
      TH1 * bgdETemp = (TH1*)origBgdE->Clone("bgdEffiTemp");

sigE->Add(sigEUnity,sigETemp,1e0,-1e0);      
bgdE->Add(bgdEUnity,bgdETemp,1e0,-1e0);      

if (_markersB==0) _markersB = new TList();
if (_textsB==0) _textsB = new TList();
if (_markersS==0) _markersS = new TList();
if (_textsS==0) _textsS = new TList();




////END
      Int_t nbins = sigE->GetNbinsX();
      Double_t low = sigE->GetBinLowEdge(1);
      Double_t high = sigE->GetBinLowEdge(nbins+1);

//cout<<"nbins="<<nbins<<endl;
//cout<<"low="<<low<<endl;
//cout<<"high="<<high<<endl;

      purS    = new TH1F(pname, pname, nbins, low, high);
      purB    = new TH1F(pnameB, pnameB, nbins, low, high);
      purEffS    = new TH1F(pename, pename, nbins, 0., 1.);
      purEffB    = new TH1F(penameB, penameB, nbins, 0., 1.);
      effBdivS = new TH1F(penameBS, penameBS, nbins, 0., 1.);
//      sSig    = new TH1F(ssigname, ssigname, nbins, low, high);
//      effpurS = new TH1F(epname, epname, nbins, low, high);        
//      effpurB = new TH1F(epnameB, epnameB, nbins, low, high);        

      // chop off useless stuff
      sigE->SetTitle( Form(" \'Before-Cut\' efficiency versus purity for %s classifier", methodTitle.Data()) );
         
      // set the histogram style
      TMVAGlob::SetSignalAndBackgroundStyle( sigE, bgdE );
      TMVAGlob::SetSignalAndBackgroundStyle( purS, bgdE );
//      TMVAGlob::SetSignalAndBackgroundStyle( effpurS, bgdE );
      TMVAGlob::SetSignalAndBackgroundStyle(sigE, purB );
//      TMVAGlob::SetSignalAndBackgroundStyle(sigE, effpurB );

      TMVAGlob::SetSignalAndBackgroundStyle(sigE, purEffB );
	 TMVAGlob::SetSignalAndBackgroundStyle( purEffS, bgdE );

      sigE->SetFillStyle( 0 );
      bgdE->SetFillStyle( 0 );
      sigE->SetLineWidth( 3 );
      bgdE->SetLineWidth( 3 );

//      sSig->SetFillStyle( 0 );
//      sSig->SetLineWidth( 3 );
    effBdivS->SetFillStyle( 0 );
    effBdivS->SetLineWidth( 3 );
	effBdivS->SetLineColor(kGreen);

      // the purity and quality
      purS->SetFillStyle( 0 );
      purS->SetLineWidth( 2 );
      purS->SetLineStyle( 5 );
      purEffS->SetFillStyle( 0 );
      purEffS->SetLineWidth( 2 );
      purEffS->SetLineStyle( 5 );
//      effpurS->SetFillStyle( 0 );
//      effpurS->SetLineWidth( 2 );
//      effpurS->SetLineStyle( 6 );


      purB->SetFillStyle( 0 );
      purB->SetLineWidth( 2 );
      purB->SetLineStyle( 5 );
      purEffB->SetFillStyle( 0 );
      purEffB->SetLineWidth( 2 );
      purEffB->SetLineStyle( 5 );
//      effpurB->SetFillStyle( 0 );
//      effpurB->SetLineWidth( 2 );
//      effpurB->SetLineStyle( 6 );


   }

   ClassDef(MethodInfo,0)
};

MethodInfo::~MethodInfo() 
{
   delete sigE;
   delete bgdE;
   delete purS;
   delete purB;
   delete purEffS;
   delete purEffB;
//   delete sSig;
//   delete effpurS;
   if(gROOT->GetListOfCanvases()->FindObject(canvas))
      delete canvas;
}

class StatDialogMVAEffs {  

   RQ_OBJECT("StatDialogMVAEffs")
      
public:

   StatDialogMVAEffs(const TGWindow* p, Float_t ns, Float_t nb,Bool_t flag);
   virtual ~StatDialogMVAEffs();
   
   void SetFormula(const TString& f) { fFormula = f; }
   TString GetFormula();
   TString GetLatexFormula();
   
   void ReadHistograms(TFile* file);
//   void UpdateSignificanceHists();
   void DrawHistograms(TString outdir);

   void RaiseDialog() { if (fMain) { fMain->RaiseWindow(); fMain->Layout(); fMain->MapWindow(); } }

private:

   TGMainFrame *fMain;
   Float_t fNSignal;
   Float_t fNBackground;  
   TString fFormula;
   TList * fInfoList;
   Bool_t _batch;


   TGNumberEntry* fSigInput;
   TGNumberEntry* fBkgInput;

   TGHorizontalFrame* fButtons;
   TGTextButton* fDrawButton;
   TGTextButton* fCloseButton;

   Int_t maxLenTitle;

   void UpdateCanvases(TString outdir);
//	double purB_;

public:

   // slots
   void SetNSignal(); //SIGNAL
   void SetNBackground(); //SIGNAL
   void Redraw(); //SIGNAL
   void Close(); //SIGNAL

//   void SetBkgPurity(double purB) {purB_=purB; return;} 

   // result printing
   //   void PrintResults( const MethodInfo* info, double bkgPur=-1e0);

void CalculateHists();

};

void StatDialogMVAEffs::SetNSignal() 
{
   fNSignal = fSigInput->GetNumber();
}

void StatDialogMVAEffs::SetNBackground() 
{
   fNBackground = fBkgInput->GetNumber();
}


TString StatDialogMVAEffs::GetFormula() 
{
   TString f = fFormula;
   f.ReplaceAll("S","x");
   f.ReplaceAll("B","y");
   return f;
}



TString StatDialogMVAEffs::GetLatexFormula() 
{
   TString f = fFormula;
   f.ReplaceAll("(","{");
   f.ReplaceAll(")","}");
   f.ReplaceAll("sqrt","#sqrt");
   return f;
}


void StatDialogMVAEffs::Redraw() 
{
//   UpdateSignificanceHists();

//   cout<<"Redraw()"<<endl;
   CalculateHists();
   UpdateCanvases("plots");
}

void StatDialogMVAEffs::Close() 
{
   delete this;
}

StatDialogMVAEffs::~StatDialogMVAEffs() 
{
   if (fInfoList) { 
      TIter next(fInfoList);
      MethodInfo *info(0);
      while ( (info = (MethodInfo*)next()) ) {
         delete info;
      }
      delete fInfoList;
      fInfoList=0;
   }


   fSigInput->Disconnect();
   fBkgInput->Disconnect();
   fDrawButton->Disconnect();
   fCloseButton->Disconnect();

   fMain->CloseWindow();
   fMain->Cleanup();
   fMain = 0;
}


StatDialogMVAEffs::StatDialogMVAEffs(const TGWindow* p, Float_t ns, Float_t nb,Bool_t batch) :
   fNSignal(ns),
   fNBackground(nb),
   fFormula(""),
   fInfoList(0),
   fSigInput(0),
   fBkgInput(0),
   fButtons(0),
   fDrawButton(0),
   fCloseButton(0),
   maxLenTitle(0),
	_batch(batch)//,
//purB_(-1e0)
{
   UInt_t totalWidth  = 500;
   UInt_t totalHeight = 300;

	      if (_batch) {
            fNSignal=1000;
            fNBackground=1000;

        }

	
   // main frame
   if (!_batch) {

   fMain = new TGMainFrame(p, totalWidth, totalHeight, kMainFrame | kVerticalFrame);

   TGLabel *sigLab = new TGLabel(fMain,"Signal events");
   fMain->AddFrame(sigLab, new TGLayoutHints(kLHintsLeft | kLHintsTop,5,5,5,5));

   fSigInput = new TGNumberEntry(fMain, (Double_t) fNSignal,5,-1,(TGNumberFormat::EStyle) 5);
   fSigInput->SetLimits(TGNumberFormat::kNELLimitMin,0,1);
   fMain->AddFrame(fSigInput, new TGLayoutHints(kLHintsLeft | kLHintsTop,5,5,5,5));
   fSigInput->Resize(100,24);

   TGLabel *bkgLab = new TGLabel(fMain, "Background events");
   fMain->AddFrame(bkgLab, new TGLayoutHints(kLHintsLeft | kLHintsTop,5,5,5,5));

   fBkgInput = new TGNumberEntry(fMain, (Double_t) fNBackground,5,-1,(TGNumberFormat::EStyle) 5);
   fBkgInput->SetLimits(TGNumberFormat::kNELLimitMin,0,1);
   fMain->AddFrame(fBkgInput, new TGLayoutHints(kLHintsLeft | kLHintsTop,5,5,5,5));
   fBkgInput->Resize(100,24);

   fButtons = new TGHorizontalFrame(fMain, totalWidth,30);

   fCloseButton = new TGTextButton(fButtons,"&Close");
   fButtons->AddFrame(fCloseButton, new TGLayoutHints(kLHintsLeft | kLHintsTop));

   fDrawButton = new TGTextButton(fButtons,"&Draw");
   fButtons->AddFrame(fDrawButton, new TGLayoutHints(kLHintsRight | kLHintsTop,15));
  
   fMain->AddFrame(fButtons,new TGLayoutHints(kLHintsLeft | kLHintsBottom,5,5,5,5));

   fMain->SetWindowName("Significance");
   fMain->SetWMPosition(0,0);
   fMain->MapSubwindows();
   fMain->Resize(fMain->GetDefaultSize());
   fMain->MapWindow();

   fSigInput->Connect("ValueSet(Long_t)","StatDialogMVAEffs",this, "SetNSignal()");
   fBkgInput->Connect("ValueSet(Long_t)","StatDialogMVAEffs",this, "SetNBackground()");

   fDrawButton->Connect("Clicked()","TGNumberEntry",fSigInput, "ValueSet(Long_t)");
   fDrawButton->Connect("Clicked()","TGNumberEntry",fBkgInput, "ValueSet(Long_t)");
   fDrawButton->Connect("Clicked()", "StatDialogMVAEffs", this, "Redraw()");   

   fCloseButton->Connect("Clicked()", "StatDialogMVAEffs", this, "Close()");
	}
}

void StatDialogMVAEffs::UpdateCanvases(TString outputdir) 
{
   if (fInfoList==0) return;
   if (fInfoList->First()==0) return;
   MethodInfo* info = (MethodInfo*)fInfoList->First();
   if ( info->canvas==0 ) {
      DrawHistograms(outputdir);
      return;
   }

   TIter next2(fInfoList);
   TIter next(fInfoList);

	 while ( (info = (MethodInfo*)next2()) ) 
	if (info->canvas) delete info->canvas;	

	 DrawHistograms(outputdir);

   while ( (info = (MethodInfo*)next()) ) {
      info->canvas->Update();	
      cout<<"my formula"<<fFormula<<endl;
      if (fFormula=="B/S") { cout<<"formula"<<endl; info->rightAxis->SetWmax(6); }
      else   info->rightAxis->SetWmax(1.1*info->maxSignificance);
      info->canvas->Modified(kTRUE);
      info->canvas->Update();
      info->canvas->Paint();
   }
}

void StatDialogMVAEffs::CalculateHists()
{

cout<<"fInfoList = "<<fInfoList<<endl;

   TIter next(fInfoList);
   MethodInfo* info(0);

TFormula f("ffff",GetFormula());



while (   info = (MethodInfo*)next() ) {

cout<<"info="<<info<<endl;
cout<<"info="<<info->Class_Name()<<endl;

if ( info->_markersB &&  info->_textsB && info->_markersS &&  info->_textsS )
{

delete info->_markersB;
info->_markersB = new TList();  
delete info->_markersS;
info->_markersS = new TList();  

delete info->_textsB;
info->_textsB = new TList();  
delete info->_textsS;
info->_textsS = new TList();  
}


/*
const int _nPoints=50;
int _nBins = info->origSigE->GetNbinsX();
int _nPointBin = (_nBins>=_nPoints)? _nBins/_nPoints:_nBins/4;
*/

double _deltaPurB=0.05;
double _prevPurB=-10;

if (fNSignal/fNBackground >=10 || fNBackground/fNSignal>=10) _deltaPurB/=10;
if (fNSignal/fNBackground >=100 || fNBackground/fNSignal>=100) _deltaPurB/=100;


      for (Int_t i=1; i<=info->origSigE->GetNbinsX(); i++) {

	double _disc = info->sigE->GetBinCenter(i);
         Float_t eS = 1e0 - info->origSigE->GetBinContent( i );
         Float_t S = eS * fNSignal;
	 Float_t eB =  (1e0- info->origBgdE->GetBinContent( i ));
	 Float_t B = eB * fNBackground;
         info->purS->SetBinContent( i, (S+B==0)?0:S/(S+B) );
         info->purB->SetBinContent( i, (S+B==0)?0:B/(S+B) );

	Float_t _purS = (S+B==0)?0:S/(S+B);
	Float_t _purB = (S+B==0)?0:B/(S+B);
	Int_t _binS   = info->purEffS->FindBin(eS);
	Int_t _binB = info->purEffS->FindBin(eB);

	 info->purEffS->SetBinContent(_binS,_purS);
	 info->purEffB->SetBinContent(_binB,_purB);

//	cout<<"_purS = "<<_purS<<endl;
//	cout<<"_purB = "<<_purS<<endl;
//	cout<<"_binS = "<<_binS<<endl;
//	cout<<"_binB = "<<_binB<<endl;

//	Double_t _x = S;
//	Double_t _y = B;
//        cout<<"f.Eval(S,B) = "<<f.Eval(_x,_y)<<endl;
          if ( f.Eval(S,B)>6) info->effBdivS->SetBinContent( _binB,6);
			else     info->effBdivS->SetBinContent( _binB, f.Eval(S,B) );


///fill each 4th point
//	if (i%_nPointBin==0 && info->_markersB && info->_textsB &&  info->_markersS && info->_textsS )
	if (fabs(_prevPurB-_purB)>_deltaPurB && info->_markersB && info->_textsB &&  info->_markersS && info->_textsS && _disc>0.01)
		{
			Float_t _size = info->purEffB->GetXaxis()->GetLabelSize();
			 TMarker *m2B = new TMarker(eB,_purB,29);
			m2B->SetMarkerSize(1.8);
			info->_markersB->Add(m2B);
			TText * t2B = new TText(eB,_purB,TString(Form("%.2f",_disc)).Data());		
			t2B->SetTextSize(_size);
			info->_textsB->Add(t2B);			

			 TMarker *m2S = new TMarker(eS,_purS,29);
			m2S->SetMarkerSize(1.8);
                        info->_markersS->Add(m2S);	
			 TText * t2S = new TText(eS,_purS,TString(Form("%.2f",_disc)).Data());
			t2S->SetTextSize(_size);

                        info->_textsS->Add(t2S);


		} 	///if

if (fabs(_prevPurB-_purB) >_deltaPurB) _prevPurB = _purB;

	} ///for

      info->maxSignificance = info->effBdivS->GetMaximum();
      info->effBdivS->Scale(1/info->maxSignificance);

} /// while


return;
}


void StatDialogMVAEffs::ReadHistograms(TFile* file) 
{
   if (fInfoList) { 
      TIter next(fInfoList);
      MethodInfo *info(0);
      while ( (info = (MethodInfo*)next()) ) {
         delete info;
      }
      delete fInfoList;
      fInfoList=0;
   }
   fInfoList = new TList;

   // search for the right histograms in full list of keys
   TIter next(file->GetListOfKeys());
   TKey *key(0);   
   while( (key = (TKey*)next()) ) {

      if (!TString(key->GetName()).BeginsWith("Method_")) continue;
      if( ! gROOT->GetClass(key->GetClassName())->InheritsFrom("TDirectory") ) continue;

      cout << "--- Found directory: " << ((TDirectory*)key->ReadObj())->GetName() << endl;

      TDirectory* mDir = (TDirectory*)key->ReadObj();

      TIter keyIt(mDir->GetListOfKeys());
      TKey *titkey;
      while((titkey = (TKey*)keyIt())) {
        if( ! gROOT->GetClass(titkey->GetClassName())->InheritsFrom("TDirectory") ) continue;
        
        MethodInfo* info = new MethodInfo();
        TDirectory* titDir = (TDirectory *)titkey->ReadObj();

        TMVAGlob::GetMethodName(info->methodName,key);
        TMVAGlob::GetMethodTitle(info->methodTitle,titDir);        
        if (info->methodTitle.Length() > maxLenTitle) maxLenTitle = info->methodTitle.Length();
        TString hname = "MVA_" + info->methodTitle;
        
        cout << "--- Classifier: " << info->methodTitle << endl;
        
        info->sig = dynamic_cast<TH1*>(titDir->Get( hname + "_S" ));
        info->bgd = dynamic_cast<TH1*>(titDir->Get( hname + "_B" ));
        info->origSigE = dynamic_cast<TH1*>(titDir->Get( hname + "_effS" ));
        info->origBgdE = dynamic_cast<TH1*>(titDir->Get( hname + "_effB" ));      
        if (info->origSigE==0 || info->origBgdE==0) { delete info; continue; }

        info->SetResultHists();
        fInfoList->Add(info);
      }
   }
   return;
}

void StatDialogMVAEffs::DrawHistograms(TString outputdir) 
{
   // counter variables
   Int_t countCanvas = 0;

   // define Canvas layout here!
   const Int_t width = 600;   // size of canvas
   Int_t signifColor = TColor::GetColor( "#00aa00" );

   TIter next(fInfoList);
   MethodInfo* info(0);
   while ( (info = (MethodInfo*)next()) ) {

      // create new canvas
      TCanvas *c = new TCanvas( Form("canvas%d", countCanvas+1), 
                                Form("\'Before-Cut\' efficiencies for %s classifier",info->methodTitle.Data()), 
                                countCanvas*50+200, countCanvas*20, width, Int_t(width*0.78) ); 
      info->canvas = c;

      // draw grid
      c->SetGrid(1);
      c->SetTickx(0);
      c->SetTicky(0);

      TStyle *TMVAStyle = gROOT->GetStyle("Plain"); // our style is based on Plain
      TMVAStyle->SetLineStyleString( 5, "[32 22]" );
      TMVAStyle->SetLineStyleString( 6, "[12 22]" );
         
      c->SetTopMargin(.2);

	 info->purEffB->SetTitle("\'Before - Cut\' efficiencies and purity");
	info->purEffB->GetXaxis()->SetTitle( "Efficiency" );
	 info->purEffB->GetYaxis()->SetTitle( "Purity" );


//      TMVAGlob::SetFrameStyle( info->effpurS );
      TMVAGlob::SetFrameStyle( info->purEffB );

      c->SetTicks(0,0);
      c->SetRightMargin ( 2.0 );

	info->purEffB->SetMaximum(1.1);
	info->purEffB->Draw("histl");

  // update
      c->Update();

	info->_markersB->Draw();
	info->_textsB->Draw();

  // update
      c->Update();


	info->purEffS->Draw("samehistl");
	info->_markersS->Draw();
	info->_textsS->Draw();

  // update
      c->Update();

	info->effBdivS->SetLineColor(signifColor);
	info->effBdivS->Draw("samehistl");

  // update
      c->Update();


      // redraw axes
      info->purEffB->Draw( "sameaxis" );

  // update
      c->Update();


  // Draw second axes
      info->rightAxis = new TGaxis(c->GetUxmax(), c->GetUymin(),
                                   c->GetUxmax(), c->GetUymax(),0,1.1*info->maxSignificance,510,"+L");
//                                   c->GetUxmax(), c->GetUymax(),0,6,510,"+L");
      info->rightAxis->SetLineColor ( signifColor );
      info->rightAxis->SetLabelColor( signifColor );
      info->rightAxis->SetTitleColor( signifColor );

      info->rightAxis->SetTitleSize( info->effBdivS->GetXaxis()->GetTitleSize() );
      info->rightAxis->SetTitle( GetLatexFormula().Data());
      info->rightAxis->Draw();	

	



      // Draw legend               
      TLegend *legend1= new TLegend( c->GetLeftMargin(), 1 - c->GetTopMargin(), 
                                     c->GetLeftMargin() + 0.4, 1 - c->GetTopMargin() + 0.12 );
      legend1->SetFillStyle( 1 );
      legend1->AddEntry(info->purEffS,"Signal efficiency-purity","L");
      legend1->AddEntry(info->purEffB,"Background efficiency-purity","L");
      legend1->Draw("same");
      legend1->SetBorderSize(1);
      legend1->SetMargin( 0.3 );

      TLegend *legend2= new TLegend( c->GetLeftMargin() + 0.4, 1 - c->GetTopMargin(), 
                                     1 - c->GetRightMargin(), 1 - c->GetTopMargin() + 0.12 );
      legend2->SetFillStyle( 1 );
//      legend2->AddEntry(info->purS,"Signal purity","L");
//      legend2->AddEntry(info->effpurS,"Signal efficiency*purity","L");
//      legend2->AddEntry(info->purB,"Background purity","L");
//      legend2->AddEntry(info->effpurB,"Background efficiency*purity","L");

      legend2->AddEntry(info->effBdivS,Form("%s",fFormula.Data()),"L");
      legend2->Draw("same");
      legend2->SetBorderSize(1);
      legend2->SetMargin( 0.3 );

      c->Update();

      // switches
      const Bool_t Save_Images = kTRUE;

      if (Save_Images) {
	 TString _fff = fFormula;
	_fff.ReplaceAll("(","");
	_fff.ReplaceAll(")","");
	_fff.ReplaceAll("/","");
	_fff.ReplaceAll("+","");
	_fff.ReplaceAll("-","");
	_fff.ReplaceAll("*","");
         TMVAGlob::imgconv( c, Form("%s/mvaeffsPur_%s_%s", outputdir.Data() ,info->methodTitle.Data(), _fff.Data()) ); 
      }
      countCanvas++;
   }
}


void  mvaeffsPur_beforecut(TString fin = "TMVA.root",
//		  TString formula="S/sqrt(S+B)",
		  TString formula="B/S", TString outputdir="plots", Bool_t raiseNum=kTRUE,
		 Bool_t useTMVAStyle = kTRUE
	)
{
   TMVAGlob::Initialize( useTMVAStyle );

   StatDialogMVAEffs* gGui = new StatDialogMVAEffs(gClient->GetRoot(), 1000, 1000,!raiseNum);


   TFile* file = TMVAGlob::OpenFile( fin );
   gGui->ReadHistograms(file);
   gGui->SetFormula(formula);
	gGui->CalculateHists();
   gGui->DrawHistograms(outputdir);
   if (raiseNum) gGui->RaiseDialog();   
}
