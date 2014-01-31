// -*- C++ -*-

#include "TString.h"

// To use in CINT:
// root [0] #include "CMSTopStyle_v2.cc"
// root [1] CMSTopStyle style           
// root [2] style.TtbarColor
// (int)633

// To use in PyRoot:
// >>> import ROOT
// >>> ROOT.gROOT.ProcessLine ('.L CMSTopStyle.cc+')
// >>> style = ROOT.CMSTopStyle()
// >>> style.TtbarColor
// 633

class CMSTopStyle
{
   public:

      CMSTopStyle();

      ////////////
      // Colors //
      ////////////

      // see http://root.cern.ch/root/html/MACRO_TColor_3_wheel.gif
      // for color wheel

      // ttbar
      int TtbarColor;        
      int TtbarOtherColor;   
                                 
      // single top                 
      int SingleTopColor;    
      int ST_tWColor;        
      int ST_t_sColor;       
                                 
      // W + jets                   
      int WJetsColor;        
      int WMUNUJetsColor;        
      int WTAUNUJetsColor;        
      int WLFJetsColor;      
      int WbbJetsColor;      
      int WccJetsColor;      
      int WcJetsColor;       
                                 
      // Z + jets / DY              
      int DYZJetsColor;      
      int DYZTauTauJetsColor;
      // we should add Z + flavor too

      // QCD
      int QCDColor;          

///Hbb + bEnriched
	int HbbColor;
	int QcdColor;

	int QcdColor15to30;
 	int QcdColor30to50;
	int QcdColor50to150;
 	int QcdColor150toInf;

///Alpgen samples
/**
2b1j.root  
2b2j.root
2b3j.root
2c1j.root  
2c2j.root
2c3j.root
2b2c.root  
2b2c1j.root  
4b.root  
4b1j.root
4c.root
4c1j.root 


**/
	int Color2b1j;
	int Color2b2j;
	int Color2b3j;
	int Color2c1j;
	int Color2c2j;
	int Color2c3j;
	int Color2b2c;
	int Color2b2c1j;
	int Color4b;
	int Color4b1j;
	int Color4c;
	int Color4c1j;


      // Other EW
      int DibosonsColor;     
      int GammaJetsColor;    
      int WGammaColor;       
 

      ///////////
      // Fills //
      ///////////

      // ttbar
      int TtbarFill;        
      int TtbarOtherFill;    
                                 
      // single top                 
      int SingleTopFill;    
      int ST_tWFill;        
      int ST_t_sFill;        
                                 
      // W + jets                   
      int WJetsFill;        
      int WMUNUJetsFill;        
      int WTAUNUJetsFill;        
      int WLFJetsFill;      
      int WbbJetsFill;      
      int WccJetsFill;      
      int WcJetsFill;       
                                 
      // Z + jets / DY              
      int DYZJetsFill;      
      int DYZTauTauJetsFill;
      // we should add Z + flavor too

      // QCD
      int QCDFill;          

///Hbb + bEnriched

	int HbbFill;
	int QcdFill;

      // Other EW
      int DibosonsFill;      
      int GammaJetsFill;    
      int WGammaFill;        
 
      //////////
      // Text //
      //////////

      // ttbar
      TString TtbarText;        
      TString TtbarOtherText;   
                                 
      // single top                 
      TString SingleTopText;    
      TString ST_tWText;        
      TString ST_t_sText;       
                                 
      // W + jets                   
      TString WJetsText;        
      TString WMUNUJetsText;        
      TString WTAUNUJetsText;        
      TString WLFJetsText;      
      TString WbbJetsText;      
      TString WccJetsText;      
      TString WcJetsText;       
                                 
      // Z + jets / DY              
      TString DYZJetsText;      
      TString DYZemuJetsText;   
      TString DYZTauTauJetsText;
      // we should add Z + flavor too

      // QCD
      TString QCDText;          

///Hbb + bEnriched
	TString HbbText;
	TString QcdText;

      // Other EW
      TString DibosonsText;     
      TString GammaJetsText;    
      TString WGammaText;       
   
};
