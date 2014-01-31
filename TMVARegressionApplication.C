/**********************************************************************************
 * Project   : TMVA - a Root-integrated toolkit for multivariate data analysis    *
 * Package   : TMVA                                                               *
 * Exectuable: TMVARegressionApplication                                          *
 *                                                                                *
 * This macro provides a simple example on how to use the trained regression MVAs *
 * within an analysis module                                                      *
 **********************************************************************************/

#include <cstdlib>
#include <vector>
#include <iostream>
#include <map>
#include <string>

#include "TFile.h"
#include "TTree.h"
#include "TString.h"
#include "TSystem.h"
#include "TROOT.h"
#include "TStopwatch.h"

#if not defined(__CINT__) || defined(__MAKECINT__)
#include "TMVA/Tools.h"
#include "TMVA/Reader.h"
#endif

using namespace TMVA;

void TMVARegressionApplication( TString myMethodList = "" , TString fileOptimizeIn="") 
{

   //---------------------------------------------------------------
   // This loads the library
   TMVA::Tools::Instance();

   // Default MVA methods to be trained + tested
   std::map<std::string,int> Use;

   // --- Mutidimensional likelihood and Nearest-Neighbour methods
   Use["PDERS"]           = 0;
   Use["PDEFoam"]         = 1; 
   Use["KNN"]             = 1;
   // 
   // --- Linear Discriminant Analysis
   Use["LD"]		        = 1;
   // 
   // --- Function Discriminant analysis
   Use["FDA_GA"]          = 1;
   Use["FDA_MC"]          = 0;
   Use["FDA_MT"]          = 0;
   Use["FDA_GAMT"]        = 0;
   // 
   // --- Neural Network
   Use["MLP"]             = 1; 
   // 
   // --- Support Vector Machine 
   Use["SVM"]             = 0;
   // 
   // --- Boosted Decision Trees
   Use["BDT"]             = 0;
   Use["BDTG"]            = 1;
   // ---------------------------------------------------------------

   std::cout << std::endl;
   std::cout << "==> Start TMVARegressionApplication" << std::endl;

   // Select methods (don't look at this code - not of interest)
   if (myMethodList != "") {
      for (std::map<std::string,int>::iterator it = Use.begin(); it != Use.end(); it++) it->second = 0;

      std::vector<TString> mlist = gTools().SplitString( myMethodList, ',' );
      for (UInt_t i=0; i<mlist.size(); i++) {
         std::string regMethod(mlist[i]);

         if (Use.find(regMethod) == Use.end()) {
            std::cout << "Method \"" << regMethod << "\" not known in TMVA under this name. Choose among the following:" << std::endl;
            for (std::map<std::string,int>::iterator it = Use.begin(); it != Use.end(); it++) std::cout << it->first << " ";
            std::cout << std::endl;
            return;
         }
         Use[regMethod] = 1;
      }
   }

   // --------------------------------------------------------------------------------------------------

   // --- Create the Reader object

   TMVA::Reader *reader = new TMVA::Reader( "!Color:!Silent" );    

   // Create a set of variables and declare them to the reader
   // - the variable names MUST corresponds in name and type to those given in the weight file(s) used
    // Read training and test data (see TMVAClassification for reading ASCII files)
   // load the signal and background event samples from ROOT trees
   TFile *input(0);
   TString fname = "./OptimizeTrees.root";
   if (!gSystem->AccessPathName( fname ))
      input = TFile::Open( fname ); // check if file in local directory exists
   else
      input = TFile::Open(fileOptimizeIn ); // if not: download from ROOT server

   if (!input) {
      std::cout << "ERROR: could not open data file" << std::endl;
      exit(1);
   }
   std::cout << "--- TMVARegressionApplication           : Using input file: " << input->GetName() << std::endl;

   TTree *regTree = (TTree*)input->Get("optimization");
   if (!regTree ) {  std::cout << "ERROR: could not get TTree "<<std::endl; exit(1) }

   Int_t numvars=regTree->GetListOfBranches()->GetEntries();


   
   Float_t * vars[100];
    for (Int_t var =0; var<numvars;var++)  vars[var] = new Float_t(0e0);

    for (Int_t var =0; var<numvars;var++){

        if (TString(regTree->GetListOfBranches()->At(var)->GetName()).Contains("result")) continue;
        cout<<"variable "<<regTree->GetListOfBranches()->At(var)->GetName()<<endl;
		reader->AddVariable( regTree->GetListOfBranches()->At(var)->GetName(),vars[var]);

	}


   // --- Book the MVA methods

   TString dir    = "regression_weights/";
   TString prefix = "TMVARegression";

   // Book method(s)
   for (std::map<std::string,int>::iterator it = Use.begin(); it != Use.end(); it++) {
      if (it->second) {
         TString methodName = it->first + " method";
         TString weightfile = dir + prefix + "_" + TString(it->first) + ".weights.xml";
         reader->BookMVA( methodName, weightfile ); 
      }
   }
   
   // Book output histograms
   TH1* hists[100];
//   TH1* hists_orig[100];
   Int_t nhists = -1;
   for (std::map<std::string,int>::iterator it = Use.begin(); it != Use.end(); it++) {
      TH1* h = new TH1F( it->first.c_str(), TString(it->first) + " method", 100, -1, 1 );
//      std::string  nameorig=it->first+"_org";
//      TH1* h2 = new TH1F( nameorig.c_str(), TString(it->first) + " method", 100, -100, 600 );
      if (it->second) {
		++nhists;
		hists[nhists] = h;
//       hists_orig[nhists] = h2;
		}
   }
   nhists++;
   

   // --- Event loop

   // Prepare the tree
   // - here the variable names have to corresponds to your tree
   // - you can use the same variables as above which is slightly faster,
   //   but of course you can use different ones and copy the values inside the event loop
   //
   TTree* theTree = (TTree*)input->Get("optimization");
   std::cout << "--- Select signal sample" << std::endl;

   
   TTree* newTrees[100];
    Int_t ntrees = -1;
   

   TFile *target  = new TFile("TMVARegApp.root","RECREATE" );

   Float_t result;

   for (std::map<std::string,int>::iterator it = Use.begin(); it != Use.end(); it++) {
     std::string nameTree=it->first + std::string("Tree");
     TTree* newTree = new TTree (nameTree.c_str(),TString(it->first) + " method");
     cout<<"newTree "<<newTree->GetName()<<endl;
      if (it->second) {
        ++ntrees;
        newTree->Branch("result",&result,"result/F");
        newTrees[ntrees] = newTree;

   }
}
   ntrees++;

   
    for (Int_t var =0; var<numvars;var++){

        if (TString(regTree->GetListOfBranches()->At(var)->GetName()).Contains("result")) continue;
		   theTree->SetBranchAddress( regTree->GetListOfBranches()->At(var)->GetName(),  vars[var]);
		}

   std::cout << "--- Processing: " << theTree->GetEntries() << " events" << std::endl;
   TStopwatch sw;
   sw.Start();
   for (Long64_t ievt=0; ievt<theTree->GetEntries();ievt++) {

      if (ievt%1000 == 0) {
         std::cout << "--- ... Processing event: " << ievt << std::endl;
      }

      theTree->GetEntry(ievt);

      // Retrieve the MVA target values (regression outputs) and fill into histograms
      // NOTE: EvaluateRegression(..) returns a vector for multi-target regression

      for (Int_t ih=0; ih<nhists; ih++) {
         TString title = hists[ih]->GetTitle();
         Float_t val = (reader->EvaluateRegression( title ))[0];
         hists[ih]->Fill( val );    
         result= (reader->EvaluateRegression( title  ))[0];
         newTrees[ih]->Fill();
      }
   }
   sw.Stop();
   std::cout << "--- End of event loop: "; sw.Print();

   // --- Write histograms

   for (Int_t ih=0; ih<nhists; ih++) {
     newTrees[ih]->Write();
	 hists[ih]->Write();
}
   target->Close();

   std::cout << "--- Created root file: \"" << target->GetName() 
             << "\" containing the MVA output histograms" << std::endl;
  
   delete reader;
    
   std::cout << "==> TMVARegressionApplication is done!" << std::endl << std::endl;
}
