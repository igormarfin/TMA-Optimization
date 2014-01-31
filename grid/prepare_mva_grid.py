#! /usr/bin/env python


"""a set of utils to prepare for mva traininig and 
   to test the obtained results

"""
__author__ =  'Igor Marfin'
__version__=  '1.7'
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
import subprocess

import os.path

parser=OptionParser(usage="""

        usage: %prog  [--run] 

        example of run:  %prog --run --nonbatch
        example of run:  %prog --vars --nonbatch
        example of run:  %prog --optimiationMVA --nonbatch

"""
)


parser.add_option("--vars",dest="vars",default=False,action="store_true")
parser.add_option("--optimiationMVA",dest="optimiationMVA",default=False,action="store_true")
parser.add_option("--run",dest="run",default=False,action="store_true")
parser.add_option("--prepare_samples",dest="prepare_samples",default=False,action="store_true")
parser.add_option("--download_mva_dcache",dest="download_mva_dcache",default=False,action="store_true")
parser.add_option("--download_mva_dcache_v2",dest="download_mva_dcache_v2",default=False,action="store_true")
parser.add_option("--nonbatch",dest="nonbatch",default=True,action="store_false")
(options,args)=parser.parse_args()


#set batch mode
sys.argv.append('-b-')
import ROOT
ROOT.gROOT.SetBatch(True)
sys.argv.remove('-b-')

import  fnmatch
import cPickle as pickle
import zlib



###Settings

trees_path="/data/user/marfin/CMSSW_5_3_3/src/Analysis/HbbMSSMAnalysis/test/Analysis2012/tmva_training_v4/batch"


#v8
tanb=20.
democtratic_mix=True
dcachepath="srm://dcache-se-cms.desy.de/pnfs/desy.de/cms/tier2/store/user/marfin/Higgs/BBbar/Analysis2012/CMSSW_535/"
dcachepathMVA="srm://dcache-se-cms.desy.de/pnfs/desy.de/cms/tier2/store/user/marfin/Higgs/BBbar/Analysis2012/CMSSW_535/MVA_Trees_v8/"

doReweight=False
doXsect=False
doNumEvt=False
doLumiWeight=False



#v8
mass_for_mix=200.
mass=["*M-140-KinVarsBDT.root*","*M-200-KinVarsBDT.root*","*M-350-KinVarsBDT.root*"]

BkgOvertrain=["*GeneralQCD-KinVarsBDT.root*"]
ptbins=["*bEnrichQCD-KinVarsBDT.root*"]




mva_method="BDT"
tree_name="KinVarsBDT"



# new variable since v3!
# do correct scenario selection 
scenario_template=""


def Download_MVA_Trees_From_DCACHE():

  """ copy all mva trees from dCache to current directory

   all MVA directories were copied to dCache in the way
   
   ls -d */ | grep "_v5" | xargs -I {} echo "find {} -iname \"Triple*root\" "| sh | xargs -I {} echo "echo {}; lcg-cp -D srmv2  file:/\`pwd\`/{} srm://dcache-se-cms.desy.de/pnfs/desy.de/cms/tier2/store/user/marfin/Higgs/BBbar/Analysis2012/CMSSW_535/MVA_Trees_v5/{}" |sh

  """

  cmd="./copySrmFilesSubFolder %s %s %s %s"

  # we are going to copy only updated root files for 
 # os.system(cmd%(dcachepathMVA,"MEDIUM","update","root"))
 
  os.system(cmd%(dcachepathMVA,"root","root","root"))  

 #2nd attempt if lcg-ls failed
  cmd="./copySrmFilesSubFolder_v2 %s %s %s %s"
  p=subprocess.Popen("find . -iname \"*.root\"",  stdout=subprocess.PIPE, shell=True)
  rootfiles,err=p.communicate()
  if (rootfiles==""):
   print "2nd attempt to download"
   os.system(cmd%(dcachepathMVA,"root","root","root"))
  

#  for m in mass:
#   os.system(cmd%(dcachepathMVA,"MEDIUM",m,"root"))
#
#  for ptbin in ptbinspattern:
#   os.system(cmd%(dcachepathMVA,"MEDIUM",ptbin,"root"))

  return

def Download_MVA_Trees_From_DCACHE_v2():

  """ copy all mva trees from dCache to current directory

   all MVA directories were copied to dCache in the way
   
   ls -d */ | grep "_v5" | xargs -I {} echo "find {} -iname \"Triple*root\" "| sh | xargs -I {} echo "echo {}; lcg-cp -D srmv2  file:/\`pwd\`/{} srm://dc$

  """

 #2nd attempt if lcg-ls failed
  cmd="./copySrmFilesSubFolder_v2 %s %s %s %s"
  print "2nd attempt to download"
  os.system(cmd%(dcachepathMVA,"root","root","root"))
  


  return


def Prepare_samples():

 """ copy all needed samples from dCache """
 
 cmd="""lcg-ls "%s" | egrep  "%s" | xargs -I {} echo " mkdir -m o=rwx \`basename {}\`; cd \`basename {}\`; ../copySrmFiles \\\"%s\`basename {}\`\\\" ; cd -; " |sh """

 for signal in mass:  os.system(cmd%(dcachepath,signal.replace("*",".*"),dcachepath))
 for ptbin in ptbins:  os.system(cmd%(dcachepath,ptbin.replace("*",".*"),dcachepath))

 return




def FindPostionMinMax(mva_method="",varName="var1"):

 if (len(mva_method)<=0) : return None
 f=open(mva_method+"_result"+".gz",'rb')
 data=zlib.decompress(f.read())
 results=pickle.loads(data)

 results=sorted(results,key=lambda x: x[2] ,reverse=True)
 results=[x for x in results if not x[0] == "000000"]
 vals=[]
 varNum=-1
 for result in results:
  vars=result[1].items()
  for var in range(len(vars)):
   if vars[var][0] == varName: 
    varNum=var
    vals.append(vars[var][1])

 vals=sorted(vals,key=lambda x: x ,reverse=True)
 return (varNum,vals[-1],vals[0])


def PrintVariableNames(mva_method="",returnList=False):
 if (len(mva_method)<=0) : return None
 f=open(mva_method+"_result"+".gz",'rb')
 data=zlib.decompress(f.read())
 results=pickle.loads(data)
 f.close()
 results=sorted(results,key=lambda x: x[2] ,reverse=True)
 results=[x for x in results if not x[0] == "000000"]
 vars=results[0][1].items()
 res=[] 
 for var in range(len(vars)):
  if (not returnList): print "variable %d : %s"%(var,vars[var][0])
  else: res.append(vars[var][0])
 if (returnList): return res
 return None



def GetNumPoints(mva_method=""):
 if (len(mva_method)<=0) : return None
 f=open(mva_method+"_result"+".gz",'rb')
 data=zlib.decompress(f.read())
 results=pickle.loads(data)

 results=sorted(results,key=lambda x: x[2] ,reverse=True)
 results=[x for x in results if not x[0] == "000000"]

 return len(results)


def GetOptimalPoint(mva_method=""):
 """ return optimal point """

 result=FindOptimalResult(mva_method)
 if len(result) ==0 : return None

 return [x[1] for x in result[1].items()]

def GetOptimalValue(mva_method=""):
 """ return optimal value """

 result=FindOptimalResult(mva_method)
 if len(result) ==0 : return None

 return result[2]



def id():
 """return id"""
 
 return "%06d" % int(random.uniform(1,1e6))

def CreateResultDB(mva_method=""):
 """ create DB for storing results """
 if (len(mva_method)<=0): return
  
 vars={}
 separation=0.
 signKS=0.
 bkgKS=0.
 id="000000"
 results=[(id,vars,separation,signKS,bkgKS)]

# pickle.dump(configs, mva_method+".pkl")
 f=open(mva_method+"_result"+".gz","wb")
 f.write(zlib.compress(pickle.dumps(results, pickle.HIGHEST_PROTOCOL),9))
 f.close()

 return


def CreateConfigDB(mva_method=""):
 """ create configs 
 for mva_method
 """

 exclude_list=[]
 exclude_file=""
 option_book_list=[]
 option_book_file=""
 option_train_list=[]
 option_train_file=""

 if (mva_method=="BDT"):
  exclude_file=""
  option_book_file=""
  option_train_file=""

#  exclude_file="exclude_bdt.lst"
#  option_book_file="options_book_BDT.lst"
#  option_train_file="options_train_test_20k.lst"

 #creating lists
 if (len(exclude_file)>0):
  f=open(exclude_file,'r')
  exclude_list=f.readlines()
  f.close()

 if (len(option_book_file)>0):
  f=open(option_book_file,'r')
  option_book_list=f.readlines()
  f.close()

 if (len(option_train_file)>0):
  f=open(option_train_file,'r')
  option_train_list=f.readlines()
  f.close()

 # save to db

# _id=id()
 _id="000000"
 configs=[(_id,exclude_list,option_book_list,option_train_list)]
# pickle.dump(configs, mva_method+".pkl")
 f=open(mva_method+"_config"+".gz","wb")
 f.write(zlib.compress(pickle.dumps(configs, pickle.HIGHEST_PROTOCOL),9))
 f.close()


def UntarMVATestOutput():
 """ untar test mva root files and weight xml from TMVA trained in grid """

 os.system("ls result_*tgz | xargs -I {} echo \" echo {};  tar -xf {} \" | sh " ) 

 return

def MergeDB(mva_method,db1_path="",db2_path=""):
 """ do merging of two db for configs and results if it's possible """

 path1=db1_path
 path2=db2_path

 if (len(mva_method)<=0) : return
 if (len(db1_path)<=0) : path1="./"
 if (len(db2_path)<=0) : path2="./"
 
 if (path1==path2): return
 
 doMergeResults=False
 doMergeConfigs=False

 if (os.system("ls "+path1+mva_method+"_config"+".gz")==0 and  os.system("ls "+path2+mva_method+"_config"+".gz")==0 ):
  doMergeConfigs=True
 if (os.system("ls "+path1+mva_method+"_result"+".gz")==0 and  os.system("ls "+path2+mva_method+"_result"+".gz")==0 ):
  doMergeResults=True


 if (doMergeConfigs):
  f=open(path1+mva_method+"_config"+".gz",'rb')
  data=zlib.decompress(f.read())
  configs1=pickle.loads(data)
  f.close()
  f=open(path2+mva_method+"_config"+".gz",'rb')
  data=zlib.decompress(f.read())
  configs2=pickle.loads(data)
  f.close()

# do fitltering here

  ids1=[x[0] for x in configs1]
  configs2=[ x for x in configs2 if not x[0] in ids1]

  f=open(path1+mva_method+"_config"+".gz",'wb')
  f.write(zlib.compress(pickle.dumps(configs1+configs2, pickle.HIGHEST_PROTOCOL),9))
  f.close()


 if (doMergeResults):
  f=open(path1+mva_method+"_result"+".gz",'rb')
  data=zlib.decompress(f.read())
  configs1=pickle.loads(data)
  f.close()
  f=open(path2+mva_method+"_result"+".gz",'rb')
  data=zlib.decompress(f.read())
  configs2=pickle.loads(data)
  f.close()

# do fitltering here

  ids1=[x[0] for x in configs1]
  configs2=[ x for x in configs2 if not x[0] in ids1]

  f=open(path1+mva_method+"_result"+".gz",'wb')
  f.write(zlib.compress(pickle.dumps(configs1+configs2, pickle.HIGHEST_PROTOCOL),9))
  f.close()

 return




def MergeConfigs(mva_method,path=""):
 """ do merging configs obtained from grid jobs """

 if (len(mva_method)<=0) : return


 # merge configs
 p = subprocess.Popen("ls "+path+mva_method+"_config"+".gz" ,  stdout=subprocess.PIPE, shell=True)
 main_db,err=p.communicate()

 p=subprocess.Popen("ls "+path+mva_method+"_config_"+"*.gz" ,  stdout=subprocess.PIPE, shell=True)
 all_db,err=p.communicate()
 all_db=all_db.split('\n')
 all_configs=[]
 if (len(main_db)<=0 and len(all_db)>0):
  os.system("mv "+all_db[0]+" "+path+mva_method+"_config"+".gz")
  all_db=all_db[1:]

 f=open(path+mva_method+"_config"+".gz",'rb')
 data=zlib.decompress(f.read())
 all_configs=pickle.loads(data)
 f.close()

 for _db in all_db:
  if (len(_db)<=0): continue
  f=open(_db,'rb')
  data=zlib.decompress(f.read())
# do fitltering here
  ids1=[x[0] for x in all_configs]
  configs2=pickle.loads(data)
  configs2=[ x for x in configs2 if not x[0] in ids1]
  all_configs+=configs2
  f.close()


 f=open(path+mva_method+"_config"+".gz",'wb')
 f.write(zlib.compress(pickle.dumps(all_configs, pickle.HIGHEST_PROTOCOL),9))
 f.close()

 return

def MergeResults(mva_method,path=""):
 """ do merging configs obtained from grid jobs """

 if (len(mva_method)<=0) : return

 # merge results
 p = subprocess.Popen("ls "+path+mva_method+"_result"+".gz" ,  stdout=subprocess.PIPE, shell=True)
 main_db,err=p.communicate()

 p=subprocess.Popen("ls "+path+mva_method+"_result_"+"*.gz" ,  stdout=subprocess.PIPE, shell=True)
 all_db,err=p.communicate()
 all_db=all_db.split('\n')
 all_configs=[]
 if (len(main_db)<=0 and len(all_db)>0):
  os.system("mv "+all_db[0]+" "+path+mva_method+"_result"+".gz")
  all_db=all_db[1:]

 f=open(path+mva_method+"_result"+".gz",'rb')
 data=zlib.decompress(f.read())
 all_configs=pickle.loads(data)
 f.close()

 for _db in all_db:
  if (len(_db)<=0): continue
  f=open(_db,'rb')
  data=zlib.decompress(f.read())
# do fitltering here
  ids1=[x[0] for x in all_configs]
  configs2=pickle.loads(data)
  configs2=[ x for x in configs2 if not x[0] in ids1]
  all_configs+=configs2
  f.close()


 f=open(path+mva_method+"_result"+".gz",'wb')
 f.write(zlib.compress(pickle.dumps(all_configs, pickle.HIGHEST_PROTOCOL),9))
 f.close()


 return


def Check_TMVA_outputGzipped(mva_method,id,path="./"):
 """ return True if the TMVA_"mva_method"_id.root is somewhere in the dCache gizpped. 
      It looks through the 'dcache_scratch' file entries to find real paths for download.
     Also, files of names like  root_files_* are needed to find the TMVA_mva_method_id.root file 
 """

 if len(mva_method)*len(id)<=0 : return False
   
 p=subprocess.Popen("ls "+path+"root_files_*" ,  stdout=subprocess.PIPE, shell=True)
 root_info,err=p.communicate()
 root_info=root_info.split('\n')
 root_info_needed=""
 for info in root_info:
  if (len(info)<=0): continue
  p=subprocess.Popen("cat "+ info ,  stdout=subprocess.PIPE, shell=True)
  tmvafiles,err=p.communicate()
  tmvafiles=tmvafiles.split('\n')
  for tmvafile in tmvafiles:
    if (len(tmvafile)<=0): continue
    if (tmvafile == "TMVA_"+mva_method+"_"+id+".root"):
       root_info_needed=info
       break

  if (len(root_info_needed)>0): break
 
 print "root_info_needed=",root_info_needed
 if len(root_info_needed)>0 : return True

 return False


def Download_TMVA_outputGzipped(mva_method,id,path="./"):
 """ download TMVA outputs in root files from dcache.
     It looks through the 'dcache_scratch' file entries to find real paths for download.
     Also, files of names like  root_files_* are needed to find the TMVA_mva_method_id.root file  """	
 """ """
 
 if len(mva_method)*len(id)<=0 : return 

 

 p = subprocess.Popen("ls "+path+"TMVA_"+mva_method+"_"+id+".root",  stdout=subprocess.PIPE, shell=True)
 myfile,err=p.communicate()
 if (len(myfile)>0): return path+"TMVA_"+mva_method+"_"+id+".root"

 p=subprocess.Popen("ls "+path+"root_files_*" ,  stdout=subprocess.PIPE, shell=True)
 root_info,err=p.communicate()
 root_info=root_info.split('\n')
 root_info_needed=""
 for info in root_info:
  if (len(info)<=0): continue
  p=subprocess.Popen("cat "+ info ,  stdout=subprocess.PIPE, shell=True)
  tmvafiles,err=p.communicate()
  tmvafiles=tmvafiles.split('\n')
  for tmvafile in tmvafiles:
    if (len(tmvafile)<=0): continue
    if (tmvafile == "TMVA_"+mva_method+"_"+id+".root"): 
       root_info_needed=info
       break

  if (len(root_info_needed)>0): break
 print "root_info_needed=",root_info_needed
 if len(root_info_needed)<=0 : return
 crabid=root_info_needed.split("_")
 crabid=crabid[2]+"_"+crabid[3]+"_"+crabid[4] 
 print "crabid =",crabid

 p = subprocess.Popen("ls "+path+"result_"+crabid+".tgz",  stdout=subprocess.PIPE, shell=True)
 myfile,err=p.communicate()
 if (len(myfile)>0): 
   cmd="cd "+path+" ; tar -xf result_"+crabid+".tgz  TMVA_"+mva_method+"_"+id+".root;"
   return path+"TMVA_"+mva_method+"_"+id+".root"


 cmd="cat " +path + "dcache_scratch | grep \"_path_\" | awk '{print $2}'"
 p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
 paths,err=p.communicate()
 paths=paths.split('\n')
 needed_path=""
 tgzfile=""
 for _path in paths:
  if len(_path)<=0 : continue
  print "current dCache path ",_path
  cmd="cd "+path+"; ./copySrmFiles "+_path+ "  result_"+crabid+".tgz"
  p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
  crabfiles,err=p.communicate()
  if len(crabfiles)>0: 
   print "Is "+  "result_"+crabid+".tgz"  +" copied? "
   p = subprocess.Popen("ls "+path+"result_"+crabid+".tgz",  stdout=subprocess.PIPE, shell=True)
   tgzfile,err=p.communicate()
   print "tgzfile=",tgzfile
   if (len(tgzfile)>0): 
    print "it's copied"
    break
 if (len(tgzfile)<=0): return
 cmd="cd "+path+" ; tar -xf result_"+crabid+".tgz  TMVA_"+mva_method+"_"+id+".root;   rm result_"+crabid+".tgz" 
 p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
 
 return path+"TMVA_"+mva_method+"_"+id+".root"



def ProcessVariables(order="Correlation",varstable=[],doSelection=False,doInversion=False):
 """ test all variables """

 democtratic_xsect=GetXSection(tanb,mass_for_mix)

 signal_files=[]
 files=[ GetListFiles(trees_path+"/*"+m+scenario_template.replace(".root","_update.root"),trees_path) for m in mass ]
 if os.path.exists(files[0][0] ):
  for item in files: signal_files+=item
 else:
  files=[ GetListFiles(trees_path+"/*"+m+scenario_template,trees_path) for m in mass ]
  for item in files:
 #  print item
   if (len(item)==0): continue
   (item,masses)=GetMassFromName(item)
   (item,numevts)=GetNumEvt(item)
   (item,lumiwgts)=GetLumiWeight(item)
   if (democtratic_mix):
    xsects=map(lambda x:  democtratic_xsect,masses)
   else:
    xsects=map(lambda x:  GetXSection(tanb,float(x)),masses)
   newwgts=GetNewWeight(1e3,lumiwgts,numevts,xsects)
   filesnew=map(lambda x: item[x].replace(".root","_update.root") ,range(len(item)))
   if (not os.path.exists(filesnew[0])):   ReWeight(tree_name='KinVarsBDT', list_of_files=item, weight=newwgts)
   signal_files+=filesnew



 # background processing
 bkg_files=[]
 files=[ GetListFiles(trees_path+"/*"+ptbin+scenario_template.replace(".root","_update.root"),trees_path) for ptbin in ptbins ]
 if os.path.exists(files[0][0]):
  for item in files: bkg_files+=item
 else:
  files=[ GetListFiles(trees_path+"/*"+ptbin+scenario_template,trees_path) for ptbin in ptbins ]
  for item in files:
 #  print item
   if (len(item)==0): continue
   (item,numevts)=GetNumEvt(item)
   (item,lumiwgts)=GetLumiWeight(item)
   newwgts=GetNewWeight(1e3,lumiwgts,numevts)
   filesnew=map(lambda x: item[x].replace(".root","_update.root") ,range(len(item)))
   if (not os.path.exists(filesnew[0])):   ReWeight(tree_name='KinVarsBDT', list_of_files=item, weight=newwgts)
   bkg_files+=filesnew


 (cor_sig,cor_bkg,ks,varnames)=GetVariableProperties(signal_files,bkg_files)
 print "\n\n\nRanking begins\n\n\n"
 varproperties=Ranking(cor_sig,cor_bkg,ks,order,varstable,doSelection,doInversion)
 if (doSelection):
  return varproperties
 else:
  return varnames


def GetVariableProperties(signal_files=[],bkg_files=[],tree_name="KinVarsBDT",exclude="exclude_for_testing_properties.lst"):

 """ the code tries to define the similarity between signal and background """




 if (len(tree_name)*len(signal_files)*len(bkg_files)<=0): return


 exclude_list=[]
 if  (len(exclude)>0 ):
  f=open(exclude,'r')
  exclude_list=f.readlines()

 exclude_list=map(lambda x: x.strip(), exclude_list)
 
 exclude_list.append("mva")
 exclude_list.append("weight")

 chain_sig=ROOT.TChain(tree_name)

 sig_variables=[]
 correlation_sig=[]
 sig_vars=[]

 chain_bkg=ROOT.TChain(tree_name)

 bkg_variables=[]
 correlation_bkg=[]
 bkg_vars=[]




 for file in signal_files:
  chain_sig.Add(file)
 branches = chain_sig.GetListOfBranches()
 for branch in branches:
  var=branch.GetName()
  if ( len([s for s in exclude_list if var == s])==0 ): sig_variables.append(var)

 for file in bkg_files:
  chain_bkg.Add(file)
 branches = chain_bkg.GetListOfBranches()
 for branch in branches:
  var=branch.GetName()
  if ( len([s for s in exclude_list if var == s])==0 ): bkg_variables.append(var)

 assert(sig_variables == bkg_variables)


 if (os.path.isfile("./"+tree_name+"_variable.gz")):
  f=open(tree_name+"_variable"+".gz","rb")
  data=zlib.decompress(f.read())
  variables=pickle.loads(data)
  return (variables[0],variables[1],variables[2],sig_variables)



# signal processing

 for i in range(len(sig_variables)):

  min_i=min(chain_sig.GetMinimum(sig_variables[i]), chain_bkg.GetMinimum(bkg_variables[i]))
  max_i=max(chain_sig.GetMaximum(sig_variables[i]), chain_bkg.GetMaximum(bkg_variables[i]))

  _tmph1=ROOT.TH1D(sig_variables[i]+"_s",sig_variables[i]+"_s",50,min_i,max_i)
  chain_sig.Draw(sig_variables[i]+">>"+sig_variables[i]+"_s")
  sig_vars.append(_tmph1)
  for j in range(i+1,len(sig_variables)):

   min_j=min(chain_sig.GetMinimum(sig_variables[j]), chain_bkg.GetMinimum(bkg_variables[j]))
   max_j=max(chain_sig.GetMaximum(sig_variables[j]), chain_bkg.GetMaximum(bkg_variables[j]))

   _tmph2=ROOT.TH2D("_tmph2"+sig_variables[i]+sig_variables[j]+"_s","_tmph2",50,min_i, max_i, 50,min_j,max_j)
   chain_sig.Draw(sig_variables[i]+":"+ sig_variables[j]+">>_tmph2"+sig_variables[i]+sig_variables[j]+"_s","weight")
   correlation_sig.append([sig_variables[i],sig_variables[j],_tmph2.GetCorrelationFactor()])

# bkg processing

 for i in range(len(bkg_variables)):
  min_i=min(chain_sig.GetMinimum(sig_variables[i]), chain_bkg.GetMinimum(bkg_variables[i]))
  max_i=max(chain_sig.GetMaximum(sig_variables[i]), chain_bkg.GetMaximum(bkg_variables[i]))


  _tmph1=ROOT.TH1D(sig_variables[i]+"_b",bkg_variables[i]+"_b",50,min_i,max_i)

  chain_bkg.Draw(bkg_variables[i]+">>"+bkg_variables[i]+"_b")
  bkg_vars.append(_tmph1)
  for j in range(i+1,len(bkg_variables)):

   min_j=min(chain_sig.GetMinimum(sig_variables[j]), chain_bkg.GetMinimum(bkg_variables[j]))
   max_j=max(chain_sig.GetMaximum(sig_variables[j]), chain_bkg.GetMaximum(bkg_variables[j]))

   _tmph2=ROOT.TH2D("_tmph2"+sig_variables[i]+sig_variables[j]+"_b","_tmph2",50,min_i, max_i, 50,min_j,max_j)
   chain_bkg.Draw(sig_variables[i]+":"+ sig_variables[j]+">>_tmph2"+sig_variables[i]+sig_variables[j]+"_b","weight")

   correlation_bkg.append([bkg_variables[i],bkg_variables[j],_tmph2.GetCorrelationFactor()])



 assert(len(bkg_vars) == len(sig_vars))

 KS=[]

 for i in range(len(sig_vars)):
  dist=sig_vars[i].KolmogorovTest(bkg_vars[i],"M N")
  sig_int=sig_vars[i].Integral()
  bkg_int=bkg_vars[i].Integral()

  KS.append([bkg_variables[i],dist])


 if (not os.path.isfile("./"+tree_name+"_variable.gz")):
  f=open(tree_name+"_variable"+".gz","wb")
  f.write(zlib.compress(pickle.dumps((correlation_sig,correlation_bkg,KS), pickle.HIGHEST_PROTOCOL),9))
  f.close()

 return (correlation_sig,correlation_bkg,KS,sig_variables)


def Ranking(correlation_sig=[],correlation_bkg=[],KS=[],order="Correlation",varstable=[],doSelection=False,doInversion=False):

 """ do ranking variables """
 if (len(KS)*len(correlation_sig)*len(correlation_bkg)<=0): return

 totalCorr_sig={}
 totalCorr_bkg={}

 vars=[i[0] for i in KS]



 for var in vars:

  corr_sigs=filter(lambda x: x[0]==var or x[1]==var, correlation_sig)
  corr_sig=sum(map(lambda x: math.pow(abs(x[2]),2),corr_sigs))
  totalCorr_sig[var]=math.sqrt(corr_sig)


  corr_bkgs=filter(lambda x: x[0]==var or x[1]==var, correlation_bkg)
  corr_bkg=sum(map(lambda x: math.pow(abs(x[2]),2),corr_bkgs))
  totalCorr_bkg[var]=math.sqrt(corr_bkg)


 totalCorr_sig=sorted([(value,key) for (key,value) in totalCorr_sig.items()])
 totalCorr_sig=tuple([(x[1],x[0]) for x in totalCorr_sig])


 totalCorr_bkg=sorted([(value,key) for (key,value) in totalCorr_bkg.items()])
 totalCorr_bkg=tuple([(x[1],x[0]) for x in totalCorr_bkg])

# do sorting of KS

 KS=sorted(KS,key=lambda x: x[1],reverse=True)

 #prepare_mva.ProcessVariables("ks_0.06_corr_0.30") as an example
 if ( "ks_" in order and  "_corr_" in order):
  settings=order.split("_")
  print "Select all vars with KS >= %f and correlation among them <=%f"%(float(settings[1]),float(settings[3]))


  KS_output=[]
  KS_delete=[]
  KS_high = filter(lambda x: x[1]>= float(settings[1]), KS)
  for i in range(len(KS_high)):
   KS_output.append(KS_high[i])
   if KS_high[i] in  KS_delete : continue
   for j in range(i+1,len(KS_high)):


    KS_corr =filter(lambda x: ( x[0]==KS_high[i][0] and x[1]==KS_high[j][0]) or (x[0]==KS_high[j][0] and x[1]==KS_high[i][0]), correlation_sig)
    if abs(KS_corr[0][2])>float(settings[3]):
     KS_delete.append(KS_high[j])


  KS_output=[s for s in KS_output if not s in KS_delete ]
  KS_inversed=[]
  for  k in KS:
   if not k in KS_output:
    KS_inversed.append(k)
  if (doSelection and not doInversion): return KS_output
  if (doSelection and doInversion): return KS_inversed


 if (order=="Correlation"):
  if (doSelection and not doInversion): return totalCorr_sig


 if (order=="KS"):
  if (doSelection): return  KS

 return None



def ReadConfigs(mva_method):
 """ read configs from gzipped db """

 if (len(mva_method)<=0) : return
 f=open(mva_method+"_config"+".gz",'rb')
 data=zlib.decompress(f.read()) 
 configs=pickle.loads(data)
 
 return configs

def ReadResults(mva_method):
 """ read results from gzipped db """

 if (len(mva_method)<=0) : return
 f=open(mva_method+"_result"+".gz",'rb')
 data=zlib.decompress(f.read())
 results=pickle.loads(data)

 return results


def UploadResult(mva_method,result):
 """ ipload  results to DB"""

 if (len(mva_method)*len(result)<=0): return
 if (not isinstance(result,tuple) ) : return

 if ( list(result).count(None)>0) : return

 
 f=open(mva_method+"_result"+".gz",'rb')
 data=zlib.decompress(f.read())
 results=pickle.loads(data)
 results.append(result)


# pickle.dump(configs, mva_method+".pkl")
 f=open(mva_method+"_result"+".gz","wb")
 f.write(zlib.compress(pickle.dumps(results, pickle.HIGHEST_PROTOCOL),9))
 f.close()

 return


def UpLoadConfig(mva_method,config):
 """ upload a new record to db """

 if (len(mva_method)*len(config)<=0): return
 if (not isinstance(config,tuple) ) : return

 if ( list(config).count(None)>0) : return


 f=open(mva_method+"_config"+".gz",'rb')
 data=zlib.decompress(f.read())
 configs=pickle.loads(data)
 f.close()
# _id=id()
# configs.append((_id,)+config)
 configs.append(config)
 f=open(mva_method+"_config"+".gz",'wb')
 f.write(zlib.compress(pickle.dumps(configs, pickle.HIGHEST_PROTOCOL),9))
 f.close()




def CreateConfig(mva_method="",_doOptimization=False,_myvars={}):
 """ create a new config """

 exclude_list=[]
 exclude_file=""
 option_book_list=[]
 option_book_file=""
 option_train_list=[]
# option_train_file=""
# option_train_file="options_train_test_20k.lst"
 option_train_file="options_train_test_100k.lst"

 _id=id()
 _vars={}
 myvars={}
 doOptimization=False
 if (_doOptimization):
  doOptimization=True
  myvars=_myvars

 if (mva_method=="BDT"):  
### exclude list
#  exclude_file="exclude_bdt.lst"
#  exclude_file="exclude_loose2.lst"

#  exclude_file="exclude_many_vars.lst"
#  f=open(exclude_file,'r')
#  exclude_list=f.readlines()
#  f.close()
  execfile("exclude_template_BDT.py")

# option book list
  execfile("option_book_template_BDT.py")
  option_book_list.append("///NameMVA=BDT_"+_id+"\n")

#  print exclude_list
# option train list

#  if (len(option_train_file)>0):
#   f=open(option_train_file,'r')
#   option_train_list=f.readlines()
#   f.close()
  execfile("option_train_test_template_BDT.py")

  print _vars
  return ((_id,exclude_list,option_book_list,option_train_list),_vars)
 
 return ((None,None,None,None),_vars)


def GetConfig(mva_method,id,path2DB=""):

 if (len(mva_method)*len(id)<=0): return
 fileDB=mva_method+"_config"+".gz"
 if (len(path2DB)>0): fileDB=path2DB+fileDB

 f=open(fileDB,'rb')
 data=zlib.decompress(f.read())
 configs=pickle.loads(data)
 f.close()
 a=[s for s in configs if id == s[0] ]
 if (len(a)<=0): return ([],[],[])
 
 return (a[0][1],a[0][2],a[0][3])


def CreateConfigLists(id="",path2DB=""):
 """ cerate the lists of all needed configs for running MVA """

 if (len(id)<=0): return

 ###Settings begin

# trees_path="/data/user/marfin/CMSSW_5_3_3/src/Analysis/HbbMSSMAnalysis/test/Analysis2012/trees_for_training"
# tanb=20.

# democtratic_mix=True
# mass_for_mix=140.
 democtratic_xsect=GetXSection(tanb,mass_for_mix)

# mva_method="BDT"

 ###Settings end

 # signal processing
 signal_files=[]
# mass=["M-100","M-140","M-300"]
# files=[ GetListFiles(trees_path+"/*"+m+"*/*/*/TripleBtagAnalysis.root",trees_path) for m in mass ]
 files=[ GetListFiles(trees_path+"/*"+m+scenario_template,trees_path) for m in mass ]

 for item in files:
#  print item
  if (len(item)==0): continue
  (item,masses)=GetMassFromName(item)
  (item,numevts)=GetNumEvt(item)
  (item,lumiwgts)=GetLumiWeight(item)
  if (democtratic_mix):
   xsects=map(lambda x:  democtratic_xsect,masses)
  else:
   xsects=map(lambda x:  GetXSection(tanb,float(x)),masses)
  newwgts=GetNewWeight(1e3,lumiwgts,numevts,xsects)
  filesnew=map(lambda x: item[x].replace(".root","_update.root") ,range(len(item)))
  if (not os.path.exists(filesnew[0])):   ReWeight(tree_name='KinVarsBDT', list_of_files=item, weight=newwgts)
  signal_files+=filesnew

 # background processing
 bkg_files=[]
# ptbins=["15To30","30To50","50To150","-150_"]
# files=[ GetListFiles(trees_path+"/*"+ptbin+"*/*/*/TripleBtagAnalysis.root",trees_path) for ptbin in ptbins ]
 files=[ GetListFiles(trees_path+"/*"+ptbin+scenario_template,trees_path) for ptbin in ptbins ]

 for item in files:
#  print item
  if (len(item)==0): continue
  (item,numevts)=GetNumEvt(item)
  (item,lumiwgts)=GetLumiWeight(item)
  newwgts=GetNewWeight(1e3,lumiwgts,numevts)
  filesnew=map(lambda x: item[x].replace(".root","_update.root") ,range(len(item)))
  if (not os.path.exists(filesnew[0])):   ReWeight(tree_name='KinVarsBDT', list_of_files=item, weight=newwgts)
  bkg_files+=filesnew

 # it helps to solve the overtraining?
 random.shuffle(signal_files)
 random.shuffle(bkg_files)


# tree_name="KinVarsBDT"
 exclude_list="_tmp_exclude.lst" 
 option_book_list="_tmp_options_book.lst"
 option_train_list="_tmp_option_train.lst"
 input_list="list_of_files"


 sign_basenames=map(lambda x: os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(x)))))+"_"+os.path.basename(os.path.dirname(x)),signal_files)
 bkg_basenames=map(lambda x: os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(x)))))+"_"+os.path.basename(os.path.dirname(x)),bkg_files)

 f = open(input_list,'w')

 for i in range(len(signal_files)):
  f.write(signal_files[i]+" "+ sign_basenames[i] + " SGN" +" 1.0" +" 1.0" + " 1.0" + " 1" + "\n")

 for i in range(len(bkg_files)):
  f.write(bkg_files[i]+" "+ bkg_basenames[i] + " BKG" +" 1.0" +" 1.0" + " 1.0" + " 1" + "\n")

 f.close()
 

 files_sig=[ROOT.TFile.Open(file) for file in signal_files]
 files_bkg=[ROOT.TFile.Open(file) for file in bkg_files]
 (_exclude_lst,_book_lst,_train_lst)=GetConfig(mva_method,id,path2DB)



 f = open(exclude_list,'w')
 for item in _exclude_lst:   f.write(item)
 f.close()

 f = open(option_book_list,'w')
 for item in _book_lst:   f.write(item)
 f.close()
 

 f = open(option_train_list,'w')
 for item in _train_lst:   f.write(item)
 f.close()

 return


def RunMVAfromConfig(id="",path2DB=""):
 """ do running MVA training from settings previously tested and stored in db under path2DB with id number 'id'
     It might me interesting for the case of validation the optimal settings obtained for different sets of MC
 """

 CreateConfigLists(id,path2DB)

 exclude_list="_tmp_exclude.lst"
 option_book_list="_tmp_options_book.lst"
 option_train_list="_tmp_option_train.lst"
 input_list="list_of_files"


 funs=ROOT.gROOT.GetListOfGlobalFunctions()
 isOk=funs.FindObject("Readinput_v2") # this function is used in TMVAClassificationCreator.C. We need to have only one copy in the memory 
 if (isOk==None): ROOT.gROOT.ProcessLine('.L TMVAClassificationCreator.C+') 
 ROOT.TMVAClassificationCreator(input_list,mva_method,tree_name,exclude_list,option_book_list,option_train_list,"retrain_TMVA_"+id+".root")

 print "done ROOT.TMVAClassificationCreator	"

 return





def ProcessMVA(doOptimize=False,myvars={}):
 """ example of the whole chain for MVA training"""

 global trees_path

# correct ini
 p = subprocess.Popen("pwd" ,  stdout=subprocess.PIPE, shell=True)
 trees_path,err=p.communicate()
 trees_path=trees_path.strip()
 print "trees_path=",trees_path

 democtratic_xsect=GetXSection(tanb,mass_for_mix)

 # signal processing
 signal_files=[]
 files=[ GetListFiles(trees_path+"/*"+m+scenario_template.replace(".root","_update.root"),trees_path) for m in mass ]
 print files
 if len(files)>0 and len(files[0])>0 and os.path.exists(files[0][0] ):
  for item in files: signal_files+=item
 else:
  files=[ GetListFiles(trees_path+"/*"+m+scenario_template,trees_path) for m in mass ]
  for item in files:
   print item
   if (len(item)==0): continue
   (item,masses)=GetMassFromName(item)
   (item,numevts)=GetNumEvt(item)
   (item,lumiwgts)=GetLumiWeight(item)
   if (democtratic_mix):
    xsects=map(lambda x:  democtratic_xsect,masses)
   else:
    xsects=map(lambda x:  GetXSection(tanb,float(x)),masses)
   newwgts=GetNewWeight(1e3,lumiwgts,numevts,xsects)
   filesnew=map(lambda x: item[x].replace(".root","_update.root") ,range(len(item)))
   if (not os.path.exists(filesnew[0])):   ReWeight(tree_name='KinVarsBDT', list_of_files=item, weight=newwgts)
   signal_files+=filesnew


 # background processing
 bkg_files=[]
 files=[ GetListFiles(trees_path+"/*"+ptbin+scenario_template.replace(".root","_update.root"),trees_path) for ptbin in ptbins ]
 if  len(files)>0 and len(files[0])>0 and os.path.exists(files[0][0]):
  for item in files: bkg_files+=item
 else:
  files=[ GetListFiles(trees_path+"/*"+ptbin+scenario_template,trees_path) for ptbin in ptbins ]
  for item in files:
   print item
   if (len(item)==0): continue
   (item,numevts)=GetNumEvt(item)
   (item,lumiwgts)=GetLumiWeight(item)
   newwgts=GetNewWeight(1e3,lumiwgts,numevts)
   filesnew=map(lambda x: item[x].replace(".root","_update.root") ,range(len(item)))
   if (not os.path.exists(filesnew[0])):   ReWeight(tree_name='KinVarsBDT', list_of_files=item, weight=newwgts)
   bkg_files+=filesnew

 #create db
 if (not os.path.isfile("./"+mva_method+"_config.gz")): CreateConfigDB(mva_method)
 if (not os.path.isfile("./"+mva_method+"_result.gz")): CreateResultDB(mva_method)


 print "CONFIGSSSSS!!!"
 print ReadConfigs(mva_method)

 

 #create config
 (config,_vars)=CreateConfig(mva_method,doOptimize,myvars)

 print "CONFIG"
 print config

 #run mva
 RunMVAFromConfig(signal_files,bkg_files,mva_method,config)

 #save config to db
 UpLoadConfig(mva_method,config) 
 print "CONFIGSSSSS 22222!!!"
 print ReadConfigs(mva_method)


# get results
 _id=config[0]
 _separation=GetSeparationMVA(mva_method,config)
 (_sgnKS,_bkgKS)=GetKSMVA(mva_method,config)
 sgn_bkg_KS = GetKSignalBackgroundMVA(mva_method,config)
 result=(_id,_vars,_separation,_sgnKS,_bkgKS,sgn_bkg_KS)
# save results

 print "result=",result
 UploadResult(mva_method,result)

# check results
 print "CONFIGSSSSS 22222!!!"
# print ReadResults(mva_method)

# ROOT.gROOT.ProcessLine('.L TMVAGui.C')
# ROOT.TMVAGu()
 return



def FindOptimalResult(mva_method="",pos=0):
 """ return optimal parameter point """

 if (len(mva_method)<=0) : return None
 f=open(mva_method+"_result"+".gz",'rb')
 data=zlib.decompress(f.read())
 results=pickle.loads(data)

 #KS=sorted(KS,key=lambda x: x[1],reverse=True)
 results_sorted=sorted(results,key=lambda x: x[2],reverse=True)

 return results_sorted[pos]
 

def GetKSignalBackgroundMVA( mva_method="",config=()):
 """ return KS of Signal/Background tests for  MVA  """
 if (len(mva_method)<=0): return (None,None)
 if (not isinstance(config,tuple) ) : return (None,None)
 if ( list(config).count(None)>0) : return (None,None)

 f=ROOT.TFile("TMVA_"+mva_method+"_"+config[0]+".root")
 if (not f): return

 prefix="Method_"+mva_method+"/"

 method=mva_method+"_"+config[0]

 sgn=f.Get(prefix+method+"/"+"MVA_"+method+"_S")
 bkg=f.Get(prefix+method+"/"+"MVA_"+method+"_B")

 if (not (sgn and bkg )) : return None

 return sgn.KolmogorovTest(bkg)


def GetKSMVA( mva_method="",config=()):
 """ return KS test for signal and background MVA output """
 if (len(mva_method)<=0): return (None,None)
 if (not isinstance(config,tuple) ) : return (None,None)
 if ( list(config).count(None)>0) : return (None,None)

 f=ROOT.TFile("TMVA_"+mva_method+"_"+config[0]+".root")
 if (not f): return

 prefix="Method_"+mva_method+"/"

 method=mva_method+"_"+config[0]

 sgn=f.Get(prefix+method+"/"+"MVA_"+method+"_S")
 bkg=f.Get(prefix+method+"/"+"MVA_"+method+"_B")

 sgnTrain=f.Get(prefix+method+"/"+"MVA_"+method+"_Train"+"_S")
 bkgTrain=f.Get(prefix+method+"/"+"MVA_"+method+"_Train"+"_B")

 if (not (sgn and bkg and sgnTrain and bkgTrain)) : return (None,None)

 return (sgn.KolmogorovTest(sgnTrain),bkg.KolmogorovTest(bkgTrain))

def GetSeparationMVA( mva_method="",config=()):
 """ return separation of the current MVA """

 if (len(mva_method)<=0): return
 if (not isinstance(config,tuple) ) : return
 if ( list(config).count(None)>0) : return

 f=ROOT.TFile("TMVA_"+mva_method+"_"+config[0]+".root")
 if (not f): return

 prefix="Method_"+mva_method+"/"

 method=mva_method+"_"+config[0]
 sgn=f.Get(prefix+method+"/"+"MVA_"+method+"_S")
 bkg=f.Get(prefix+method+"/"+"MVA_"+method+"_B")


 if (not (sgn and bkg)) : return
 tools=ROOT.TMVA.Tools.Instance()

 return tools.GetSeparation(sgn,bkg)

  

def RunMVAFromConfig(signal_files=[],bkg_files=[], mva_method="",config=()):
 """ start mva on config and """

 print "RunMVAFromConfig"


 if (len(mva_method)*len(config)*len(signal_files)*len(bkg_files)<=0): return
 if (not isinstance(config,tuple) ) : return

 if ( list(config).count(None)>0) : return

# it helps to solve the overtraining?
 random.shuffle(signal_files)
 random.shuffle(bkg_files)


# tree_name="KinVarsBDT"
 exclude_list="_tmp_exclude.lst" 
 option_book_list="_tmp_options_book.lst"
 option_train_list="_tmp_option_train.lst"
 input_list="list_of_files"



 sign_basenames=map(lambda x: os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(x)))))+"_"+os.path.basename(os.path.dirname(x)),signal_files)
 bkg_basenames=map(lambda x: os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(x)))))+"_"+os.path.basename(os.path.dirname(x)),bkg_files)

 f = open(input_list,'w')

 for i in range(len(signal_files)):
  f.write(signal_files[i]+" "+ sign_basenames[i] + " SGN" +" 1.0" +" 1.0" + " 1.0" + " 1" + "\n")

 for i in range(len(bkg_files)):
  f.write(bkg_files[i]+" "+ bkg_basenames[i] + " BKG" +" 1.0" +" 1.0" + " 1.0" + " 1" + "\n")

 f.close()

 

 files_sig=[ROOT.TFile.Open(file) for file in signal_files]
 files_bkg=[ROOT.TFile.Open(file) for file in bkg_files]
 (_id,_exclude_lst,_book_lst,_train_lst)=config



 f = open(exclude_list,'w')
 for item in _exclude_lst:   f.write(item)
 f.close()

 f = open(option_book_list,'w')
 for item in _book_lst:   f.write(item)
 f.close()
 

 f = open(option_train_list,'w')
 for item in _train_lst:   f.write(item)
 f.close()

 funs=ROOT.gROOT.GetListOfGlobalFunctions()
 isOk=funs.FindObject("Readinput_v2") # this function is used in TMVAClassificationCreator.C. We need to have only one copy in the memory 
 if (isOk==None): ROOT.gROOT.ProcessLine('.L TMVAClassificationCreator.C+') 
 ROOT.TMVAClassificationCreator(input_list,mva_method,tree_name,exclude_list,option_book_list,option_train_list,"TMVA_"+_id+".root")

 print "after ROOT.TMVAClassificationCreator	"
# file=ROOT.TFile("TMVA.root","UPDATE")
 file=ROOT.TFile("TMVA_"+_id+".root","UPDATE")
# gDirectory->Delete(object_to_remove.c_str());

# print "deleting trees"
# file.Delete("TestTree;*")
# file.Delete("TrainTree;*")
 
# file.Delete("InputVariables_Id/CorrelationPlots")
# file.Delete("InputVariables_Gauss_Deco/CorrelationPlots")
# file.Delete("Method_+"mva_method"+"/BDT_"+config[0]+"/CorrelationPlots")
 
  
 currdir=file.GetPath()
 file.cd("InputVariables_Id/CorrelationPlots")
 objs=ROOT.gDirectory.GetListOfKeys()
 for obj in objs:
#  print obj.GetName()
  ROOT.gDirectory.Delete(obj.GetName()+";*")
 file.cd(currdir)

 file.cd("InputVariables_Gauss_Deco/CorrelationPlots")
 objs=ROOT.gDirectory.GetListOfKeys()
 for obj in objs:
#  print obj.GetName()
  ROOT.gDirectory.Delete(obj.GetName()+";*")
 file.cd(currdir)

# file.cd("InputVariables_Norm/CorrelationPlots")
# objs=ROOT.gDirectory.GetListOfKeys()
# for obj in objs:
#  print obj.GetName()
#  ROOT.gDirectory.Delete(obj.GetName()+";*")
# file.cd(currdir)

 file.cd("Method_"+mva_method+"/"+mva_method+"_"+config[0]+"/CorrelationPlots")
 objs=ROOT.gDirectory.GetListOfKeys()
 for obj in objs:
#  print obj.GetName()
  ROOT.gDirectory.Delete(obj.GetName()+";*")
 file.cd(currdir)


 file.Close()
 
# do optimization using internal TMVA support

# print factory
# method=factory.GetMethod(mva_method+"_"+config[0])
# print method
# method.OptimizeTuningParameters("Separation","Scan")
# factory.OptimizeAllMethods("Separation","Scan")



# os.system("mv TMVA.root TMVA_"+_id +".root")
# os.system("hadd -f TMVA_"+mva_method+"_"+_id +".root  TMVA.root")
 print "do hadd"

 os.system("hadd -f9 TMVA_"+mva_method+"_"+_id +".root  TMVA_"+_id+".root")
 os.system("rm "+exclude_list)
 os.system("rm "+option_book_list)
# os.system("cat "+option_train_list)
 os.system("rm "+option_train_list)
# os.system("rm TMVA.root")
 os.system("rm TMVA_"+_id+".root")



def RunMVATraining(signal_files=[],bkg_files=[]):
 """ perform running of TMVA """

 if (len(signal_files)==0): return False
 if (len(bkg_files)==0): return False

# mva_method="Likelihood"
# mva_method="BDT"
# mva_method="BDTGrad"
# tree_name="KinVarsBDT"
# exclude_list="exclude_bdt.lst"
# exclude_list="exclude2.lst"
 exclude_list="exclude_loose2.lst"

 option_book_list="options_book_Likelihood.lst"
# option_book_list="options_book_BDT.lst"
# option_book_list="options_book_BDTGrad.lst"
# option_train_list="options_train_test.lst"
 option_train_list=""
# option_train_list="options_train_test_20k.lst"
 input_list="list_of_files"

 print "prepare an input list"


 sign_basenames=map(lambda x: os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(x)))))+"_"+os.path.basename(os.path.dirname(x)),signal_files)
 bkg_basenames=map(lambda x: os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(x)))))+"_"+os.path.basename(os.path.dirname(x)),bkg_files)

 f = open(input_list,'w')

 print "Signal samples"
 for i in range(len(signal_files)):
#  print signal_files[i], sign_basenames[i],"SGN","1.0","1.0","1.0","1"
  f.write(signal_files[i]+" "+ sign_basenames[i] + " SGN" +" 1.0" +" 1.0" + " 1.0" + " 1" + "\n")

 print "Background samples"
 for i in range(len(bkg_files)):
#  print bkg_files[i], bkg_basenames[i],"BKG","1.0","1.0","1.0","1"
  f.write(bkg_files[i]+" "+ bkg_basenames[i] + " BKG" +" 1.0" +" 1.0" + " 1.0" + " 1" + "\n")

 f.close()

 files_sig=[ROOT.TFile.Open(file) for file in signal_files]
 files_bkg=[ROOT.TFile.Open(file) for file in bkg_files]

 ROOT.gROOT.ProcessLine('.L TMVAClassificationCreator.C') 


 ROOT.TMVAClassificationCreator(input_list,mva_method,tree_name,exclude_list,option_book_list,option_train_list) 

 return True


def GetMassFromName(file_names=[]):
 """ return a  mass name """
 if (len(file_names)==0): return False
# file_names = list(set(file_names)) # remover duplicated values
 # to get a list of available masses
 pm=re.compile(r"M-\d+",re.IGNORECASE)
 masses=map(lambda x: pm.search(x).group(0),file_names) # to get numeric val use [2:]
# masses = list(set(masses)) # remover duplicated values
 masses = map(lambda x: x[2:], masses)  # to get numeric val use [2:]

 return (file_names,masses)

def GetNewWeight(lumi=1e3,lumiweight=[],numevt=[],xsection=[]):
 """ return a weight list for reweighting """

 if (len(lumiweight)==0) : return False
 if (len(numevt)==0) : return False
 assert (len(lumiweight)==len(numevt))
 totalNum=sum(j for j in numevt)


 _numevt=map(lambda x: float(x)/float(totalNum),numevt) # now, they are fraction


 if len(xsection)==0: return _numevt
# _lumiweight=map(lambda x: lumiweight[x]*_numevt[x],range(_numevt))
 
 assert (len(lumiweight)==len(xsection))
 _xsectold=map(lambda x: lumiweight[x]*numevt[x]/lumi,range(len(lumiweight)))
 
 _xsecweight=map(lambda x: xsection[x]/_xsectold[x]*_numevt[x],range(len(_xsectold)))

 return _xsecweight

def GetNumEvt(file_names=[]):
 """ return a list of numEvts """
 if (len(file_names)==0): return False
 result=[]
 for file in file_names:
  if (not doNumEvt):
   result.append(-1)
   continue
  RootFile=ROOT.TFile(file)
  count=RootFile.Get("countSample/count")
  if (count==None): return False
  result.append(count.GetBinContent(1))

 return (file_names,result) 

def GetXSection(tanb=20.,mass=120.):
 """ return XSection at tanb and mass """

 """  
		xsections.tbl was created in python session
  
        import prepare_mva_grid
        import os
  
        myfile=file("xsections.tbl.2","w")
        for tanb in [10,20,25,30,35,40,45,50]:
         for mass in [90,120,140,160,180,200,250,300,350,400,450,500,600]: 
            print >> myfile, " %d %d %f"%(tanb,mass,prepare_mva_grid.GetXSection(tanb,mass))

        myfile.close()
        os.system("mv xsections.tbl.2 xsections.tbl")


 """

 if (not doXsect): return 1.0
 if  os.path.isfile("xsections.tbl"):
   myfile = open('xsections.tbl', 'r')
   lines=myfile.readlines()
   lines=[ x.split() for x in lines]
   for xsct in lines:
    if int(xsct[0])==int(tanb) and int(xsct[1])==int(mass): return float(xsct[2])

   return 1.
 else:
  ROOT.gROOT.ProcessLine('.L MSSM_tools/XSCalculator.C+')
  """  XSCalculator --> to XS for signal calculate """
  xsct=ROOT.XSCalculator(mass,tanb,"MSSM_tools/")

 return xsct

def GetLumiWeight(file_names=[]):
 """ return lumi weight """
 if (len(file_names)==0): return False
# file_names = list(set(file_names)) # remover duplicated values
 result=[]
 for file in file_names:
  if (not doLumiWeight):
   result.append(-1)
   continue
  RootFile=ROOT.TFile(file)
  lumiweight=RootFile.Get("lumiweight/lumiweight")
  if (lumiweight==None): return False 
  result.append(lumiweight.GetBinContent(1))

 return (file_names,result)

def GetListFiles(pattern="*", path=""):
 """ find files using pattern
    example: find all root files in theMergeList-pythia_QCD_Pt-30To50 subfolder of 
    /data/user/marfin/CMSSW_5_3_3/src/Analysis/HbbMSSMAnalysis/test/Analysis2012/trees_for_training/

    prepare_mva.GetListFiles("*the*30To50*root","/data/user/marfin/CMSSW_5_3_3/src/Analysis/HbbMSSMAnalysis/test/Analysis2012/trees_for_training/")
 """
 
 if (path.find("srm://")>=0):
  pattern=pattern.replace("*",".*")
  cmd=""" ./findSrmFiles "%s" "root"  | egrep "%s"   """ % (path,pattern) 
  """

  """
  oldaddr="srm://dcache-se-cms.desy.de/"
  newaddr="dcap://dcache-cms-dcap.desy.de/"
  p =subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
  mystr,err=p.communicate()
  mystr=mystr.split('\n')
  mystr=mystr[0:-1]
  results=[x.replace(oldaddr,newaddr) for x in mystr ]
  return  list(set(results))
 else:
  treeroot=os.getcwd()
  if (len(path)!=0): treeroot=path
  
  results = []
  for base, dirs, files in os.walk(treeroot):
#    print "files=",files
    files=map(lambda x: base+"/"+x,files)
    goodfiles = fnmatch.filter(files, pattern)
#    print "gfiles=",goodfiles

    results.extend(os.path.join(base, f) for f in goodfiles)

  return list(set(results))


def ReWeight(tree_name="KinVarsBDT",list_of_files=[],weight=[]):
 """ performs reweighting of the tree"""

 if (len(tree_name) == 0) : return False
 if (len(list_of_files)==0) : return False
 if (len(weight)==0) : return False
 assert (len(list_of_files)==len(weight))

 i=0 
 for file in list_of_files:
  filenew=file.replace(".root","_update.root")
#  RootFile=ROOT.TFile(file,"UPDATE")
  if (not doReweight):
   os.system("cp "+file+" "+filenew)
   continue
  RootFile=ROOT.TFile(file)
  tree=RootFile.Get(tree_name)
  if (tree==None): return False
  RootFileNew=ROOT.TFile(filenew,"RECREATE")
  newtree=tree.CloneTree(0)  
  wgt=array.array('f',[0])
  tree.SetBranchAddress("weight",wgt)
  entry=0
  while tree.GetEntry(entry):
   entry += 1
   wgt[0]*=weight[i]
   newtree.Fill()
  newtree.Write("",ROOT.TObject.kOverwrite)
  RootFileNew.Close()
  RootFile.Close()
  i+=1

 return True




if  __name__ == '__main__':
 """ main subroutine """


 if options.prepare_samples: Prepare_samples()
 if options.download_mva_dcache: Download_MVA_Trees_From_DCACHE()
 if options.download_mva_dcache_v2: Download_MVA_Trees_From_DCACHE_v2()
 if options.run:  ProcessMVA()  

 elif not options.download_mva_dcache and  not options.vars and not options.optimiationMVA and not options.prepare_samples and not options.download_mva_dcache_v2:
  print """
	
	Help:  

 Here a few examples how to use the package:
 


 """
