from ROOT import TPySelector, TProofOutputFile,TNtuple
import ROOT

import array

class MyPySelector( TPySelector ):
  def Begin( self ):
       print 'Main Constructor py: beginning'




  def SlaveBegin( self, tree ):
       print 'py: slave beginning'

       self.th1S=None
       self.th1B=None
       self.Reader=ROOT.TMVA.Reader()
       self.mva=""
       self.vars_Test={}
       self.dir=""
       self.fileXML=""
       input=self.fInput
       if (input):
        self.th1S=input.FindObject("mva_Test_S")
        self.th1B=input.FindObject("mva_Test_B")
        self.mva=input.FindObject("Variables")
        self.dir=input.FindObject("dir")
        if (self.dir!=None): self.dir=self.dir.GetTitle()
        self.fileXML=input.FindObject("fileXML")
        if (self.fileXML!=None): self.fileXML=self.fileXML.GetTitle()
        self.mva_method=input.FindObject("MVA")
        if (self.mva_method!=None): self.mva_method=self.mva_method.GetTitle()
       if (not ( self.mva=="" or self.dir=="" or self.fileXML=="")):
         for var in self.mva:
          self.vars_Test[var.GetName()]=array.array('f',[0])
          if (not "weight" in var.GetName() ): self.Reader.AddVariable(var.GetName(), self.vars_Test[var.GetName()])
         self.Reader.BookMVA(self.mva_method,self.dir+self.fileXML)
       else: self.Reader = None
 


  def Process( self, entry ):
# get file name runtime
       """
       f=self.fChain.GetTree().GetCurrentFile()
       if (f):
         print f.GetName()
       else:
         ff=self.fChain.GetFile()
         if(ff):
          print  ff.GetName()
       print "Current file=",self.fChain.GetTree().GetCurrentFile().GetName()
       """
       if self.fChain.GetEntry( entry ) <= 0:
          return 0
       if self.Reader==None: return 0     
       for var in self.mva:
         if (not "weight" in var.GetName() ):     self.vars_Test[var.GetName()][0]=self.fChain.GetLeaf(var.GetName()).GetValue()
       
#       mvaout=self.Reader.EvaluateMVA(self.mva_method,self.fChain.weight)
       mvaout=self.Reader.EvaluateMVA(self.mva_method)
#       print "mva=",mvaout
       if (self.th1S): self.th1S.Fill(mvaout,self.fChain.weight)
       if (self.th1B): self.th1B.Fill(mvaout,self.fChain.weight)
#       if (self.th1S): self.th1S.Fill(mvaout)
#       if (self.th1B): self.th1B.Fill(mvaout)
#       print "D=",self.vars_Test["D"][0]
#       print "weight=",self.vars_Test["weight"][0]

       return 1



  def SlaveTerminate( self ):
       print 'py: slave terminating'
#       print "self.th1S=",self.th1S
#       print "self.th1B=",self.th1B
       if (self.th1S!=None):  
        self.GetOutputList().Add(self.th1S.Clone("mva_Test_S"))
       if (self.th1B!=None):  self.GetOutputList().Add(self.th1B.Clone("mva_Test_B"))
       for item in self.GetOutputList():
         print '  +',item.GetName()

  def Terminate( self ):
       print 'py: terminating'
 #      res=self.GetOutputList().FindObject("result")
 #      if (res):
 #        print "j0 ",res.GetBinContent(1)
 #        print "j1 ",res.GetBinContent(2)
 #        print "j2 ",res.GetBinContent(3)     
       for item in self.GetOutputList():
          print '  <>',item.GetName()

