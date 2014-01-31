#! /usr/bin/env python

"""a set of utils to run TMultydimFit && scipy.interpolate.Rbf

parameterization

uses different cuts on pT


"""
__author__ =  'Igor Marfin'
__version__=  '1.0'
__nonsense__ = 'HiggsGroup'


import time
import os
import sys
import commands
import re
from optparse import OptionParser
import math 
import numpy
import random
import array

from scipy.interpolate import Rbf,UnivariateSpline,splprep,splev
#set batch mode
#sys.argv.append('-b-')
import ROOT 
#ROOT.gROOT.SetBatch(True)
#from ROOT import *
#sys.argv.remove('-b-')

try:  
 cmssw =os.environ["CMSSW_BASE"]
 print cmssw
except KeyError: 
 print "Please ini CMSSW"
 print "We neend CMSSW for scipy!" 
 sys.exit(1)



def get_pseudo_points(file,type="sgnf",point=[60,53]):
 """    get pseudo true points 

 """
 
 ntuple=file.Get("result_tntuple")
 print ntuple
 if (ntuple):
#  (pj0,pj1,pj2,sig_sel,bkg_sel,sgnf,sig_eff,bkg_eff)=(float(),float(),float(),float(),float(),float(),float(),float())
  pj0 = array.array('f',[0])
  pj1 = array.array('f',[0])
  pj2 = array.array('f',[0])
  sig_sel = array.array('f',[0])
  bkg_sel = array.array('f',[0])
  sig_eff = array.array('f',[0])
  bkg_eff = array.array('f',[0])
  sgnf = array.array('f',[0])

  ntuple.SetBranchAddress("pj0",pj0)
  ntuple.SetBranchAddress("pj1",pj1)
  ntuple.SetBranchAddress("pj2",pj2)
  ntuple.SetBranchAddress("sig_sel",sig_sel)
  ntuple.SetBranchAddress("bkg_sel",bkg_sel)
  ntuple.SetBranchAddress("sig_eff",sig_eff)
  ntuple.SetBranchAddress("bkg_eff",bkg_eff)
  ntuple.SetBranchAddress(type,sgnf)

  x1=numpy.ndarray(ntuple.GetEntries())
  x2=numpy.ndarray(ntuple.GetEntries())
  x3=numpy.ndarray(ntuple.GetEntries())
  y=numpy.ndarray(ntuple.GetEntries())
  for i in range(ntuple.GetEntries()):
   ntuple.GetEntry(i)
   if (abs(point[0]-pj0[0])/point[0] <0.1) &  (abs(point[1]-pj1[0])/point[1] <0.1):
     x1[i]=pj0[0]
     x2[i]=pj1[0]
     x3[i]=pj2[0]
     y[i]=sgnf[0]
     print "x1=",x1[i]
     print "x2=",x2[i]
     print "x3=",x3[i]
     print "y=",y[i]
  gr1 = ROOT.TGraph(len(y),x3, y)
  gr1.SetLineColor(2)
  gr1.SetMarkerColor(2)
  gr1.Sort()
 return gr1


def get_true_points(file,type="sgnf"):
 """    get true points 

 """

 ntuple=file.Get("result_tntuple")
 print ntuple
 if (ntuple):
#  (pj0,pj1,pj2,sig_sel,bkg_sel,sgnf,sig_eff,bkg_eff)=(float(),float(),float(),float(),float(),float(),float(),float())
  pj0 = array.array('f',[0])
  pj1 = array.array('f',[0])
  pj2 = array.array('f',[0])
  sig_sel = array.array('f',[0])
  bkg_sel = array.array('f',[0])
  sig_eff = array.array('f',[0])
  bkg_eff = array.array('f',[0])
  sgnf = array.array('f',[0])

  ntuple.SetBranchAddress("pj0",pj0)
  ntuple.SetBranchAddress("pj1",pj1)
  ntuple.SetBranchAddress("pj2",pj2)
  ntuple.SetBranchAddress("sig_sel",sig_sel)
  ntuple.SetBranchAddress("bkg_sel",bkg_sel)
  ntuple.SetBranchAddress("sig_eff",sig_eff)
  ntuple.SetBranchAddress("bkg_eff",bkg_eff)
  ntuple.SetBranchAddress(type,sgnf)

  x1=numpy.ndarray(ntuple.GetEntries())
  x2=numpy.ndarray(ntuple.GetEntries())
  x3=numpy.ndarray(ntuple.GetEntries())
  y=numpy.ndarray(ntuple.GetEntries())
  for i in range(ntuple.GetEntries()):
   ntuple.GetEntry(i)
   x1[i]=pj0[0]
   x2[i]=pj1[0]
   x3[i]=pj2[0]
   y[i]=sgnf[0]
  gr1 = ROOT.TGraph(len(y),x3, y)
  gr1.SetLineColor(2)
  gr1.SetMarkerColor(2)
  gr1.Sort()
 return gr1

def getRatioError(X,Y,Xerr=0.,Yerr=0.):
 """ return error of X/Y ratio assuming nX and Y """

 if (Xerr == 0.):	Xerr=math.sqrt(X)
 if (Yerr == 0.):	Yerr=math.sqrt(Y)
 
 if (Y not 0.):
# 1)  Gauss aproximation of two X/Y numbers
#http://www.talkstats.com/showthread.php/16499-Standard-deviation-of-the-Ratio-of-two-means
#Var[X/Y]= \frac {1} {\mu_Y^2}Var[X] + \frac {\mu_X^2} {\mu_Y^4}Var[Y] - 2\frac {\mu_X} {\mu_Y^3}Cov[X, Y]

#http://en.wikipedia.org/wiki/Propagation_of_uncertainty
#\left(\frac{\sigma_f}{f}\right)^2 \approx \left(\frac{\sigma_A}{A}\right)^2 + \left(\frac{\sigma_B}{B}\right)^2 - 2\frac{\sigma_A\sigma_B}{AB}\rho_{AB}

  error=math.sqrt(math.pow(Xerr,2)*math.pow(Y,-2) + math.pow(Yerr,2)*math.pow(X,2)*math.pow(Y,-4))
 else:
  error=0.
 return 0.

def create_multidim (file,type="sgnf",output="TMultiDimFit"):
 """ 	read data from file and create multidimfit parameterization
         for significance

	available types are 
		* sgnf,
		* sig_eff,
		* bkg_eff

	available output are
 		* TMultiDimFit
		* Rbf
 """



##read a list of files
 ntuple=file.Get("result_tntuple")
 print ntuple
 if (ntuple):
#  (pj0,pj1,pj2,sig_sel,bkg_sel,sgnf,sig_eff,bkg_eff)=(float(),float(),float(),float(),float(),float(),float(),float())
  pj0 = array.array('f',[0])
  pj1 = array.array('f',[0])
  pj2 = array.array('f',[0])
  sig_sel = array.array('f',[0])
  bkg_sel = array.array('f',[0])
  sig_eff = array.array('f',[0])
  bkg_eff = array.array('f',[0])
  sgnf = array.array('f',[0])

  ntuple.SetBranchAddress("pj0",pj0)
  ntuple.SetBranchAddress("pj1",pj1)
  ntuple.SetBranchAddress("pj2",pj2)
  ntuple.SetBranchAddress("sig_sel",sig_sel)
  ntuple.SetBranchAddress("bkg_sel",bkg_sel)
  ntuple.SetBranchAddress("sig_eff",sig_eff)
  ntuple.SetBranchAddress("bkg_eff",bkg_eff)
  ntuple.SetBranchAddress(type,sgnf)

  multifit = ROOT.TMultiDimFit(3,ROOT.TMultiDimFit.kMonomials,"")
  x=numpy.ndarray(3)
  x1=numpy.ndarray(ntuple.GetEntries())
  x2=numpy.ndarray(ntuple.GetEntries())
  x3=numpy.ndarray(ntuple.GetEntries())
  y=numpy.ndarray(ntuple.GetEntries())
#  x1=numpy.ndarray(50)
#  x2=numpy.ndarray(50)
#  x3=numpy.ndarray(50)
#  y=numpy.ndarray(50)
  print multifit
  for i in range(ntuple.GetEntries()):
#   if (i>48):
#    continue
   ntuple.GetEntry(i)
   x[0]=pj0[0]
   x[1]=pj1[0]
   x[2]=pj2[0]
   multifit.AddRow(x,sgnf[0])
   x1[i]=pj0[0]
   x2[i]=pj1[0]
   x3[i]=pj2[0]
   y[i]=sgnf[0]
   print "x1[i]=",x1[i]
   print "x2[i]=",x2[i]
   print "x3[i]=",x3[i]
   print "y[i]=",y[i]
## 1-D cases
#   tckp,u=splprep([x1, x2, x3],y,s=3.0,k=3.0,nest=-1)
#  return tckp
#   return UnivariateSpline([x1, x2, x3], y)
  if "TMultiDimFit" in output:
   return  multifit
  if "Rbf-gaussian" in output:
   return Rbf(x1, x2, x3, y,function='gaussian',smooth=0.00005)
  if "Rbf-cubic" in output:
   return Rbf(x1, x2, x3, y,function='cubic')
  if "Rbf-inverse" in output:
   return Rbf(x1, x2, x3, y,function='inverse')
  if "Rbf-thin_plate" in output:
   return Rbf(x1, x2, x3, y,function='thin_plate')
  if "Rbf" in output:
   return Rbf(x1, x2, x3, y,smooth=0.00005)


def multidim_config(multifit):
 """    to do set up multifit 
         
 """
# x=numpy.ndarray(3)
# x=array.array('l',[0,1,2])
# x[0]=long(3)
# x[1]=long(3)
# x[2]=long(3)
# multifit.SetMaxPowers(x)

# multifit.SetMaxFunctions(500)
# multifit.SetMaxStudy(500)
# multifit.SetMaxTerms(50)
# multifit.SetPowerLimit(3)
# multifit.SetMinRelativeError(0.1)
 ROOT.gROOT.ProcessLine('.L multidim_config.C+')
 ROOT.multidim_config(multifit)
 

def multidim_process(multifit,type="sgnf"):
 """    to get result
  
 	   available types are 
        * sgnf,
        * sig_eff,
        * bkg_eff
    
 """

 multifit.Print('s')
 multifit.MakeHistograms()
 multifit.FindParameterization()
 multifit.Print('rc')
 multifit.MakeCode(type)
 


def get_result_multidimfit (multifit,params=[121.47734,68.657943,32.487167],interpolator="TMultiDimFit"):
 """ to get result
    available interpolator are
        * TMultiDimFit
        * Rbf
"""
 if (multifit):
  x=numpy.ndarray(len(params),float)
  for i in range(len(params)):
   x[i]=params[i]

  if "TMultiDimFit" in interpolator:
   return multifit.Eval(x)
  if "Rbf" in interpolator:
   return multifit(*x) 
#  return multifit(x) 


##1-D case
#  x1,x2,x3,y=splev(x,multifit)
#  return y

def plot_sgnf_3rdjet(multifit,params12=[60,53],cut=[50,20,60],interpolator="TMultiDimFit"):
 """ return TGraph with significance as a function of a cut on 3rd jet pT
	range is [bins,min,max] of 3rdjet
    params12 defines selection on 1,2 jets

     available interpolator are
        * TMultiDimFit
        * Rbf


 """

 bins=cut[0]
 xmin=cut[1]
 xmax=cut[2]
 
 if (bins>1):
  dx=float(xmax-xmin)/(bins-1)
  xs=numpy.ndarray(bins)
  ys=numpy.ndarray(bins)
 else:
  dx=float(xmax-xmin)/49
  xs=numpy.ndarray(50)
  ys=numpy.ndarray(50)
  bins=50
 for bin in range(bins):
  xs[bin]=xmin+bin*dx
  a=params12[:]
  a.append(xs[bin])
  ys[bin]=get_result_multidimfit(multifit,a,interpolator)

 gr1 = ROOT.TGraph(bins,xs, ys)
# gr1.SetName("Significance")
 gr1.SetLineColor(2)
 gr1.SetMarkerColor(2)
 gr1.Sort()
 print gr1
 return gr1

def plot_eff_3rdjet(multifit,params12=[60,53],cut=[50,20,60],interpolator="TMultiDimFit"):
 """ return TGraph with significance as a function of a cut on 3rd jet pT
	range is [bins,min,max] of 3rdjet
    params12 defines selection on 1,2 jets

    available interpolator are
        * TMultiDimFit
        * Rbf


 """

 bins=cut[0]
 xmin=cut[1]
 xmax=cut[2]
 
 if (bins>1):
  dx=float(xmax-xmin)/(bins-1)
  xs=numpy.ndarray(bins)
  ys=numpy.ndarray(bins)
 else:
  dx=float(xmax-xmin)/49
  xs=numpy.ndarray(50)
  ys=numpy.ndarray(50)
  bins=50
 for bin in range(bins):
  xs[bin]=xmin+bin*dx
  a=params12[:]
  a.append(xs[bin])
  ys[bin]=get_result_multidimfit(multifit,a,interpolator)
#  print ("xs=%f,ys=%f")%(xs[bin],ys[bin])

 gr1 = ROOT.TGraph(bins,xs, ys)
# gr1.SetName("Efficiency")
 gr1.SetLineColor(2)
 gr1.SetMarkerColor(2)
 gr1.Sort()
# print gr1
 return gr1

def test (multifit,params=[121.47734,68.657943,32.487167],interpolator="TMultiDimFit"):
 """ to perform a test

    available interpolator are
        * TMultiDimFit
        * Rbf

 """
 if (multifit):
  x=numpy.ndarray(len(params),float)
  print "input arguments: ", params
  for i in range(len(params)):
   x[i]=params[i]
 
 # d=multifit.Eval(x)
  d=get_result_multidimfit(multifit,x,interpolator)
  print "result=", d

def test_scenario (multifit,interpolator="TMultiDimFit"):
 """ to perform a test of scenarios

    available interpolator are
        * TMultiDimFit
        * Rbf

 """

 print "Low, mass: "
 for ptj3 in [20,21,22,25,30,30.09,31,32,33,35,40,41,42,43,45,50,51,51.5,53.456,55,60]:
  a=[60,53]
  a.append(ptj3)
  d=get_result_multidimfit(multifit,a,interpolator)
  print "result=",d
#  test(multifit,a)
 print "Medium, mass: "
 for ptj3 in [20,21,22,25,30,30.09,31,32,33,35,40,41,42,43,45,50,51,51.5,53.456,55,60]:
  a=[80,70]
  a.append(ptj3)
  d=get_result_multidimfit(multifit,a,interpolator)
  print "result=",d  
#  test(multifit,a)
 print "High, mass: "
 for ptj3 in [20,21,22,25,30,30.09,31,32,33,35,40,41,42,43,45,50,51,51.5,53.456,55,60]:
  a=[160,120]
  a.append(ptj3)  
  d=get_result_multidimfit(multifit,a,interpolator)
  print "result=",d
#  test(multifit,a)

 
def write_result(ptjet0,ptjet1,ptjet2,sig_sel,sig_all,bkg_sel,bkg_all):
 """ writes results to the file 'results.root'
 The results are histograms with 9 bins
    1bin -- ptj0 cut
    2bin -- ptj1 cut
    3bin -- ptj2 cut

    so far no triggers and btagging

    4bin -- all signal events
    5bin -- passed selection signal events 
    6bin -- all background events
    7bin -- passed selection background events 
    8bin -- significance
    9bin -- efficiency of signal selection
    10bin -- efficienct of background selection
 The name of the histogram is unique one like
 'result_'+str(int(random.uniform(1,1000))) """

 name='result_'+str(int(random.uniform(1,1000)))
 outputF=ROOT.TFile("result.root","UPDATE") 
 outputH=ROOT.TH1F(name,name,10,0,10)
 tntuple=outputF.Get("result_tntuple")
 sgnf=0.
 sig_eff=0.
 bkg_eff=0.
 if (tntuple):
  print "ntuple ",  tntuple
 else:
  tntuple=ROOT.TNtuple("result_tntuple","result_tntuple","pj0:pj1:pj2:sig_all:sig_sel:bkg_all:bkg_sel:sgnf:sig_eff:bkg_eff")
 tntuple.SetDirectory(outputF);
 tntuple.AutoSave();
 outputH.SetBinContent(1,ptjet0)
 outputH.SetBinContent(2,ptjet1)
 outputH.SetBinContent(3,ptjet2)
 outputH.SetBinContent(4,sig_all)
 outputH.SetBinContent(5,sig_sel)
 outputH.SetBinContent(6,bkg_all)
 outputH.SetBinContent(7,bkg_sel)
 if not ((sig_sel==0) & (bkg_sel==0)):
  outputH.SetBinContent(8,sig_sel/math.sqrt(sig_sel+bkg_sel))
  sgnf=sig_sel/math.sqrt(sig_sel+bkg_sel)
 else:
  outputH.SetBinContent(8,0.)
 if (sig_all!=0):
  outputH.SetBinContent(9,sig_sel/sig_all)
  sig_eff=sig_sel/sig_all
 else:
  outputH.SetBinContent(9,0.)

 if (bkg_all!=0):
  outputH.SetBinContent(10,bkg_sel/bkg_all)
  bkg_eff=bkg_sel/bkg_all
 else:
  outputH.SetBinContent(10,0.)


 tntuple.Fill(ptjet0,ptjet1,ptjet2,sig_all,sig_sel,bkg_all,bkg_sel,sgnf,sig_eff,bkg_eff)
 tntuple.Write("",ROOT.TObject.kOverwrite)  
 outputH.Write()
 outputF.Close()

def get_random ():
 """ return three random numbers in ranges defined throug ptjetMin/ptjetMax"""
 ptjet0=random.uniform(ptjet0Min,ptjet0Max)
 ptjet1=random.uniform(ptjet0*0.5,ptjet0)  # 80% window for ptjet1 selection
 ptjet2=random.uniform(ptjet2Min,0.50*ptjet1) # 50% of remaining window

 return (ptjet0,ptjet1,ptjet2)



if  __name__ == '__main__':
 """ 	main subroutine """

# interpolator="Rbf-cubic"
# interpolator="Rbf-inverse"
# interpolator="Rbf-thin_plate"
# interpolator="Rbf-gaussian"
 interpolator="Rbf"
# interpolator="TMultiDimFit"
 type="sgnf"
 


  
###Significance
# multifit=create_multidim (ROOT.TFile("result.root"),output=interpolator)
 multifit=create_multidim (ROOT.TFile("result_comb2.root"),output=interpolator)
 if "TMultiDimFit" in interpolator:
  multidim_config(multifit)
  multidim_process(multifit)
 c=ROOT.TCanvas("c","Significance")
##Low mass
 gr=plot_sgnf_3rdjet(multifit,params12=[60,53],cut=[50,20,50],interpolator=interpolator)
##Medium mass
 gr2=plot_sgnf_3rdjet(multifit,params12=[80,70],cut=[50,20,50],interpolator=interpolator)
 gr2.SetLineColor(3)
 gr2.SetMarkerColor(3)
##High mass
 gr3=plot_sgnf_3rdjet(multifit,params12=[160,120],cut=[50,20,50],interpolator=interpolator)
 gr3.SetLineColor(4)
 gr3.SetMarkerColor(4)

###True points for low mass
 gr4=get_true_points(ROOT.TFile("result_low.root"),type=type)
 gr4.SetLineColor(1)
 gr4.SetMarkerStyle(3)
###True points for medium mass
 gr5=get_true_points(ROOT.TFile("result_medium.root"),type=type)
 gr5.SetLineColor(1)
 gr5.SetMarkerColor(3)
 gr5.SetMarkerStyle(3)
###True points for high mass
 gr6=get_true_points(ROOT.TFile("result_high.root"),type=type)
 gr6.SetLineColor(1)
 gr6.SetMarkerColor(4)
 gr6.SetMarkerStyle(4)

###True points for low mass
 gr7=get_pseudo_points(ROOT.TFile("result.root"),type=type)
 gr7.SetLineColor(1)
 gr7.SetMarkerColor(1)
 gr7.SetMarkerStyle(1)



 mg1= ROOT.TMultiGraph()
 mg1.SetName("Significance")
 mg1.Add(gr)
 mg1.Add(gr2)
 mg1.Add(gr3)
 mg1.Add(gr4)
 mg1.Add(gr5)
 mg1.Add(gr6)
# mg1.Add(gr7)
 mg1.Draw("ALP")
 mg1.GetXaxis().SetTitle("p_{T}(jet_{3}),[GeV/c]")
 mg1.GetYaxis().SetTitle("significance")
 mg1.GetYaxis().SetLabelOffset(0.01);

 mg1.GetYaxis().SetTitleOffset(1.3);
 mg1.GetXaxis().SetTitleOffset(1.2);

# gr7.Draw("AP same")
 c.Modified()

 type="sig_eff"

###Signal Efficiency
 multifitSigEff=create_multidim (ROOT.TFile("result.root"),"sig_eff",output=interpolator)
# multifitSigEff=create_multidim (ROOT.TFile("result_comb2.root"),"sig_eff",output=interpolator)
 if "TMultiDimFit" in interpolator:
  multidim_config(multifitSigEff)
  multidim_process(multifitSigEff,type="sig_eff")
 c2=ROOT.TCanvas("c2","Signal Efficiency")

##Low mass
 gr11=plot_eff_3rdjet(multifitSigEff,params12=[60,53],cut=[50,20,50],interpolator=interpolator)

##Medium mass
 gr22=plot_eff_3rdjet(multifitSigEff,params12=[80,70],cut=[50,20,50],interpolator=interpolator)
 gr22.SetLineColor(3)
 gr22.SetMarkerColor(3)


##High mass
 gr33=plot_eff_3rdjet(multifitSigEff,params12=[160,120],cut=[50,20,50],interpolator=interpolator)
 gr33.SetLineColor(4)
 gr33.SetMarkerColor(4)


###True points for low mass
 gr44=get_true_points(ROOT.TFile("result_low.root"),type=type)
 gr44.SetLineColor(1)
 gr44.SetMarkerStyle(3)
###True points for medium mass
 gr55=get_true_points(ROOT.TFile("result_medium.root"),type=type)
 gr55.SetLineColor(1)
 gr55.SetMarkerColor(3)
 gr55.SetMarkerStyle(3)
###True points for high mass
 gr66=get_true_points(ROOT.TFile("result_high.root"),type=type)
 gr66.SetLineColor(1)
 gr66.SetMarkerColor(4)
 gr66.SetMarkerStyle(4)


 
 mg2= ROOT.TMultiGraph()
 mg2.SetName("Efficiency_Sig")
 mg2.Add(gr11)
 mg2.Add(gr22)
 mg2.Add(gr33)
 mg2.Add(gr44)
 mg2.Add(gr55)
 mg2.Add(gr66)
 mg2.Draw("ALP")
 mg2.GetXaxis().SetTitle("p_{T}(jet_{3}),[GeV/c]")
 mg2.GetYaxis().SetTitle("efficiency")
 mg2.GetYaxis().SetLabelOffset(0.01);

 mg2.GetYaxis().SetTitleOffset(1.3);
 mg2.GetXaxis().SetTitleOffset(1.2);


 c2.Modified()

 type="bkg_eff"

###Bkg Efficiency
 multifitBkgEff=create_multidim (ROOT.TFile("result.root"),"bkg_eff",output=interpolator)
# multifitBkgEff=create_multidim (ROOT.TFile("result_comb2.root"),"bkg_eff",output=interpolator)
 if "TMultiDimFit" in interpolator:
  multidim_config(multifitBkgEff)
  multidim_process(multifitBkgEff,type="bkg_eff")
 c3=ROOT.TCanvas("c3","Background Efficiency")

##Low mass
 gr111=plot_eff_3rdjet(multifitBkgEff,params12=[60,53],cut=[50,20,50],interpolator=interpolator)

##Medium mass
 gr222=plot_eff_3rdjet(multifitBkgEff,params12=[80,70],cut=[50,20,50],interpolator=interpolator)
 gr222.SetLineColor(3)
 gr222.SetMarkerColor(3)


##High mass
 gr333=plot_eff_3rdjet(multifitBkgEff,params12=[160,120],cut=[50,20,50],interpolator=interpolator)
 gr333.SetLineColor(4)
 gr333.SetMarkerColor(4)


###True points for low mass
 gr444=get_true_points(ROOT.TFile("result_low.root"),type=type)
 gr444.SetLineColor(1)
 gr444.SetMarkerStyle(3)
###True points for medium mass
 gr555=get_true_points(ROOT.TFile("result_medium.root"),type=type)
 gr555.SetLineColor(1)
 gr555.SetMarkerColor(3)
 gr555.SetMarkerStyle(3)
###True points for high mass
 gr666=get_true_points(ROOT.TFile("result_high.root"),type=type)
 gr666.SetLineColor(1)
 gr666.SetMarkerColor(4)
 gr666.SetMarkerStyle(4)
 

 mg3= ROOT.TMultiGraph()
 mg3.SetName("Efficiency_Bkg")
 mg3.Add(gr111)
 mg3.Add(gr222)
 mg3.Add(gr333)
 mg3.Add(gr444)
 mg3.Add(gr555)
 mg3.Add(gr666)
 mg3.Draw("ALP")
 mg3.GetXaxis().SetTitle("p_{T}(jet_{3}),[GeV/c]")
 mg3.GetYaxis().SetTitle("efficiency")
 mg3.GetYaxis().SetLabelOffset(0.01);

 mg3.GetYaxis().SetTitleOffset(1.3);
 mg3.GetXaxis().SetTitleOffset(1.2);


 c3.Modified()
  
 


 """  test(multifit)

 print "Test RBF"
 rbfi=create_multidim (ROOT.TFile("result.root"),type=type,output="Rbf")
 print get_result_multidimfit(rbfi,[107.08874,77.627258,24.829326],interpolator="Rbf")
 test(rbfi,[136.25308,95.458007,31.881153],interpolator="Rbf")
 test(rbfi,[107.08874,77.627258,24.829326],interpolator="Rbf")
 test_scenario(rbfi,interpolator="Rbf")


 print "Test TMultiDimFit" 
 rbfi2=create_multidim (ROOT.TFile("result.root"),type=type,output="TMultiDimFit")
 multidim_config(rbfi2)
 multidim_process(rbfi2,type=type)
 print get_result_multidimfit(rbfi2,[107.08874,77.627258,24.829326],interpolator="TMultiDimFit")
 test(rbfi2,[136.25308,95.458007,31.881153],interpolator="TMultiDimFit")
 test(rbfi2,[107.08874,77.627258,24.829326],interpolator="TMultiDimFit")
 test_scenario(rbfi2,interpolator="TMultiDimFit")

 """
 time.sleep(200)
