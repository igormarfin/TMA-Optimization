#include <iostream>
#include <vector>

#include "TList.h"
#include "TROOT.h"
#include "TKey.h"
#include "TString.h"
#include "TControlBar.h"
#include "TObjString.h"
#include "TROOT.h"

#include "tmvaglob.C"

// some global lists
static TList*               TMVAGui_keyContent;

TList* GetKeyList( const TString& pattern )
{
   TList* list = new TList();

   TIter next( TMVAGui_keyContent );
   TKey* key(0);
   while ((key = (TKey*)next())) {         
      if (TString(key->GetName()).Contains( pattern )) { list->Add( new TObjString( key->GetName() ) ); }
   }
   return list;
}

// main GUI
void TMVAGuiForPython( const char* fName = "TMVA.root" , const char * outputdir="plots", int type=-1 ) ///usage:
{   


//TMVA::gConfig().GetVariablePlotting().fNbins1D = 50.0;
//TMVA::gConfig().GetVariablePlotting().fNbinsXOfROCCurve=50;

   // Use this script in order to run the various individual macros
   // that plot the output of TMVA (e.g. running TMVAClassification.C),
   // stored in the file "TMVA.root"

   TString curMacroPath("./");
   // uncomment next line for macros submitted to next root version
   gROOT->SetMacroPath(curMacroPath+":$ROOTSYS/tmva/test/:");
   
   // for the sourceforge version, including $ROOTSYS/tmva/test in the
   // macro path is a mistake, especially if "./" was not part of path
   // add ../macros to the path (comment out next line for the ROOT version of TMVA)
   // gROOT->SetMacroPath(curMacroPath+":../macros:");
   


   // check if file exist
   TFile* file = TFile::Open( fName );
   if (!file) {
      cout << "==> Abort TMVAGui, please verify filename" << endl;
      return;
   }
   // find all references   
   cout << "--- Reading keys ..." << endl;
   TMVAGui_keyContent = (TList*)file->GetListOfKeys()->Clone();

   // close file
   file->Close();

   TString defaultRequiredClassifier = "";

   TList* keylist= GetKeyList( "InputVariables" );;
   TListIter it = TListIter ( keylist );
   char ch = 'a';

   if (type==0 ){
   // find all input variables types
   keylist = GetKeyList( "InputVariables" );
   it = TListIter ( keylist );
   TObjString* str = 0;
   ch = 'a';
   while ((str = (TObjString*)it())) {
      TString tmp   = str->GetString();
      TString title = Form( "Input variables '%s'-transformed (training sample)", 
                            tmp.ReplaceAll("InputVariables_","").Data() );
      if (tmp.Contains( "Id" )) title = "Input variables (training sample)";
      gROOT->ProcessLine( Form( ".x variables.C(\"%s\",\"%s\",\"%s\",\"%s\")", fName, str->GetString().Data(), title.Data(),outputdir ) );
   }      
   

} ///type ==0

/*
   if (type==1 ){
		it.Reset(); ch = 'a';

	 while ((str = (TObjString*)it())) {
      TString tmp   = str->GetString();
      TString title = Form( "Input variable correlations '%s'-transformed (scatter profiles)", 
                            tmp.ReplaceAll("InputVariables_","").Data() );
      if (tmp.Contains( "Id" )) title = "Input variable correlations (scatter profiles)";
	  gROOT->ProcessLine( Form( ".x CorrGui.C(\"%s\",\"%s\",\"%s\")", fName, str->GetString().Data(), title.Data(),outputdir );
   }      


	} ///type ==1
*/


   if (type==1 ){
		gROOT->ProcessLine( Form( ".x correlations.C(\"%s\",\"%s\")", fName, outputdir ));
	} ///type==1

   if (type==2)
	{

		gROOT->ProcessLine( Form( ".x   mvas.C(\"%s\",\"%s\",0)", fName, outputdir ));
	} //type==2

   if (type==3)
	{

	 gROOT->ProcessLine( Form( ".x   mvas.C(\"%s\",\"%s\",3)", fName, outputdir ));

	} ///type==3

   if (type==4)
	{

	 gROOT->ProcessLine( Form( ".x   mvas.C(\"%s\",\"%s\",1)", fName, outputdir ));

	} ///type==4


   if (type==5)
	{

	 gROOT->ProcessLine( Form( ".x   mvas.C(\"%s\",\"%s\",2)", fName, outputdir ));

	} ///type==5

   if (type==6)
	{

	 gROOT->ProcessLine( Form( ".x  mvaeffs_beforecut.C(\"%s\",\"B/S\",\"%s\",kFALSE)", fName, outputdir ));

	} ///type==6


	if (type==7)
	{

		gROOT->ProcessLine( Form( ".x  mvaeffsPur_beforecut.C(\"%s\",\"B/S\",\"%s\",kFALSE)", fName, outputdir ));

	} //type==7

}
