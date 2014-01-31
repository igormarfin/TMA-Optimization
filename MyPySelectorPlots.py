from ROOT import TPySelector, TProofOutputFile,TNtuple
import ROOT

import array

class MyPySelectorPlots( TPySelector ):
  def Begin( self ):
       print 'Main Constructor py: beginning'




  def SlaveBegin( self, tree ):
       print 'py: slave beginning'

       self.Reader=ROOT.TMVA.Reader()
       self.mva=""
       self.vars_Test={}
       self.dir=""
       self.fileXML=""
       self.cuts=""
       self.prefix="_S"

       self.plots=None     
       self.plots_before={} # before mva selection
       self.plots_after={}  # after mva selection   
 
       self.weightfiles=None
       self.weights={}
       self.numevt={}

       self.plots_before2={} # before mva selection
       self.plots_after2={}  # after mva selection   
 
    
       input=self.fInput
       if (input):
        self.weightfiles=input.FindObject("Weights")
        if (self.weightfiles!=None):
         for file in self.weightfiles:
          self.weights[file.GetName()]=float(file.GetTitle())       
          self.numevt[file.GetName()]=0e0
    
        self.mva=input.FindObject("Variables")

        self.prefix=input.FindObject("Prefix")
        if (self.prefix!=None): self.prefix=self.prefix.GetTitle()
   
        self.dir=input.FindObject("dir")
        if (self.dir!=None): self.dir=self.dir.GetTitle()
       
        self.fileXML=input.FindObject("fileXML")
        if (self.fileXML!=None): self.fileXML=self.fileXML.GetTitle()
   
        self.mva_method=input.FindObject("MVA")
        if (self.mva_method!=None): self.mva_method=self.mva_method.GetTitle()
   
        self.cuts=input.FindObject("CUT")
        if (self.cuts!=None): self.cuts=self.cuts.GetTitle()

        self.plots=input.FindObject("Plots")
        if (self.plots!=None): 
         for var in self.plots:
           th1bins=var.GetTitle()
           th1bins=th1bins.split(":")
           self.plots_before[var.GetName()]=ROOT.TH1F(var.GetName()+self.prefix+"_before", var.GetName(),int(th1bins[0]),float(th1bins[1]),float(th1bins[2]))
           self.plots_after[var.GetName()]=ROOT.TH1F(var.GetName()+self.prefix+"_after", var.GetName(),int(th1bins[0]),float(th1bins[1]),float(th1bins[2]))
           self.plots_before[var.GetName()].Sumw2()
           self.plots_after[var.GetName()].Sumw2()

           key1=str(var.GetName())
           self.plots_before2[key1]={}
           self.plots_after2[key1]={}
           k=int(0)
           for file in self.weightfiles:
#            print "1 adding file ", file.GetName()
            key2=str(file.GetName())
            obj=ROOT.TH1F(var.GetName()+self.prefix+"_before_%d"%k, var.GetName(),int(th1bins[0]),float(th1bins[1]),float(th1bins[2]))
            obj2=ROOT.TH1F(var.GetName()+self.prefix+"_after_%d"%k, var.GetName(),int(th1bins[0]),float(th1bins[1]),float(th1bins[2]))
#            print "key1=",key1
#            print "key2=",key2
#            print "obj=",obj
            self.plots_before2[key1].update({key2:obj}) 
            self.plots_after2[key1].update({key2:obj2}) 
#            self.plots_before2.update({key1:{key2:obj}}) 
            k+=1      
#            print "check  ", self.plots_before2
#            self.plots_after2[var.GetName()].update({file.GetName():ROOT.TH1F(var.GetName()+self.prefix+"_after_%d"%(k+1000), var.GetName()+self.prefix+"_after",int(th1bins[0]),float(th1bins[1]),float(th1bins[2]))})
            self.plots_before2[key1][key2].Sumw2()
            self.plots_after2[key1][key2].Sumw2()


         self.plots_after["mva"]=ROOT.TH1F("mva"+self.prefix+"_after", "mva",500,-2.4,2.4)
         self.plots_before["mva"]=ROOT.TH1F("mva"+self.prefix+"_before", "mva",500,-2.4,2.4)
         self.plots_before["mva"].Sumw2()
         self.plots_after["mva"].Sumw2()



 
         self.plots_before2["mva"]={}
         self.plots_after2["mva"]={}
   
         k=int(0)
         for file in self.weightfiles:
          key2=str(file.GetName())
          obj=ROOT.TH1F("mva"+self.prefix+"_before_%d"%k, "mva",500,-2.4,2.4)
          obj2=ROOT.TH1F("mva"+self.prefix+"_after_%d"%k, "mva",500,-2.4,2.4)          
          self.plots_before2["mva"].update({key2:obj}) 
          self.plots_after2["mva"].update({key2:obj2}) 
          self.plots_before2["mva"][key2].Sumw2()
          self.plots_after2["mva"][key2].Sumw2()
          k+=1

         

        
       if (not ( self.mva=="" or self.dir=="" or self.fileXML=="")):
         for var in self.mva:
          self.vars_Test[var.GetName()]=array.array('f',[0])
          if (not "weight" in var.GetName() ): self.Reader.AddVariable(var.GetName(), self.vars_Test[var.GetName()])
         self.Reader.BookMVA(self.mva_method,self.dir+self.fileXML)
       else: self.Reader = None
 


  def Process( self, entry ):
# get file name runtime
       
       f=self.fChain.GetTree().GetCurrentFile()
       filename=""
       if (f):    filename=f.GetName()
       else:
         ff=self.fChain.GetFile()
         if(ff):   filename=ff.GetName()
       
#       print "Current file=",filename
     
       if self.fChain.GetEntry( entry ) <= 0:
          return 0
       if self.Reader==None: return 0     
       for var in self.mva:
         if (not "weight" in var.GetName() ):     self.vars_Test[var.GetName()][0]=self.fChain.GetLeaf(var.GetName()).GetValue()

       self.numevt[filename]+=1e0
#       print "current numevt is ",  self.numevt[filename]       
       mvaout=self.Reader.EvaluateMVA(self.mva_method)
       _cut=self.cuts
       _cut = _cut.replace("cut",str(mvaout))
       _passMVA=int(ROOT.TFormula("fm",_cut).Eval(0e0));
#       print _cut
#       print _passMVA
       
       
       for var in self.plots_before:
#        print "self.plots_before2 = ", self.plots_before2[var]        
#        print "self.plots_before2 = ", self.plots_before2[var][filename]
         
        if (var == "mva"):   
#         self.plots_before[var].Fill(mvaout,self.fChain.weight)
         a=self.plots_before2[var][filename].Fill(mvaout,self.fChain.weight)
        else: 
#         self.plots_before[var].Fill(self.fChain.GetLeaf(var).GetValue(),self.fChain.weight)
         self.plots_before2[var][filename].Fill(self.fChain.GetLeaf(var).GetValue(),self.fChain.weight)
#         print "test ",self.plots_before2[var][filename].Integral()

        
        if (_passMVA>0): 
         if (var == "mva"):   
#          self.plots_after[var].Fill(mvaout,self.fChain.weight)
          self.plots_after2[var][filename].Fill(mvaout,self.fChain.weight)
         else: 
#          self.plots_after[var].Fill(self.fChain.GetLeaf(var).GetValue(),self.fChain.weight)
          self.plots_after2[var][filename].Fill(self.fChain.GetLeaf(var).GetValue(),self.fChain.weight)      
        
       

       return 1



  def SlaveTerminate( self ):
       print 'py: slave terminating'
       
       for var  in self.plots_before: 
#        self.GetOutputList().Add(self.plots_before[var].Clone(self.plots_before[var].GetName()))
#        self.GetOutputList().Add(self.plots_after[var].Clone( self.plots_after[var].GetName())))
        clone_before=self.plots_before[var].Clone(self.plots_before[var].GetName())
        clone_after=self.plots_after[var].Clone(self.plots_after[var].GetName())
        clone_before.Reset()
        clone_after.Reset()
        for file in self.weights:
         if (self.numevt[file]==0): continue
         print "file in terminate = ",file
         if (self.weights[file]>0):
          clone_before.Add(self.plots_before2[var][file], self.weights[file]/self.numevt[file])
          clone_after.Add(self.plots_after2[var][file], self.weights[file]/self.numevt[file])
          print "do weighting"
         else:
           clone_before.Add(self.plots_before2[var][file])
           clone_after.Add(self.plots_after2[var][file])
           print "no do weighting"
         print "var=",var," file=",file," integ=", clone_before.Integral() ," numevt=",self.numevt[file]," total evt=",self.weights[file]," weight=",self.weights[file]/self.numevt[file]
        self.GetOutputList().Add(clone_before)
        self.GetOutputList().Add(clone_after)
       
       for item in self.GetOutputList():
         print '  +',item.GetName()



  def Terminate( self ):
       print 'py: terminating'
       for item in self.GetOutputList():
          print '  <>',item.GetName()

