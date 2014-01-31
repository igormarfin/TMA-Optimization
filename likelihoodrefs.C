#include <vector>
#include <string>
#include "tmvaglob.C"


// this macro plots the reference distribuions for the Likelihood
// methods for the various input variables used in TMVA (e.g. running
// TMVAnalysis.C).  Signal and Background are plotted separately

// input: - Input file (result from TMVA),
//        - use of TMVA plotting TStyle
void likelihoodrefs( TString fin = "TMVA.root", Bool_t useTMVAStyle = kTRUE )
{
   // set style and remove existing canvas'
   TMVAGlob::Initialize( useTMVAStyle );
  
   // checks if file with name "fin" is already open, and if not opens one
   TFile* file = TMVAGlob::OpenFile( fin );  

   // get all titles of the method likelihood
   TList titles;
   UInt_t ninst = TMVAGlob::GetListOfTitles("Method_Likelihood",titles);
   if (ninst==0) {
      cout << "Could not locate directory 'Method_Likelihood' in file " << fin << endl;
      return;
   }
   // loop over all titles
   TIter keyIter(&titles);
   TDirectory *lhdir;
   TKey *key;
   while ((key = TMVAGlob::NextKey(keyIter,"TDirectory"))) {
      lhdir = (TDirectory *)key->ReadObj();
      likelihoodrefs( lhdir );
   }
}

void likelihoodrefs( TDirectory *lhdir ) {
   Bool_t newCanvas = kTRUE;
   
   const UInt_t maxCanvas = 200;
   TCanvas** c = new TCanvas*[maxCanvas];
   Int_t width  = 670;
   Int_t height = 380;

   // avoid duplicated printing
   std::vector<std::string> hasBeenUsed;
   const TString titName = lhdir->GetName();
   UInt_t ic = -1;   
   UInt_t ic2 = 0;   

   TIter next(lhdir->GetListOfKeys());
   TKey *key;
   while ((key = TMVAGlob::NextKey(next,"TH1"))) { // loop over all TH1
      TH1 *h = (TH1*)key->ReadObj();
      TH1F *b( 0 );
      TString hname( h->GetName() );

      // avoid duplicated plotting
      Bool_t found = kFALSE;
      for (UInt_t j = 0; j < hasBeenUsed.size(); j++) {
         if (hasBeenUsed[j] == hname.Data()) found = kTRUE;
      }
      if (!found) {

         // draw original plots
         if (hname.EndsWith("_sig_nice")) {

            if (newCanvas) {
               char cn[20];
               sprintf( cn, "cv%d_%s", ic+1, titName.Data() );
//               ++ic;
		ic+=2;
               TString n = hname;	  
               c[ic] = new TCanvas( cn, Form( "%s reference for variable: %s", 
                                              titName.Data(),(n.ReplaceAll("_sig","")).Data() ), 
                                    ic*50+50, ic*20, width, height ); 
               c[ic]->Divide(2,1);


		ic2+=2;
               sprintf( cn, "cv%d_%s", ic2+1, titName.Data() );
	        c[ic2] = new TCanvas( cn, Form( "%s reference for variable: %s",
                                              titName.Data(),(n.ReplaceAll("_sig","")).Data() ),
                                    ic2*50+50, ic2*20, width, height );



               newCanvas = kFALSE;
            }      

            // signal
            Int_t color = 4; 
            TPad * cPad2 = (TPad*)c[ic2]->cd();
            TPad * cPad = (TPad*)c[ic]->cd(1);
            TString plotname = hname;

            h->SetMaximum(h->GetMaximum()*1.3);
            h->SetMinimum( 0 );
            h->SetMarkerColor(color);
            h->SetMarkerSize( 0.7 );
            h->SetMarkerStyle( 24 );
            h->SetLineWidth(1);
            h->SetLineColor(color);
            color++;
            h->Draw("e1");
            Double_t hSscale = 1.0/(h->GetSumOfWeights()*h->GetBinWidth(1));

            TLegend *legS= new TLegend( cPad->GetLeftMargin(), 
                                        1-cPad->GetTopMargin()-.14, 
                                        cPad->GetLeftMargin()+.77, 
                                        1-cPad->GetTopMargin() );
            legS->SetBorderSize(1);
            legS->AddEntry(h,"Input data (signal)","p");


            TLegend *legS2= new TLegend( cPad2->GetLeftMargin(), 
                                        1-cPad2->GetTopMargin()-.14, 
                                        cPad2->GetLeftMargin()+.77, 
                                        1-cPad2->GetTopMargin() );
            legS2->SetBorderSize(1);


            // background
            TString bname( hname );	
            b = (TH1F*)lhdir->Get( bname.ReplaceAll("_sig","_bgd") );
            cPad = (TPad*)c[ic]->cd(2);
            color = 2;
            b->SetMaximum(b->GetMaximum()*1.3);
            b->SetMinimum( 0 );
            b->SetLineWidth(1);
            b->SetLineColor(color);
            b->SetMarkerColor(color);
            b->SetMarkerSize( 0.7 );
            b->SetMarkerStyle( 24 );
            b->Draw("e1");       
            Double_t hBscale = 1.0/(b->GetSumOfWeights()*b->GetBinWidth(1));
            TLegend *legB= new TLegend( cPad->GetLeftMargin(), 
                                        1-cPad->GetTopMargin()-.14, 
                                        cPad->GetLeftMargin()+.77, 
                                        1-cPad->GetTopMargin() );
            legB->SetBorderSize(1);
            legB->AddEntry(b,"Input data (backgr.)","p");

            // register
            hasBeenUsed.push_back( bname.Data() );

            // the PDFs --------------

            // check for splines
            h = 0;
            b = 0;
            TString pname = hname; pname.ReplaceAll("_nice","");            
            for (int i=0; i<= 5; i++) {
               TString hspline = pname + Form( "_smoothed_hist_from_spline%i", i );
               h = (TH1F*)lhdir->Get( hspline );
               if (h) {
                  b = (TH1F*)lhdir->Get( hspline.ReplaceAll("_sig","_bgd") );
                  break;
               }
            }

            // check for KDE
            if (h == 0 && b == 0) {
               TString hspline = pname + Form( "_smoothed_hist_from_KDE", i );
               h = (TH1F*)lhdir->Get( hspline );
               if (h) {
                  b = (TH1F*)lhdir->Get( hspline.ReplaceAll("_sig","_bgd") );
               }
            }
               
            // found something ?
            if (h == 0 || b == 0) {
               cout << "--- likelihoodrefs.C: did not find spline for histogram: " << pname.Data() << endl;
            }
            else {
               
               Double_t pSscale = 1.0/(h->GetSumOfWeights()*h->GetBinWidth(1));
	     color = 4;
               c[ic]->cd(1);
               h->SetLineWidth(2);
               h->SetLineColor(color);

	TH1 * h2 = (TH1* )h->Clone();
               h->Scale( pSscale/hSscale );
          

               legS->AddEntry(h,"Estimated PDF (norm. signal)","l");
               h->Draw("histsame");
               legS->Draw();

		legS2->AddEntry(h2,"Estimated PDF (norm. signal)","l");

//		gPad->Modified();
	  
               Double_t pBscale = 1.0/(b->GetSumOfWeights()*b->GetBinWidth(1));
               color = 2;
               c[ic]->cd(2);
               b->SetLineColor(color);
               b->SetLineWidth(2);
		TH1 * b2 = (TH1* )b->Clone();
               b->Scale( pBscale/hBscale );

               legB->AddEntry(b,"Estimated PDF (norm. backgr.)","l");
               b->Draw("histsame");

               // draw the legends
               legB->Draw();

//	gPad->Modified();
//            c[ic]->Update();

		legS2->AddEntry(b2,"Estimated PDF (norm. backgr.)","l");
		
//	 h->Scale(hSscale /pSscale);

		 h2->Scale( pSscale);
//		  b->Scale( hBscale/pBscale );
		 b2->Scale( pBscale);



	  if (h2->GetMaximum()>b2->GetMaximum())
	 {
	c[ic2]->cd();
	h2->Draw("hist");
	b2->Draw("histsame");
	} else
	{
	c[ic2]->cd();
	b2->Draw("hist");
	h2->Draw("histsame");
	}
		 legS2->Draw();		

	            c[ic]->Update();
	            c[ic2]->Update();

               hasBeenUsed.push_back( pname.Data() );
            }	  


            // write to file
            TString fname = Form( "plots/%s_refs_c%i", titName.Data(), ic+1 );
            TMVAGlob::imgconv( c[ic], fname );

            fname = Form( "plots/%s_refs_c%i", titName.Data(), ic2+1 );
            TMVAGlob::imgconv( c[ic2], fname );

            //	c[ic]->Update();

            newCanvas = kTRUE;
            hasBeenUsed.push_back( hname.Data() );
         }
      }
   }
}

