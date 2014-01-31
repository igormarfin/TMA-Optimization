#! /usr/bin/env python

"""a set of utils to prepare for mva traininig and 
   to test the obtained results

"""
__author__ =  'Igor Marfin'
__version__=  '1.12'
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
import copy

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
parser.add_option("--optimizer",dest="optimizer",default=False,action="store_true")
parser.add_option("--run",dest="run",default=False,action="store_true")
parser.add_option("--download_mva_dcache",dest="download_mva_dcache",default=False,action="store_true")
parser.add_option("--prepare_samples",dest="prepare_samples",default=False,action="store_true")
parser.add_option("--nonbatch",dest="nonbatch",default=True,action="store_false")
(options,args)=parser.parse_args()

if  options.nonbatch and not os.path.isfile(".prepare_mva.batch"):
 import ROOT 
#sys.argv.remove('-b-')
else:
#set batch mode
 sys.argv.append('-b-')
 import ROOT
 ROOT.gROOT.SetBatch(True)
 sys.argv.remove('-b-')


import  fnmatch
#import pickle
import cPickle as pickle
import zlib

try:
 cmssw =os.environ["CMSSW_BASE"]
 print cmssw
 from scipy.interpolate import Rbf,UnivariateSpline,splprep,splev

except KeyError:
 print "Please ini CMSSW"
 print "We neend CMSSW for scipy!"
 sys.exit(1)


###Settings

#stand-alone v8
dcachepathMVA="srm://dcache-se-cms.desy.de/pnfs/desy.de/cms/tier2/store/user/marfin/Higgs/BBbar/Analysis2012/CMSSW_535/MVA_Trees_v8/"

trees_path="/data/user/marfin/CMSSW_5_3_3/src/Analysis/HbbMSSMAnalysis/test/Analysis2012/tmva_test_v7/train_mva_standalone"
data_trees_path="/data/user/marfin/CMSSW_5_3_3/src/Analysis/HbbMSSMAnalysis/test/Analysis2012/tmva_test_v7/train_mva_standalone"
dcachepath="srm://dcache-se-cms.desy.de/pnfs/desy.de/cms/tier2/store/user/marfin/Higgs/BBbar/Analysis2012/CMSSW_535/"



tanb=20.
democtratic_mix=True
doReweight=False
doXsect=True
doNumEvt=False
doLumiWeight=False



mass_for_mix=200.
mass=["*M-140-KinVarsBDT.root*","*M-200-KinVarsBDT.root*","*M-350-KinVarsBDT.root*"]

BkgOvertrain=["*GeneralQCD-KinVarsBDT.root*"]
ptbins=["*bEnrichQCD-KinVarsBDT.root*"]
datapattern=["*data.root*"]



mva_method="BDT"
tree_name="KinVarsBDT"

# v8
# new variable since v3!
# do correct scenario selection 
scenario_template=""
scenario_template_data=""
scenario_template_update=""

def Download_MVA_Trees_From_DCACHE():

  """ copy all mva trees from dCache to current directory

   all MVA directories were copied to dCache in the way
   
   ls -d */ | grep "_v5" | xargs -I {} echo "find {} -iname \"Triple*root\" "| sh | xargs -I {} echo "echo {}; lcg-cp -D srmv2  
   file:/\`pwd\`/{} srm://dcache-se-cms.desy.de/pnfs/desy.de/cms/tier2/store/user/marfin/Higgs/BBbar/Analysis2012/CMSSW_535/MVA_Trees_v5/{}" |sh

  """

  cmd="./copySrmFilesSubFolder %s %s %s %s"

  # we are going to copy only updated root files for 
 # os.system(cmd%(dcachepathMVA,"MEDIUM","update","root"))

  os.system(cmd%(dcachepathMVA,"MEDIUM","root","root"))

 #2nd attempt if lcg-ls failed
  cmd="./copySrmFilesSubFolder_v2 %s %s %s %s"
  p=subprocess.Popen("find . -iname \"*.root\"",  stdout=subprocess.PIPE, shell=True)
  rootfiles,err=p.communicate()
  if (rootfiles==""):
   os.system(cmd%(dcachepathMVA,"MEDIUM","root","root"))

#  for m in mass:
#   os.system(cmd%(dcachepathMVA,"MEDIUM",m,"root"))
#
#  for ptbin in ptbinspattern:
#   os.system(cmd%(dcachepathMVA,"MEDIUM",ptbin,"root"))

  return

def Prepare_samples():

 """ copy all needed samples from dCache """

 cmd="""lcg-ls "%s" | egrep  "%s" | xargs -I {} echo " mkdir -m o=rwx \`basename {}\`; cd \`basename {}\`; ../copySrmFiles \\\"%s\`basename {}\`\\\" ; cd -; " |sh """

 for signal in mass:  os.system(cmd%(dcachepath,signal.replace("*",".*"),dcachepath))
 for ptbin in ptbins:  os.system(cmd%(dcachepath,ptbin.replace("*",".*"),dcachepath))

 return


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


def Download_XML_outputGzipped(mva_method,id,path="./",pathTo="./"):
 """ download TMVA outputs in root files from dcache.
     It looks through the 'dcache_scratch' file entries to find real paths for download.
     Also, files of names like  root_files_* are needed to find the TMVA_mva_method_id.root file  """   
 """ """

 if len(mva_method)*len(id)<=0 : return



 p = subprocess.Popen("ls "+path+"TMVA_"+mva_method+"_"+id+".root",  stdout=subprocess.PIPE, shell=True)
 myfile,err=p.communicate()
 if (len(myfile)>0): return path+"weights/"

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
   cmd="cd "+path+" ; tar -xf result_"+crabid+".tgz  weights;"
   p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
   p.wait()
   cmd="mv "+path+"weights "+pathTo+"weights"
   p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
   p.wait()
   return pathTo+"weights"


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
 cmd="cd "+path+" ; tar -xf result_"+crabid+".tgz  weights    rm result_"+crabid+".tgz"
 p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
 p.wait()
 cmd="mv "+path+"weights "+pathTo+"weights"
 p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
 p.wait()
 return pathTo+"weights"








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
   p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
   p.wait()
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
 p.wait()
 return path+"TMVA_"+mva_method+"_"+id+".root"


def Download_TMVA_XML_outputGzipped(mva_method,id,path="./"):
 """ download TMVA outputs in root files from dcache.
     It looks through the 'dcache_scratch' file entries to find real paths for download.
     Also, files of names like  root_files_* are needed to find the TMVA_mva_method_id.root file  """   
 """ """

 if len(mva_method)*len(id)<=0 : return



 p = subprocess.Popen("ls "+path+"TMVA_"+mva_method+"_"+id+".root",  stdout=subprocess.PIPE, shell=True)
 myfile,err=p.communicate()
 if (len(myfile)>0): return path+"TMVA_"+mva_method+"_"+id+".root\n " + path +"weights"

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
   cmd="cd "+path+" ; tar -xf result_"+crabid+".tgz  TMVA_"+mva_method+"_"+id+".root weights; "
   p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
   p.wait()
   return path+"TMVA_"+mva_method+"_"+id+".root \n " + path + "weights"


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
 cmd="cd "+path+" ; tar -xf result_"+crabid+".tgz  TMVA_"+mva_method+"_"+id+".root weights;   rm result_"+crabid+".tgz"
# cmd="cd "+path+" ; tar -xf result_"+crabid+".tgz  TMVA_"+mva_method+"_"+id+".root weights;"
 p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
 p.wait()
 return path+"TMVA_"+mva_method+"_"+id+".root \n " + path+"weights"





def Upload_All_TMVA_outputTo_dCache(mva_method,path="./"):

 cmd="ls " +path + "TMVA_"+mva_method+"*root"
 p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
 tmvafiles,err=p.communicate()
 tmvafiles=tmvafiles.split('\n')
 for file in tmvafiles:
   if len(file)==0 : continue
   file= file.split('_')
   mva=file[1]
   id=file[2].replace(".root","")
   Upload_TMVA_outputTo_dCache(mva,id,path)

 return 




def Check_TMVA_outputIn_dCache(mva_method,id,path="./"):

 if (len(mva_method)*len(id)==0): return False
 
 cmd="cat " +path + "dcache_scratch | grep \"_defaultpath_\" | awk '{print $2}'"
 p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
 defaultpath,err=p.communicate()

 file="TMVA_"+mva_method+"_"+id+".root"

 cmd="lcg-ls  %s | grep %s"
 p = subprocess.Popen(cmd%(defaultpath,file),  stdout=subprocess.PIPE, shell=True)
 mystr,err=p.communicate()
 if (len(mystr)>0): return True


 return False




def Upload_TMVA_outputTo_dCache(mva_method,id,path="./"):   

 cmd="cat " +path + "dcache_scratch | grep \"_defaultpath_\" | awk '{print $2}'"
 p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
 defaultpath,err=p.communicate()
 
 cmd="cat " +path + "dcache_scratch | grep \"_path_\" | awk '{print $2}'"
 p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
 paths,err=p.communicate()
 paths=paths.split('\n')

 addPath=True
 if defaultpath in paths: addPath=False
 file="TMVA_"+mva_method+"_"+id+".root"
 cmd="lcg-cp -D srmv2   file:/\`pwd\`/%s%s %s/%s"
 p = subprocess.Popen(cmd%(path,file,defaultpath,file),  stdout=subprocess.PIPE, shell=True)
 mystr,err=p.communicate()

 CanbeDeleted=False
 cmd="lcg-ls  %s | grep %s"
 p = subprocess.Popen(cmd%(defaultpath,file),  stdout=subprocess.PIPE, shell=True)
 mystr,err=p.communicate()
 if (len(mystr)>0): CanbeDeleted=True

 if (CanbeDeleted):
  cmd="rm "+"TMVA_"+mva_method+"_"+id+".root"
  p = subprocess.Popen(cmd%(path,file,defaultpath,file),  stdout=subprocess.PIPE, shell=True)
  mystr,err=p.communicate()  

 if (addPath):  cmd="echo "+ defaultpath+" >> "+path + "dcache_scratch"

 return
 



def Download_TMVA_outputFrom_dCache(mva_method,id,path="./"):
 """ download TMVA test outputs in root files from dcache.
     It looks through the 'dcache_scratch' file entries to find real paths for download.
     Also, files of names like  root_files_* are needed to find the TMVA_mva_method_id.root file  """   
 """ """

 cmd="cat " +path + "dcache_scratch | grep \"_path_\" | awk '{print $2}'"
 p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
 paths,err=p.communicate()
 paths=paths.split('\n')
 tgzfile=""

 for _path in paths:
  if len(_path)<=0 : continue
  print "current dCache path ",_path
  cmd="cd "+path+"; ./copySrmFiles "+_path+ "  TMVA_"+mva_method+"_"+id+".root"
  p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
  crabfiles,err=p.communicate()

  if len(crabfiles)>0:
   print "Is "+  "TMVA_"+mva_method+"_"+id+".root"  +" copied? "
   p = subprocess.Popen("ls "+path+" TMVA_"+mva_method+"_"+id+".root",  stdout=subprocess.PIPE, shell=True)
   tgzfile,err=p.communicate()
   print "tgzfile=",tgzfile
   if (len(tgzfile)>0):
    print "it's copied"
    break

 if (len(tgzfile)<=0): return
 return path+"TMVA_"+mva_method+"_"+id+".root"




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


def CheckVariablesForOptimization(mva_method="",interpolator=None,_minsmoothy=0.):
 """ return a list of variables for further optimization """
 if (len(mva_method)<=0) : return None
 if (interpolator==None): return None
 
 f=open(mva_method+"_result"+".gz",'rb')
 data=zlib.decompress(f.read())
 results=pickle.loads(data)

 results=sorted(results,key=lambda x: x[2] ,reverse=True)
 results=[x for x in results if not x[0] == "000000"]
 vars=results[0][1].items()
 point=GetOptimalPoint(mva_method)
 vars_to_optimize={}
 for var in range(len(vars)):
  pos=FindPostionMinMax(mva_method,vars[var][0])
  minX,maxX,smoothy=GetSmoothy1D(interpolator,point,pos[0],(GetNumPoints(mva_method),pos[1],pos[2]))
  if (smoothy>_minsmoothy): vars_to_optimize[vars[var][0]]=smoothy
 
 st=sorted([(value,key) for (key,value) in  vars_to_optimize.items()],reverse=True)  
 return  [(key,value) for (value,key) in st]


def DrawVariables(mva_method="",interpolator=None):
 """ Draw 1D interpolations """

 """
		Example of drwaing by hands

     results=prepare_mva.FindOptimalResult("BDT")
interpol1=prepare_mva.Interpolate_MVA("BDT","Rbf",0.00000005,"")
interpol1(* [ i[1] for i in results[1].items() ])

interpol2=prepare_mva.Interpolate_MVA("BDT","Rbf",0.00000005,"robust")
interpol2(*[ i[1] for i in results[1].items() ])
interpol3=prepare_mva.Interpolate_MVA("BDT","Rbf-gaussian",0.000000000000005,"")
interpol3(*[ i[1] for i in results[1].items() ])
interpol4=prepare_mva.Interpolate_MVA("BDT","Rbf-inverse",0.000005,"")
interpol4(*[ i[1] for i in results[1].items() ])
 interpol5=prepare_mva.Interpolate_Regression_MVA("MLP")
 interpol5(*[ i[1] for i in results[1].items() ])
 pos=FindPostionMinMax("BDT","var5")
 gr4=prepare_mva.PlotFunction(interpol4,[ i[1] for i in results[1].items() ],0,(prepare_mva.GetNumPoints("BDT"),pos[1],pos[2]) )
gr5=prepare_mva.PlotFunction(interpol5,[ i[1] for i in results[1].items() ],0,(prepare_mva.GetNumPoints("BDT"),pos[1],pos[2]) )

 """


 if (len(mva_method)<=0) : return None
 if (interpolator==None): return None

 f=open(mva_method+"_result"+".gz",'rb')
 data=zlib.decompress(f.read())
 results=pickle.loads(data)

 f.close()

 results=sorted(results,key=lambda x: x[2] ,reverse=True)
 results=[x for x in results if not x[0] == "000000"]
 vars=results[0][1].items()
 point=GetOptimalPoint(mva_method)
 canvs=[]
 grs=[]
 for var in range(len(vars)):
  pos=FindPostionMinMax(mva_method,vars[var][0])
  gr=PlotFunction(interpolator,point,pos[0],(GetNumPoints(mva_method),pos[1],pos[2]))
  canv=ROOT.TCanvas("Variable %s"%vars[var][0],"Variable %s"%vars[var][0])
  gr.SetName("var_%s"%vars[var][0])
  gr.SetTitle("var_%s"%vars[var][0])
  gr.SetLineWidth(4)
  gr.SetFillStyle(0)
  gr.Draw("ALP")
  ROOT.SetOwnership(canv,False)
  ROOT.SetOwnership(gr,False)
#  canv.Close()
  canvs.append(canv)
  grs.append(gr)
  
 return (canvs,grs)	

def DrawVariables2File(grs=[],pos=[],fileout="test"):
 """ Print obtained TGraph objects to some file """
 
 mg=ROOT.TMultiGraph("mg_"+fileout,"mg_"+fileout) 
 for gr in grs:
  for i in pos:
   mg.Add(gr[i])

 xLegend = 0.82;
 yLegend = 0.92;
 sizeLeg = 0.5;

 canv=ROOT.TCanvas(fileout,fileout, 1200, 800)
 ROOT.TGaxis.SetMaxDigits(3);
 ROOT.gPad.SetFrameBorderMode(0);
 ROOT.gPad.SetRightMargin(0.25);
 ROOT.gPad.SetLeftMargin(0.2);
 ROOT.gPad.SetBottomMargin(0.2);
 mg.Draw("ALP")
 canv.BuildLegend(xLegend , yLegend - 0.5*sizeLeg , xLegend + 0.2*sizeLeg, yLegend)
 canv.Print(fileout+".png","png")
 return


def DrawOptimalPoints(mva_method="",interpolator=None):
 """ Draw 1D interpolations """
 if (len(mva_method)<=0) : return None
 if (interpolator==None): return None

 f=open(mva_method+"_result"+".gz",'rb')
 data=zlib.decompress(f.read())
 results=pickle.loads(data)

 f.close()

 results=sorted(results,key=lambda x: x[2] ,reverse=True)
 results=[x for x in results if not x[0] == "000000"]
 vars=results[0][1].items()
 point=GetOptimalPoint(mva_method)
 canvs=[]
 grs=[]

 for var in range(len(vars)):
  pos=FindPostionMinMax(mva_method,vars[var][0])
  gr=PlotFunction(interpolator,point,pos[0],(1,point[pos[0]],point[pos[0]]))
  canv=ROOT.TCanvas("OptimalVariable %s"%vars[var][0],"OptimalVariable %s"%vars[var][0])
#  print canv.GetName()
  gr.SetName("opt_var_%s"%vars[var][0])
  gr.Draw("ALP")
  gr.SetMarkerStyle(3)
  gr.SetMarkerSize(2.4)
  gr.SetMarkerColor(ROOT.kRed)
  gr.SetTitle("opt_var_%s"%vars[var][0])
  gr.SetLineWidth(4)
  gr.SetFillStyle(0)
  ROOT.SetOwnership(canv,False)
  ROOT.SetOwnership(gr,False)
  canv.Close()
  canvs.append(canv)
  grs.append(gr)
  
#return grs
 return (canvs,grs)	


def Interpolate_MVA_grid(x,mva_method="",interpolation="nearest",point=[],position=-1):
 """ returns grid of values """


 if (scipy.__version__ < "0.9.0"): return None
 from scipy.interpolate import griddata

 if (len(mva_method)<=0) : return None
 if (len(point)<=0): return None
 if (position<0): return None


 results=[]                

 if os.path.exists(mva_method+"_result.gz"):
  f=open(mva_method+"_result"+".gz",'rb')
  data=zlib.decompress(f.read())
  results=pickle.loads(data)
  f.close()

 if os.path.exists("grid/"+mva_method+"_result.gz"):
  f=open(mva_method+"_result"+".gz",'rb')
  data=zlib.decompress(f.read())
  results+=pickle.loads(data)
  f.close()


 results=sorted(results,key=lambda x: x[2] ,reverse=True)
 results=[x for x in results if not x[0] == "000000"]
# print results

 nVars=len(results[0][1])
# print nVars
 nPoints=len(results)
# print nPoints

# point_2=[]
# for p in range(len(point)):
#  if p in position:
#   point_2.append(x[position.index(p)])
#  else:
#   point_2.append(point[p])

# point=point_2

 point[position]=x

 Points=numpy.ndarray((nPoints,nVars))
 Values=numpy.ndarray(nPoints)

 for i in range(nPoints):
  for j in range(nVars):

 #  print "j=",j
 #  print results[i][1].items()
 #  print results[i][1].items()[j]
   Points[i][j]=results[i][1].items()[j][1]

# fill y
 for i in range(nPoints):
  Values[i]=results[i][2]
 
 return griddata(Points,Values,numpy.array(point),method=interpolation)

def GetNumPoints(mva_method=""):
 if (len(mva_method)<=0) : return 0
 if os.path.exists(mva_method+"_result.gz"):
  f=open(mva_method+"_result"+".gz",'rb')
  data=zlib.decompress(f.read())
  results=pickle.loads(data)
  results=sorted(results,key=lambda x: x[2] ,reverse=True)
  results=[x for x in results if not x[0] == "000000"]
  return len(results)
 else : return 0




class Rbf_Functor_V2():
 """ to represent MVA regressor """

 # args
 """
  0 -- method name 

 """
 def __init__(self,rbf,name=""):
  if (name==""): self.name="Rbf"
  else : self.name=name
  self._negate_call = False
  self.rbf=rbf

 def __call__(self,args):
   return  -self.rbf(*args) if  self._negate_call else self.rbf(*args)

 def __neg__(self):
   other = copy.copy(self)
   other._negate_call = not other._negate_call
   return other



def Interpolate_MVA(mva_method="",interpolation="Rbf",_smooth=0.00005,options="robust",version="V1"):
 """ do interpolation of mva """

 if (len(mva_method)<=0) : return None

 results=[]

 if os.path.exists(mva_method+"_result.gz"):
  f=open(mva_method+"_result"+".gz",'rb')
  data=zlib.decompress(f.read())
  results=pickle.loads(data)
  f.close()
  
# if os.path.exists("grid/"+mva_method+"_result.gz"):
#  f=open(mva_method+"_result"+".gz",'rb')
#  data=zlib.decompress(f.read())
#  results+=pickle.loads(data)
#  f.close()


 results=sorted(results,key=lambda x: x[2] ,reverse=True)
 results=[x for x in results if not x[0] == "000000"]
# print results


 nVars=len(results[0][1])
# print nVars
 #x=numpy.ndarray(nVars)
# nPoints=len(results)-1
 nPoints=len(results)
# print nPoints

 Points=[]
 for i in range(nVars):
  Points.append(numpy.ndarray(nPoints))


# to store y
 Points.append(numpy.ndarray(nPoints))
 

# fill points
 for j in range(nVars):
  for i in range(nPoints):
 #  print "j=",j
 #  print results[i][1].items()
 #  print results[i][1].items()[j]
   try:
    Points[j][i]=results[i][1].items()[j][1]
   except IndexError:
    Points[j][i]=0.
     
# fill y
 for i in range(nPoints):
  Points[nVars][i]=results[i][2]


 print nPoints

 nmin=1+nVars+nVars*(nVars+1.)/2. #+(nVars+1.)*(nVars+1.)/6.

 print nmin

 if "robust" in options:
  if (version=="V1"):  return Rbf(*Points)
  if (version=="V2"):  return Rbf_Functor_V2(Rbf(*Points),"Rbf-robust")

 

 if (interpolation == "Rbf"): 
  if  nPoints<=nmin:
   if (version=="V1"): return Rbf(*Points,smooth=_smooth,epsilon=0.99999999999)
   if (version=="V2"): return Rbf_Functor_V2(Rbf(*Points,smooth=_smooth,epsilon=0.99999999999),"Rbf-epsilon-0.99999999999")
  else:
   if (version=="V1"): return Rbf(*Points,smooth=_smooth,epsilon=1000)
   if (version=="V2"): return  Rbf_Functor_V2(Rbf(*Points,smooth=_smooth,epsilon=1000),"Rbf-epsilon-1000")
 if (interpolation == "Rbf-gaussian"):
  if nPoints<=nmin:
   if (version=="V1"): return Rbf(*Points,function='gaussian',smooth=_smooth,epsilon=0.99999999999)
   if (version=="V2"): return Rbf_Functor_V2(bf(*Points,function='gaussian',smooth=_smooth,epsilon=0.99999999999),"Rbf-gaussian-epsilon-0.99999999999")
  else:
   if (version=="V1"): return Rbf(*Points,function='gaussian',smooth=_smooth,epsilon=1000)
   if (version=="V2"): return  Rbf_Functor_V2(Rbf(*Points,function='gaussian',smooth=_smooth,epsilon=1000),"Rbf-gaussian-epsilon-1000")
 if (interpolation == "Rbf-inverse"): 
  if nPoints<=nmin:
   if (version=="V1"): return Rbf(*Points,function='inverse',smooth=_smooth,epsilon=0.999999999999)
   if (version=="V2"): return  Rbf_Functor_V2(Rbf(*Points,function='inverse',smooth=_smooth,epsilon=0.999999999999),"Rbf-inverse-epsilon-0.99999999999")
  else:
   if (version=="V1"): return Rbf(*Points,function='inverse',smooth=_smooth,epsilon=1000)
   if (version=="V2"): return  Rbf_Functor_V2(Rbf(*Points,function='inverse',smooth=_smooth,epsilon=1000),"Rbf-inverse-epsilon-1000")

#  return Rbf(*Points,function='inverse',smooth=_smooth)
 if (interpolation == "FITPACK"):
  if (nVars>=11): return None 
  # spline parameters
  s=3.0 # smoothness parameter
  k=2 # spline order
  nest=-1 # estimate of number of knots needed (-1 = maximal)
  # find the knot points
  xPoints=[]
  for i in range(nVars+1):
   xPoint=array.array('f',Points[i])
   xPoints.append(xPoint)
  tckp,u = splprep(xPoints,s=s,k=k,nest=-1)

  return tckp

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

def PlotAllPoints(mva_method="",position=-1):
 """return  TGraph  """

 if (position<0): return None
 if (len(mva_method)<=0) : return None

 numPt=GetNumPoints(mva_method)
 xs=numpy.ndarray(numPt)
 ys=numpy.ndarray(numPt)

 f=open(mva_method+"_result"+".gz",'rb')
 data=zlib.decompress(f.read())
 results=pickle.loads(data)
 f.close()


 results=sorted(results,key=lambda x: x[2] ,reverse=True)
 results=[x for x in results if not x[0] == "000000"]

 i=0
 name=""
 for result in results:
  vars=result[1].items()
  xs[i]=vars[position][1]
  name="points_%s"%vars[position][0]
  ys[i]=result[2]
  i+=1

 gr1 = ROOT.TGraph(numPt,xs, ys)
 gr1.SetName(name)
 gr1.SetLineColor(3)
 gr1.SetMarkerColor(3)
 gr1.SetTitle(name)
 gr1.SetLineWidth(4)
 gr1.SetFillStyle(0)

 gr1.Sort()
# print gr1
 return gr1



def PlotFunction (interpolator=None,point=[],position=-1,minmax=()):
 """ return TGraph of 1D function """ 
 """ """

 if (position<0): return None
 if (interpolator==None or len(point)==0): return None
 if (minmax==()): return None


 nStep=int(minmax[0])
 minVal=float(minmax[1])
 maxVal=float(minmax[2])

 if (nStep  == 0) : return None

 if (nStep>1):
  dx=float(maxVal-minVal)/(nStep-1)
  xs=numpy.ndarray(nStep)
  ys=numpy.ndarray(nStep)
 else:
  dx=float(maxVal-minVal)/49
  xs=numpy.ndarray(50)
  ys=numpy.ndarray(50)
  nStep=50


 for bin in range(nStep):
  xs[bin]=minVal+bin*dx
  ys[bin]=InterpolatedFunction1D(xs[bin],interpolator,point,position)

 gr1 = ROOT.TGraph(nStep,xs, ys)
# gr1.SetName("Significance")
 gr1.SetLineColor(1)
 gr1.SetMarkerColor(1)
 gr1.Sort()
# print gr1
 return gr1



def ControlInterplolator(mva_method="",interpolator=None):
 """ Do controling the interpolator


 """

 import numpy as np
 import math

 if (len(mva_method)==0): return None
 if (interpolator==None): return None

 results=[]
 for i in range(len(ReadResults(mva_method))): 
  res=FindOptimalResult(mva_method,i)
  if (res[0]=="000000"): continue
  results.append(res)
 points=[]
 values=[]
 for result in results: 
  points.append(result[1])
  values.append(result[2])


 values_interpolated=[]
 for point in points:
   _point=[ i[1] for i in point.items()]
   print _point
   values_interpolated.append(interpolator(_point) )

 sqrtsum=0.
 for i in range(len(values)):
  sqrtsum+=(values[i]- values_interpolated[i])*(values[i]- values_interpolated[i])/len(values)

 sqrtsum=math.sqrt(sqrtsum)
 print "sqrtsum=",sqrtsum
 return


def GetInterpolators(mva_method=""):

 """ Returns 5 different interpolators 
     requested by optimizer

 """

 if (len(mva_method)==0): return None
 # create 5 different interpolators (we will use 5 different paths for optimization)
 interpolators=[]
 #1
 try:
  print "test"
  interpolators.append(Interpolate_MVA(mva_method,"Rbf",0.00000005,"","V2"))
  print "test"
 except:
  pass
 #2 
 try:
  print "test2"
  interpolators.append(Interpolate_MVA("BDT","Rbf",0.00000005,"robust","V2"))
 except:
  pass
 #3
 try:
  interpolators.append(Interpolate_MVA("BDT","Rbf-gaussian",0.000000000000005,"","V2"))
 except:
  pass
 # MVA Regression
 try:
  CreateTreesForOptimization(mva_method)
  Prepare_Regression_Computers(["MLP","BDT"])
 #4
  interpolators.append(Interpolate_Regression_MVA("MLP","V2"))
 #5
  interpolators.append(Interpolate_Regression_MVA("BDT","V2"))
 except:
  pass

 print interpolators
 return interpolators

def ProcessOptimizer():
 """ example of the optimization with help of interpolation """


 # find 3 best optimal points reconstructed so far
 results=[]
 if (os.path.exists(".optimizerID")): 
  file=open(".optimizerID","r")
  _results = file.readlines()
  for i in range(min(3,len(_results))): 
   results.append(GetResults(mva_method,_results[i].rstrip('\n')))
 else:
  for i in range(3):  results.append(FindOptimalResult(mva_method,i))
 points=[]
 for result in results: points.append(result[1])
 
 interpolators=GetInterpolators(mva_method)
 print "interpolators=",interpolators
 if (interpolators==None): return

 from multiprocessing import Pool
 
 for point in points:
  pool = Pool(processes=len(interpolators))
  async_results=[]
  for interpolator in interpolators:
   _point=[ i[1] for i in point.items()]
   _name=[ i[0] for i in point.items()]
   res,mypoint=OptimizeThePoint(mva_method,interpolator,_point,250)
   print "predicted result is ", res, " for interpolator",interpolator  
   _myvars={}
   for i in range(len(mypoint)): _myvars[_name[i]]=mypoint[i]
   async_results.append(pool.apply_async(ProcessMVA,args = (True,_myvars)) )
#   ProcessMVA(True,_myvars)
  for res in async_results: 
   myres=res.get()
   print "obtained res is ", myres

 return



def OptimizeThePoint(method="",interpolator=None,point=[],numiteration=100):

 """ does iteration to find best point 
     it uses interpolator

 """

 if interpolator==None or len(point)==0 or len(method)==0:
  print OptimizeThePoint.__doc__
  return None

 mypoint=copy.copy(point)
 res=-9999.9
 cons=GetContraints_V2(method)
 step=0.01
 for i in range(numiteration):
  currentres=res
  res,mypoint=CheckVicinity_V2(interpolator,mypoint,cons,0,res,step)
  if (abs(currentres-res)/res<0.01): 
   step*=2.
  if step>1e8: return res,mypoint  

 return res,mypoint


def CheckVicinity_V2(interpolator,point=[],_cons=[],pos=0,thebest=-9999,step=0.01):
 """
		Does small (1% ) movements around the point to find possible better interpolated results 

 """
 
 _point=copy.copy(point)
 mypoint=copy.copy(_point)
# print "point=",_point
# print "cons=",_cons

 if (interpolator==None or len(point)==0 or len(_cons)==0):
  print CheckVicinity_V2.__doc__
  return None

 import  numpy  as np

 res=copy.copy(thebest)
 _thebest=copy.copy(thebest)

 if pos != len(_point):
  x=_point[pos]
  _point[pos]=  _point[pos] - (_cons[pos][1]- _cons[pos][0])*step
  if (_point[pos]>_cons[pos][1]): _point[pos]=_cons[pos][1]
  if (_point[pos]<_cons[pos][0]): _point[pos]=_cons[pos][0]
#  print "diff=", (_cons[pos][1]- _cons[pos][0])*0.01
#  print "1 ",_point[pos]
  res=interpolator(np.array(_point))
#  print "1 res ",res
  if res>thebest : 
   _thebest=res
  res,_mypoint=CheckVicinity_V2(interpolator,_point,_cons,pos+1,_thebest,step)
#  print "11 res ",res
  if (res>_thebest) : 
   _thebest=res
   mypoint=_mypoint

  _point[pos]=x
  _point[pos] +=(_cons[pos][1]- _cons[pos][0])*0.01
#  print "2 ",_point[pos]
  res=interpolator(np.array(_point))
#  print "2 res ",res
  if res>_thebest :    
   _thebest=res
   mypoint=copy.copy(_point)
  
  res,_mypoint=CheckVicinity_V2(interpolator,_point,_cons,pos+1,_thebest,step)
#  print "22 res ",res
  if (res>_thebest) :
    _thebest=res
    mypoint=_mypoint
 else: return thebest,mypoint
 return _thebest,mypoint	


    


def GetContraints_V2(method=""):
 """
    return constrints as 
    [(),(),() etc]
  
    constraints should be applied for constrained  optimization done on "V2" interpolators  
    
 """

 if (method==""):
  print GetContraints_V2.__doc__
  return []

 vars=PrintVariableNames(method,True)
 res=[]   
 cons={}
 if os.path.exists("contraints.py"):
  execfile("contraints.py")
  for var in vars:    res.append(cons[var])

 return res
    


def FindInterpolatedMax_constrained_V2(interpolator=None,x0=[],Bounds=None,solver="BFGS"):
 """ does constrained optimization by means of scipy.optimize
     it works only with functors of version=="V2".
     If you want to find maximum. use '-interpolator' "

     Bound can be None or list object 
   
    possible solvers:
       BFGS
       Newton
       SLSP --  Sequential Least SQuares Programming   
 """

 if (interpolator==None or len(x0)==0):
  print FindInterpolatedMax_constrained_V2.__doc__
  return None
  
 if (Bounds!=None): assert(len(x0)==len(Bounds))

 from  scipy import optimize
 import  numpy  as np
 if (solver=="BFGS"): return  optimize.fmin_l_bfgs_b(interpolator,np.array(x0),fprime=None, args=(),approx_grad=True,bounds=Bounds)
 if (solver=="Newton"): return optimize.fmin_tnc(interpolator,np.array(x0),fprime=None, args=(),approx_grad=True,bounds=Bounds)
 if (solver=="SLSP"): return optimize.fmin_slsqp(interpolator,np.array(x0),fprime=None, args=(),bounds=Bounds)




def FindInterpolatedMax(interpolator=None,point=[],solver="BFGS"):
 """ taken from
     http://scipy-lectures.github.com/advanced/mathematical_optimization/index.html

    return point where maximum was found 

     available methods:
      Conjugate_gradient_descent
      BFGS (Broyden-Fletcher-Goldfarb-Shanno algorithm) 
      Simplex
 """
 from scipy import optimize
 if (interpolator==None or len(point)==0): return None
 if (solver=="Conjugate_gradient_descent"): return optimize.fmin_cg(InterpolatedValue2,point,args=[interpolator])
 if (solver=="BFGS"): return optimize.fmin_bfgs(InterpolatedValue2,point,args=[interpolator])
 if (solver=="Simplex"): return optimize.fmin(InterpolatedValue2,point,args=[interpolator]) 

 return None






def FindInterpolatedMax1D(interpolator=None,point=[],solver="Conjugate_gradient_descent",position=-1):
 from scipy import optimize
# def InterpolatedFunction1D(x,interpolator=None,point=[],position=-1):

 if (interpolator==None or len(point)==0): return None
 if (solver=="Conjugate_gradient_descent"): return optimize.fmin_cg(InterpolatedFunction1D_2,[point[position]],args=[interpolator,point,position])
 if (solver=="BFGS"): return optimize.fmin_bfgs(InterpolatedFunction1D_2,[point[position]],args=[interpolator,point,position])
 if (solver=="Simplex"): return optimize.fmin(InterpolatedFunction1D_2,[point[position]],args=[interpolator,point,position])

 return None


def InterpolatedFunction1D_2(x,interpolator=None,point=[],position=-1): 
 return -InterpolatedFunction1D(x,interpolator,point,position)

def InterpolatedValue2(x,interpolator):
 return -InterpolatedValue(interpolator,x)


def FindShortestDistance1D(interpolator=None,point=[],solver="Conjugate_gradient_descent",position=-1,y0=0.):
 from scipy import optimize
# def InterpolatedFunction1D(x,interpolator=None,point=[],position=-1):

 if (interpolator==None or len(point)==0): return None
 if (solver=="Conjugate_gradient_descent"):  bestPoint=optimize.fmin_cg(InterpolatedFunction1D_3,[point[position]],args=[interpolator,point,position,y0])
 if (solver=="BFGS"):  bestPoint=optimize.fmin_bfgs(InterpolatedFunction1D_3,[point[position]],args=[interpolator,point,position,y0])
 if (solver=="Simplex"): bestPoint=optimize.fmin(InterpolatedFunction1D_3,[point[position]],args=[interpolator,point,position,y0])

 val=InterpolatedFunction1D(bestPoint[0],interpolator,point,position)[()]
 return (bestPoint[0],val,InterpolatedFunction1D_3(bestPoint[0],interpolator,point,position,y0))





def PlotShortestDistance1D(interpolator=None,point=[],solver="Conjugate_gradient_descent",position=-1,y0=0.):
 from scipy import optimize
# def InterpolatedFunction1D(x,interpolator=None,point=[],position=-1):

 if (interpolator==None or len(point)==0): return None
 if (solver=="Conjugate_gradient_descent"):  bestPoint=optimize.fmin_cg(InterpolatedFunction1D_3,[point[position]],args=[interpolator,point,position,y0])
 if (solver=="BFGS"):  bestPoint=optimize.fmin_bfgs(InterpolatedFunction1D_3,[point[position]],args=[interpolator,point,position,y0])
 if (solver=="Simplex"): bestPoint=optimize.fmin(InterpolatedFunction1D_3,[point[position]],args=[interpolator,point,position,y0])

 val=InterpolatedFunction1D(bestPoint[0],interpolator,point,position)[()]
 

 xs=numpy.ndarray(2)
 ys=numpy.ndarray(2)

 xs[0]=bestPoint[0]
 ys[0]=val
 
 xs[1]=point[position]
 ys[1]=y0
  
# gr1 = ROOT.TGraph(2,xs, ys)
 gr1 = ROOT.TLine(xs[0],ys[0],xs[1],ys[1])
# gr2 = ROOT.TPaveText()
# gr1.SetName("shortest_dist")
 gr1.SetLineColor(4)
# gr1.SetMarkerColor(4)
# gr1.Sort()
# print gr1
 return gr1



def InterpolatedFunction1D_3(x,interpolator=None,point=[],position=-1,y0=0.): 
 x0=point[position]
 y=InterpolatedFunction1D(x,interpolator,point,position)
 return math.sqrt(math.pow(y0-y,2)+math.pow(x0-x,2))
 

def GetSmoothy1D(interpolator=None,point=[],position=-1,minmax=()):
 """ return Smoothy parameter: the number of peaks
     too large value indicates non-smoothy graph
 """
 if (position<0): return None
 if (interpolator==None or len(point)==0): return None
 if (minmax==()): return None

 nStep=int(minmax[0])
 minVal=float(minmax[1])
 maxVal=float(minmax[2])

 if (nStep  == 0 or minVal == maxVal) : return None
 optVal = InterpolatedFunction1D(0.,interpolator,point,-1)


 binW=(maxVal-minVal)/(nStep)
 vals=[]
 xs=[]
 for i in range(nStep):
  x=minVal+binW*i
  xs.append(x)
  val=InterpolatedFunction1D(x,interpolator,point,position)
  vals.append(float(val))

#taken from http://stackoverflow.com/questions/4624970/finding-local-maxima-minima-with-numpy-in-a-1d-numpy-array
# print xs
# print vals

# xs_a=array.array('f',xs)
# data=array.array('f',vals)
 xs_a=numpy.array(xs,dtype=numpy.float)
 data=numpy.array(vals,dtype=numpy.float)
 b = (numpy.diff(numpy.sign(numpy.diff(data))) > 0).nonzero()[0] + 1 # local min
 c = (numpy.diff(numpy.sign(numpy.diff(data))) < 0).nonzero()[0] + 1 # local max
 bb=[xs_a[i] for i in b]
 cc=[xs_a[i] for i in c]
 smoothy=max(float(len(bb))/nStep,float(len(cc))/nStep)
 return (bb,cc,smoothy)


def GetSensitivity(interpolator=None,point=[],position=-1,minmax=()):
 """ return sensitivity as  max[(val-optimalval)/optimalval] """

 if (position<0): return None
 if (interpolator==None or len(point)==0): return None
 if (minmax==()): return None


 nStep=int(minmax[0])
 minVal=float(minmax[1])
 maxVal=float(minmax[2])

 if (nStep  == 0 or minVal == maxVal) : return None
 optVal = InterpolatedFunction1D(0.,interpolator,point,-1)


 binW=(maxVal-minVal)/(nStep)
 vals=[]
 for i in range(nStep):
  x=minVal+binW*i
  val=InterpolatedFunction1D(x,interpolator,point,position)
  if (optVal==0) :
   vals.append(0.)
  else :
   vals.append(abs(val-optVal)/optVal)

 vals=sorted(vals,key=lambda x: x,reverse=True)

 return vals[0]


def GetDerivative1st(x,interpolator=None,point=[],position=-1):
 """ return 1st derivative """
 import DerApproximator as da

 return da.get_d1(InterpolatedFunction1D,x,diffInt=1.5e-6, pointVal = None, args=(interpolator,point,position), stencil = 3, varForDifferentiation = None, exactShape = False)
#							get_d2(fun, vars, fun_d = None, diffInt = 1.5e-4, pointVal = None, args=(), stencil = 3, varForDifferentiation = None, exactShape = True, pointD1 = None)
# if order ==2 :  return da.get_d2(InterpolatedFunction1D,x,fun_d = None, diffInt = 1.5e-4, pointVal = None, args=(interpolator,point,position), stencil = 3, varForDifferentiation = None, exactShape = True, pointD1 = None)

def GetDerivative2nd(x,interpolator=None,point=[],position=-1):
 """ return 2nd derivative """

 import DerApproximator as da
 return da.get_d1(GetDerivative1st,x,diffInt=1.5e-6, pointVal = None, args=(interpolator,point,position), stencil = 3, varForDifferentiation = None, exactShape = False)
 



def GetFunction(interpolator=None,point=[],position=[],x=[],minmax=[]):
 """ return of ND interpolated function"""

 if (len(position)==0 or len(x)==0 or len(position) != len(x)) : return  InterpolatedValue(interpolator,point)
 point_2=[]
 for p in range(len(point)):
  if p in position:
   point_2.append(x[position.index(p)])
  else:
   point_2.append(point[p])

 return InterpolatedValue(interpolator,point_2)



def InterpolatedFunction1D(x,interpolator=None,point=[],position=-1):
 """ return 1D interpolated function"""
 if (position<0): return InterpolatedValue(interpolator,point)

 if (interpolator==None or len(point)==0): return None
 
 return GetFunction(interpolator,point,[position],[x])



def InterpolatedValue(interpolator=None,point=[]):
 """ return interpolated value """

 if (interpolator==None or len(point)==0) : return None
 
 x=numpy.ndarray(len(point),float)
 for i in range(len(point)):
  x[i]=point[i]

 return interpolator(*x)


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


def CreateConfigForOptimization(mva_method="",variableName="",interval=0.5):
 """ create a new config """

 if (len(mva_method)<=0) : return None


 exclude_list=[]
 exclude_file=""
 option_book_list=[]
 option_book_file=""
 option_train_list=[]
# option_train_file=""
# option_train_file="options_train_test_20k.lst"
 option_train_file="optimization_train_test_100k.lst"

 best_result=FindOptimalResult(mva_method)
 if len(best_result) ==0 : return None

 if (len(variableName)>0):
  ss=filter(lambda x: variableName in x[0], best_result[1].items())
  if (len(ss)<=0): return None
  bestVal=ss[0][1]
 
  bestVal=random.uniform(bestVal*(1.-interval),bestVal*(1.+interval))
  _vars=result[1]
  _vars[variableName]=bestVal

 else :
  _vars=best_result[1]
  ss=best_result[1].items()
  for sss in ss:
   bestVal=sss[1]
   bestVal=random.uniform(bestVal*(1.-interval),bestVal*(1.+interval))
   _vars[sss[0]]=bestVal
   print "Optimization: %s %f"%(sss[0],bestVal)

 _id=id()
 
 if (mva_method=="BDT"):  
  execfile("optimization_exclude_template_BDT.py")

# option book list
  execfile("optimization_book_template_BDT.py")
  option_book_list.append("///NameMVA=BDT_"+_id+"\n")

#  print exclude_list
# option train list

  execfile("optimization_train_test_template_BDT.py")

  print "myvars= ", _vars
  return ((_id,exclude_list,option_book_list,option_train_list),_vars)
 
 return ((None,None,None,None),_vars)

def CreateBestVariablesDB(mva_method=""):
 """ create configs DB for variables
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
 separation=0.
 signKS=0.
 bkgKS=0.
 vars={}
 configs=[(_id,exclude_list,option_book_list,option_train_list,separation,signKS,bkgKS,vars)]
# pickle.dump(configs, mva_method+".pkl")
 f=open(mva_method+"_bestvariables"+".gz","wb")
 f.write(zlib.compress(pickle.dumps(configs, pickle.HIGHEST_PROTOCOL),9))
 f.close()

def ReadBestVariables(mva_method):
 """ read configs of BestVariables from gzipped db """

 if (len(mva_method)<=0) : return []

 if not os.path.exists(mva_method+"_bestvariables"+".gz"): return []


 f=open(mva_method+"_bestvariables"+".gz",'rb')
 data=zlib.decompress(f.read()) 
 configs=pickle.loads(data)
 
 return configs


def UpLoadBestVariables(mva_method,config):
 """ upload a new record to db """

 if (len(mva_method)*len(config)<=0): return
 if (not isinstance(config,tuple) ) : return

 if ( list(config).count(None)>0) : return


 f=open(mva_method+"_bestvariables"+".gz",'rb')
 data=zlib.decompress(f.read())
 configs=pickle.loads(data)
 print "current len is ", len(configs)
 f.close()
# _id=id()
# configs.append((_id,)+config)
 configs.append(config)
 f=open(mva_method+"_bestvariables"+".gz",'wb')
 f.write(zlib.compress(pickle.dumps(configs, pickle.HIGHEST_PROTOCOL),9))
 f.close()


def GetKSNumMode(mva_method,mode,varname=[],doPrint=True):

 """ return the dictionanry of type of var:KS for testing NumMode """

 if (len(mva_method)<=0 or not ( mode==3 or mode==4 or mode==5)): return {}

 _varname=varname
 if  (len(_varname)<=0): _varname=ProcessVariables("ks_1.0_corr_1.0")


 configs=ReadBestVariables(mva_method)
 KS={}
 id="000000"
 if mode==3:
   id="NMNone"
 elif mode==4:
   id="NMEqNE"
 elif mode==5:
   id="NMNumE"
 for config in configs:
  if id in config[0]:
   vars=config[7]
   for i, j in vars.items():
    if (i in _varname): KS[i]=j
   break

 if doPrint:
  print "KS for mode ",id
  for i, j in KS.items():
   print i," : ",j
 return KS 


def CreateConfigForVariables(mva_method=""):
 """ create a new config 
  
      for testing of the variables 
      possible modes:

      0 -- default mode, when NormMode=NumEvents and variable lenght of input variables is excluded
      3 -- no exclusions and NormMode=None
      4 -- no exclusions and NormMode=EqualNumEvents
      5 -- no exclusions and NormMode=NormMode=NumEvents

     

 """
 

 mode=0

 if os.path.exists("variables.mode"):
  file=open("variables.mode","r")
  mode=int(file.readline())
  file.close()

 if (len(mva_method)<=0) : return None


 exclude_list=[]
 exclude_file=""
 option_book_list=[]
 option_book_file=""
 option_train_list=[]
 option_train_file=""

 _vars={}
 _id=""
 if (mode==0):
  _id=id()
 elif mode==3:
  _id="NMNone"
 elif mode==4:
  _id="NMEqNE"
 elif mode==5:
  _id="NMNumE" 
  
 
 if (mva_method=="BDT"):  
  if (mode==0):  execfile("bestvariables_exclude_template_BDT.py")
  if (mode>0): execfile("exclude_template_BDT.py")

# option book list

# some predifined values of fast BDT training
  _vars["var1"]=500 #NTrees
  _vars["var2"]=0.90 #BoostType=AdaBoost:UseRandomisedTrees=True
  _vars["var3"]=0.10 #SeparationType=GiniIndex
  _vars["var6"]=0.6 #Shrinkage=0.6
  _vars["var7"]=0.90 #PruneMethod=CostComplexity
  _vars["var8"]=-1 #PruneStrength  

  if (mode==0):  
   _vars["var21"]=0.90 #NormMode=NumEvents\n
  elif mode==3:
   _vars["var21"]=0.10
  elif mode==4:
   _vars["var21"]=0.50
  elif mode==5:
   _vars["var21"]=0.90
 

  execfile("bestvariables_book_template_BDT.py")
  option_book_list.append("///NameMVA=BDT_"+_id+"\n")

#  print exclude_list
# option train list

  execfile("optimization_train_test_template_BDT.py")

  print _vars
  return ((_id,exclude_list,option_book_list,option_train_list),_vars)
 
 return ((None,None,None,None),_vars)



def OptimizeVariablesTraining():
 """ train using the best choice of the variables which was defined in the previous steps """


 democtratic_xsect=GetXSection(tanb,mass_for_mix)

 # signal processing
 signal_files=[]
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


 #create db
 if (not os.path.isfile("./"+mva_method+"_bestvariables.gz")): CreateBestVariablesDB(mva_method)


 #create config

 (config,_vars)=CreateConfigForVariables(mva_method)


# print signal_files,bkg_files,mva_method,config

 #run mva
 RunMVAFromConfig(signal_files,bkg_files,mva_method,config)

# get results
 _separation=GetSeparationMVA(mva_method,config)

 (_sgnKS,_bkgKS)=GetKSMVA(mva_method,config)


 mode=0

 if os.path.exists("variables.mode"):
  file=open("variables.mode","r")
  mode=int(file.readline())
  file.close()
 
 if (mode==0):
  result=config+(_separation,_sgnKS,_bkgKS,{})
 else:
  KS=GetKSIntputVariables(mva_method,config[0])
  result=config+(_separation,_sgnKS,_bkgKS,KS)

# save to DB
 UpLoadBestVariables(mva_method,result)

# check results
 print "CONFIGSSSSS 22222!!!"
 print result
# print ReadResults(mva_method)
# ROOT.gROOT.ProcessLine('.L TMVAGui.C')
# ROOT.TMVAGu()
 return


def GetKSIntputVariables(mva_method="",id=""):
 """ extract KS distance from TMVA root files 
     needed to test NormMode variable
    
 """

 vars={}
 varnames=[]
 sigvars={}
 bkgvars={}
 
 if (len(mva_method)*len(id)<=0): return vars

 file=ROOT.TFile("TMVA_"+mva_method+"_"+id+".root")
  
 currdir=file.GetPath()
 stat=file.cd("InputVariables_Id/")
 if (stat):
  objs=ROOT.gDirectory.GetListOfKeys()
  for obj in objs:
   hist=obj.ReadObj()
   if (hist):
    classname=hist.ClassName()
    if (not "TH1" in classname): continue
    varname=hist.GetName().split("__")[0]
    if ("Signal" in hist.GetName()): sigvars[varname]=hist
    if ("Background" in hist.GetName()): bkgvars[varname]=hist
    if (not varname in varnames): varnames.append(varname)

  for varname in varnames:
   dist=sigvars[varname].KolmogorovTest(bkgvars[varname],"M N")
   vars[varname]=dist

  file.cd(currdir)
 file.Close()

 return vars

def OptimizeVariablesRanking(mva_mehtod="",how_many_best_results=10,doPrint=True,exludeEntries=[]):
 """ do finding the best choice of input variables for MVA """


 if (len(mva_mehtod)<=0): return

 configs=ReadBestVariables(mva_mehtod)


 configs=filter(lambda x: not x[0] in exludeEntries, configs)
#(_id,exclude_list,option_book_list,option_train_list,separation,signKS,bkgKS,{})
 results_sorted=sorted(configs,key=lambda x: x[4],reverse=True)

 best_results=results_sorted[:how_many_best_results]


 print 
 print "Best excluded variables "
 print best_results
 print 

 if (len(best_results)==0): return



 # 3-level rank system


# Idea 
# 1st rank EXCLUDED variables : all training variables of the best point if they are presented for 75% of all other best 
#(with lower results)  
#points (here, 10  best points)
#
#2nd rank  EXCLUDED variables : all variable of remaining  (after selecting 1st rank variables) 
#75% best choices + remaining variables of the best point which 
# were not selected during 1st ranking 
#
#3rd rank EXCLUDED variables: take all variables shared among first half best points which occured to be presented at least in 50% cases and which were not put
# in 1st and 2nd rank selection lists.



 all_vars_1level={}
 all_vars_2level={}
 all_vars_3level={}
 exclude_list2=[]

 exclude_list2.append("nEvt")
 exclude_list2.append("mva")
 exclude_list2.append("flav_cont")
 exclude_list2.append("Pt1")
 exclude_list2.append("Pt2")
 exclude_list2.append("Pt3")
 exclude_list2.append("Pt1_b")
 exclude_list2.append("Pt2_b")
 exclude_list2.append("Pt3_b")
 exclude_list2.append("Pt1_nonb")
 exclude_list2.append("Pt2_nonb")
 exclude_list2.append("Pt3_nonb")
 exclude_list2.append("Eta1_b")
 exclude_list2.append("Eta2_b")
 exclude_list2.append("Eta3_b")
 exclude_list2.append("Eta1_nonb")
 exclude_list2.append("Eta2_nonb")
 exclude_list2.append("Eta3_nonb")
 exclude_list2.append("M12")
 exclude_list2.append("Pt1_c")
 exclude_list2.append("Pt2_c")
 exclude_list2.append("Pt1_q")
 exclude_list2.append("Pt2_q")
 exclude_list2.append("Eta1_c")
 exclude_list2.append("Eta2_c")
 exclude_list2.append("Eta1_q")
 exclude_list2.append("Eta2_q")
 exclude_list2.append("Et1")
 exclude_list2.append("Et2")
 exclude_list2.append("Et3")
 exclude_list2.append("nPV")



 i=0

 # 1,2st levels
# all_vars_1level=dict([best_results[0][1][i], 1] for i in range(len(best_results[0][1])) )
 all_vars_1level=dict([best_results[0][1][i].strip(), 1] for i in range(len(best_results[0][1])) )
 all_vars_1level=dict([i,j] for i, j in all_vars_1level.items() if not i in exclude_list2)
 for result in best_results:
  exclude_list=map(lambda x: x.strip(), result[1])
  exclude_list=filter(lambda x: not x in exclude_list2, exclude_list)
  for var in exclude_list:  
   if var in all_vars_2level:
    all_vars_2level[var]+=1
   else:
    all_vars_2level[var]=1

# print all_vars_1level
# print all_vars_2level

 level2=0.75 # percentage for level 2
# print int(level2*how_many_best_results)

 all_vars_2level=dict([i,j] for i, j in all_vars_2level.items() if j>=int(level2*how_many_best_results ))
# print all_vars_2level

 all_vars_1level_final=dict([i,j] for i, j in all_vars_2level.items() if i in all_vars_1level)
 all_vars_2level_final=dict([i,j] for i, j in all_vars_2level.items() if not i in all_vars_1level_final )
 all_vars_2level_final_2=dict([i,j] for i, j in all_vars_1level.items() if not i in all_vars_2level)
 all_vars_2level_final.update(all_vars_2level_final_2)

# print all_vars_1level_final


 # 3 level
 level3=0.5 # percentage for level 3
 best_results=results_sorted[:int(how_many_best_results/2)]
 for result in best_results:
  exclude_list=map(lambda x: x.strip(), result[1])
  exclude_list=filter(lambda x: not x in exclude_list2, exclude_list)
  for var in exclude_list:
   if var in all_vars_3level:
    all_vars_3level[var]+=1
   else:
    all_vars_3level[var]=1

 all_vars_3level=dict([i,j] for i, j in all_vars_3level.items() if j>=int(level3*how_many_best_results/2.) )
 all_vars_3level_final=dict([i,j] for i, j in all_vars_3level.items() if  not i in all_vars_1level_final and not i in all_vars_2level_final)

 # do sorting



 all_vars_1level_final=sorted(all_vars_1level_final.items(),key=lambda x: x[1], reverse=True)
 all_vars_2level_final=sorted(all_vars_2level_final.items(),key=lambda x: x[1], reverse=True)
 all_vars_3level_final=sorted(all_vars_3level_final.items(),key=lambda x: x[1], reverse=True)

 if (doPrint):
  print "1st rank:"
  for i in all_vars_1level_final:
   print "%s : %d"%(i[0],i[1])

  print "2nd rank:"
  for i in all_vars_2level_final:
   print "%s : %d"%(i[0],i[1])
  print "3rd rank:"
  for i in all_vars_3level_final:
   print "%s : %d"%(i[0],i[1])


# return 1st,2nd,3rd variables
 return (all_vars_1level_final,all_vars_2level_final,all_vars_3level_final)
 




def OptimizeMVA():
 """ example of the whole chain """

 democtratic_xsect=GetXSection(tanb,mass_for_mix)

 # signal processing
 signal_files=[]
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

 #create config

 (config,_vars)=CreateConfigForOptimization(mva_method,"",0.2)

# print "CONFIG"
# print config

 #run mva
 RunMVAFromConfig(signal_files,bkg_files,mva_method,config)

 #save config to db
 UpLoadConfig(mva_method,config) 
 print "CONFIGSSSSS 22222!!!"
# print ReadConfigs(mva_method)


# get results
 _id=config[0]
 _separation=GetSeparationMVA(mva_method,config)
 (_sgnKS,_bkgKS)=GetKSMVA(mva_method,config)
 result=(_id,_vars,_separation,_sgnKS,_bkgKS)
# save results

 print "result=",result
 UploadResult(mva_method,result)

# check results
 print "CONFIGSSSSS 22222!!!"
# print ReadResults(mva_method)

# ROOT.gROOT.ProcessLine('.L TMVAGui.C')
# ROOT.TMVAGu()
 return




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

  print "CreateConfig (vars)= ", _vars
  return ((_id,exclude_list,option_book_list,option_train_list),_vars)
 
 return ((None,None,None,None),_vars)

def ProcessXML(mva_method="",file=""):
 """ do parsing of MVA computer 
     mva_method can be BDT_id
     and return variables used for training
 """

 if (len(mva_method)<=0): return
 
 dir="weights/"
 fileXML="TMVAClassification_"
 fileXML+=mva_method+".weights.xml"

 fullpath="./"+dir+fileXML

 print "fullpath=",fullpath
 if (file!=""): fullpath=file

 if (not os.path.isfile(fullpath)): return

 import ElementTree as ET

 tree = ET.parse(fullpath)
 root = tree.getroot()

 if (not root) : return

 # find section of variables
 vars=root.find("Variables")
 #extract names of vars

 if (not vars): return 

 var_names=[]
 for var in vars.findall("Variable"):
  var_names.append(var.attrib["Expression"])

 return var_names




def PrintPlot(plots=[],canvs=[],Normalized=False,doStack=False,doFilled=False,colors=[],labels=[],fileout="test",style=[],rebin=-1):

 """ Do printing of plots in files """
 """
 prepare_mva.PrintPlot([a2[6],c2[6],v2[6]],[],True,False,False,["kRed","kBlue","kBlack"],["Signal","Backg.","Data"],a2[6].GetName().split("_")[0]+"_qcdGeneral_M350_allData",["hist","E1","E1"])


 """

 if (len(plots)<=0 and len(canvs)<=0): return
 if (len(plots)>0 and len(canvs)>0 ): return

# assert(len(plots)==len(colors))
# assert(len(plots)==len(labels))
  

 _doStack=doStack
 _doFilled=doFilled
 if (Normalized):  _doStack=False
 if (Normalized):  _doFilled=False


 xLegend = 0.75;
 yLegend = 0.72;
 sizeLeg = 0.5;

 if (len(plots)>0):
  _plots=[]
  for plot in plots: _plots.append(plot.Clone())
  _Xtitle=_plots[0].GetTitle()

  for i in range(len(_plots)):
   print labels[i]
   print _plots[i]
   _plots[i].SetTitle(labels[i])
   if (rebin>0): _plots[i].Rebin(rebin)
     

  _plots2=[]
  for i in range(len(_plots)):
   _plots2.append([_plots[i],style[i]])

  hs = None 
  if (_doStack): hs=ROOT.THStack("hs",_Xtitle)
  
  for i in range(len(_plots)): 
   _plots[i].SetLineColor(ROOT.__getattr__(colors[i]))
   if (_doFilled): _plots[i].SetFillColor(ROOT.__getattr__(colors[i]))
  _plots=sorted(_plots,key=lambda x: x.GetMaximum() ,reverse=True)
  _style2=sorted( _plots2, key=lambda x: x[0].GetMaximum(),reverse=True)
  _style=[]
  for i in  range(len(_style2)): _style.append(_style2[i][1])
  style=_style
  print _Xtitle
  canv1=ROOT.TCanvas("plot_%d"%random.uniform(1,1000),_Xtitle)
  ROOT.TGaxis.SetMaxDigits(3);
  ROOT.gPad.SetFrameBorderMode(0);
  ROOT.gPad.SetRightMargin(0.25);
  ROOT.gPad.SetLeftMargin(0.20);
  ROOT.gPad.SetBottomMargin(0.20);

  _plots[0].GetXaxis().SetTitle(_Xtitle)
  _plots[0].GetYaxis().SetTitle("#frac{dN}{d(%s)}"%_Xtitle) 


  if (Normalized): 
   ROOT.SetOwnership(_plots[0],False)
   _plots[0].GetYaxis().SetTitle("a.u")
   integ=_plots[0].Integral()
#   _plots[0].DrawNormalized()
   if (integ>0): _plots[0].Scale(1e0/integ)
   if (len(style)>0):  _plots[0].Draw(style[0])
   else: _plots[0].Draw("hist")
   print "Norm"
  elif _doStack:
   hs.Add(_plots[0])
  else: 
   ROOT.SetOwnership(_plots[0],False)
   if (len(style)>0):  _plots[0].Draw("hist E1")
   else:   _plots[0].Draw("hist E1")

  for i in range(1,len(_plots)):
   if (not _doStack):
    if (Normalized): 
     ROOT.SetOwnership(_plots[i],False)
#     _plots[i].DrawNormalized("same")
     integ=_plots[i].Integral()
     if (integ>0): _plots[i].Scale(1e0/integ)
     if (len(style)>1):  _plots[i].Draw("same "+style[i])
     else: _plots[i].Draw("same E1")
    else: 
      ROOT.SetOwnership(_plots[i],False)
      if (len(style)>1):  _plots[i].Draw("same "+style[i])
      else: _plots[i].Draw("same E1")
   else: 
    hs.Add(_plots[i])
    ROOT.SetOwnership(_plots[i],False)

  if (_doStack): 
   ROOT.SetOwnership(hs,False)
   hs.SetTitle(_Xtitle)
   hs.Draw("hist NOSTACK")
   print _Xtitle
   hs.GetHistogram().SetTitle(_Xtitle)
   hs.GetHistogram().SetXTitle(_Xtitle)
   hs.GetHistogram().SetYTitle("#frac{dN}{d(%s)}"%_Xtitle)
   if (_doFilled):
    hs.Draw("hist NOSTACK")
   else:
    hs.Draw("hist")


  leg=canv1.BuildLegend(xLegend , yLegend - 0.5*sizeLeg , xLegend + 0.4*sizeLeg, yLegend)
  leg.SetFillColor(0)
  leg.SetTextSize(0.031);
  leg.SetFillStyle (0);
  leg.SetBorderSize(0);
 
  _plots[0].SetTitle(_Xtitle)
  ROOT.SetOwnership(canv1,False)
  canv1.Print(fileout+".png","png")

 if (len(canvs)>0):
  for i in range(len(canvs)):
   canvs[i].Print(fileout+"_%d"%i+".png","png")

 return

def start_proof (workers='6'):

 """ requested by TestMVAOutPut
     
     Organize proof cluster for fast getting MVA output

 """

 proof= ROOT.TProof.Open ('workers='+workers)
 time.sleep(3)                     # needed for GUI to settle
 proof.Exec ('TPython::Exec("%s");' % \
   ("import sys; sys.path.insert(0,'"+os.path.dirname(os.path.abspath("pyselect"))+"')"))
 ROOT.TProof.AddEnvVar ("PYTHONHOME", sys.prefix+":"+sys.exec_prefix)
 return proof



def TestMVACuts(mva_method="",tree_name="",vars=["M12"],cuts="",sgn=[],bkg=[],data=[],nEvt=10000,lumi=1e3,useRandomizer=True,doData=False):

 """ do testing of mva discriminators """
 """
# How to get a pattern for QCD general
 ls -d ../trees_for_training_v4/*/ | grep "Pt"| grep "to" | awk  -F'_' '{print $7}'
 
# How to plot
 a2,b2,c2,d2,k2,m2,n2,v2,w2=prepare_mva.TestMVACuts("BDT_560008","KinVarsBDT",[],"cut<=-0.05",["M-350"],
 ["30to50","50to80","80to120","120to170","170to300","300to470","470to600","600to800","800to1000"],[],-1,1e3,False,True)
 prepare_mva.PrintPlot([a2[6],c2[6],v2[6]],[],True,False,False,["kRed","kBlue","kBlack"],["Signal","Backg.","Data"],
 a2[6].GetName().split("_")[0]+"_qcdGeneral_M350_allData",["hist","E1","E1"])


 # example of getting plots for all variables


 ## b enriched sample
  a,b,c2,d2,k2,m2,n2,v2,w2=prepare_mva.TestMVACuts("BDT_560008","KinVarsBDT",
 ["detajet2jet3","maxdijetmass","mindijetmass","aplanarity","sphericity","Eta1","Eta2",
 "Eta3","dptjet1jet2","dptjet1jet3","djet1jet2pt","detajet1jet2","dthetajet1jet2_boost",
 "dphijet1jet2_boost","dphijet1jet2","dphijet2jet3","dphijet1jet3","Et2byEt1","Et3byEt1",
 "Et3byEt2","sphericity_boost","thetajet1_boost12","thetajet3_boost12","dphijet2jet3_boost12","D","isotropy"],
 "cut<=-0.05",["M-350"],[],[],-1,1e3,False,True)

 ## QCD general
 a,b,c,d,k,m,n,v,w=prepare_mva.TestMVACuts("BDT_560008","KinVarsBDT",["detajet2jet3","maxdijetmass",
 "mindijetmass","aplanarity","sphericity","Eta1","Eta2",
 "Eta3","dptjet1jet2","dptjet1jet3",
 "djet1jet2pt","detajet1jet2","dthetajet1jet2_boost","dphijet1jet2_boost","dphijet1jet2",
 "dphijet2jet3","dphijet1jet3","Et2byEt1","Et3byEt1","Et3byEt2","sphericity_boost","thetajet1_boost12",
 "thetajet3_boost12","dphijet2jet3_boost12","D","isotropy"],"cut<=-0.05",["M-350"],["_*to*_"],[],-1,1e3,False,True)

 # plot all vairables
 for i in range(len(a)): prepare_mva.PrintPlot([a[i],c[i],c2[i],v[i]],[],True,False,False,["kRed","kBlue","kGreen","kBlack"],
 ["Signal","BackDg.(QCDgeneral)","Backg.(QCDBenrich)","Data"],c[i].GetName().split("_")[0]+"_qcdbGeneral_qcdBenriched_560008_rebin3",
 ["hist","hist","E1","E1"],3)

 """

 # returns ([Signal vars before],[Signal vars after],[Bkg vars before],[Bkg vars after],[Eff signal,Eff back, B/S]) 

 if (len(mva_method)*len(tree_name)<=0): return ([None],[None],[None],[None],[0,0,0])
 
 print "Start TestMVACuts"
 print mva_method

 var_names=ProcessXML(mva_method)
 plots={}

 print var_names
 dir=os.getcwd()+"/weights/"
 fileXML="TMVAClassification_"
 fileXML+=mva_method+".weights.xml"

 _sgns=[]

 if len(sgn)==0 : _sgns=mass
 else: _sgns=sgn

 _bkgs=[]
 if len(bkg)==0 : _bkgs=BkgOvertrain
 else: _bkgs=bkg

 _data=[]
 if (len(data)==0): 
  _data=datapattern
  lumi=3875
 else: _data=data
# lumi=1e3
 
 
 # signal
 democtratic_xsect=GetXSection(tanb,mass_for_mix)


#prepare_mva.GetListFiles("*the*30To50*root","/data/user/marfin/CMSSW_5_3_3/src/Analysis/HbbMSSMAnalysis/test/Analysis2012/trees_for_training/"

 signal_weights=[]
 signal_files=[]
 files=[ GetListFiles(trees_path+"/*"+m+scenario_template,trees_path) for m in _sgns ]
 print "Signal files"
 
 for item in files:
  print item
  if (len(item)==0): continue
  (item,masses)=GetMassFromName(item)
  (item,numevts)=GetNumEvt(item)
  (item,lumiwgts)=GetLumiWeight(item)
  if (democtratic_mix and len(sgn)==0):
   xsects=map(lambda x:  democtratic_xsect,masses)
  else:
   xsects=map(lambda x:  GetXSection(tanb,float(x)),masses)
  newwgts=GetNewWeight(1e3,lumiwgts,numevts,xsects)



  print lumiwgts
  print newwgts
  print item
  print numevts



  filesnew=map(lambda x: item[x].replace(".root","_update.root") ,range(len(item)))
  if (not os.path.exists(filesnew[0])): ReWeight(tree_name, list_of_files=item, weight=newwgts)
  signal_files+=filesnew
  weight=sum(numevts)
  if (lumi!=1e3): weight*=lumi/1e3 
  print "weight=",weight
  print "filesnew=",filesnew
  for ii in filesnew: signal_weights.append([ii,weight])

 print "Ho"

 # background
 bkg_files=[]
 bkg_weights=[]
 files=[ GetListFiles(trees_path+"/*"+ptbin+scenario_template,trees_path) for ptbin in   _bkgs ]
 for item in files:
#  print item
  if (len(item)==0): continue
  (item,numevts)=GetNumEvt(item)
  (item,lumiwgts)=GetLumiWeight(item)
  newwgts=GetNewWeight(1e3,lumiwgts,numevts)


  print lumi
  print lumiwgts
  print newwgts
  print item
  print numevts
  filesnew=map(lambda x: item[x].replace(".root","_update.root") ,range(len(item)))
  if (not os.path.exists(filesnew[0])):   ReWeight(tree_name, list_of_files=item, weight=newwgts)
  bkg_files+=filesnew
  weight=sum(numevts)
  print "weight before=",weight
  if (lumi!=1e3): weight*=lumi/1e3 
  print "weight after=",weight
  for ii in filesnew: bkg_weights.append([ii,weight])

 print "data here"
 # data files
 data_files=[]
 data_weights=[]
 if (doData): 
  files=[ GetListFiles(data_trees_path+"/*"+x+scenario_template_data,data_trees_path) for x in   _data ]
  for item in files:
   print item
   if (len(item)==0): continue
   (item,numevts)=GetNumEvt(item)
   weight=numevts
   filesnew=map(lambda x: item[x],range(len(item)))
   data_files+=filesnew
   for ii in range(len(item)): data_weights.append([filesnew[ii],weight[ii]])
   print "data weights=",data_weights
 
 chain_sig=ROOT.TChain(tree_name)
 chain_bkg=ROOT.TChain(tree_name)
 if (doData): chain_data=ROOT.TChain(tree_name)

# it helps to solve the overtraining?
 random.shuffle(signal_files)
 random.shuffle(bkg_files)



 for file in signal_files:
  chain_sig.Add(file)

 for file in bkg_files:
  chain_bkg.Add(file)

 if (doData):
  for file in data_files:
   chain_data.Add(file)

 _signEvt=chain_sig.GetEntries()
 _bkgnEvt=chain_bkg.GetEntries()

 if (nEvt<0):    _nEvtSig=_signEvt
 elif (nEvt>_signEvt): _nEvtSig=_signEvt
 else:  _nEvtSig=nEvt

 if (nEvt<0):    _nEvtBkg=_bkgnEvt
 elif (nEvt>_bkgnEvt): _nEvtBkg=_bkgnEvt
 else:  _nEvtBkg=nEvt

 if cuts=="":
  _mva=mva_method.split("_")
  _cuts=GetsBKGPeaks(_mva[0],_mva[1])
  _cuts=_cuts.replace("\n"," || ")
 else: _cuts=cuts


 if (useRandomizer):
# here,try to do randomizing signal
  entrylists=[]
  entrylistindex=[]
  chain_sig.Draw(">>+ myListSig","", "entrylist")
  print "here"
  print ROOT.myListSig
  k=0
  for lst in ROOT.myListSig.GetLists():  
   entrylists.append(lst)
   entrylistindex.append(k)
 #  print "Before k=",k," GetN()=",lst.GetN()
   k=k+1



  _numremove=0 # how many elements to remove from entrylists
  _numremove=_signEvt-_nEvtSig

 # print "All sgn nevt", _signEvt
 # print "All sgn evt to remove", _numremove

  gg=0
  while gg<_numremove:
   gg=gg+1
   lstind=int(random.uniform(0,len(entrylistindex)))
   lstind2=entrylistindex[lstind]
   if (entrylists[lstind2].GetN()==0):
#    print "Removing index ",lstind2, " gg=",gg
    del entrylistindex[lstind]
    gg=gg-1
    continue

   numevt=int(random.uniform(0,entrylists[lstind2].GetN()))
   numevt=entrylists[lstind2].GetEntry(numevt)
   stat=entrylists[lstind2].Remove(numevt) 
   if not stat: 
     print "not ok", " numevt=",numevt
     gg=gg-1 

#  print "After i=",0," GetN()=",entrylists[0].GetN()
  for i in range(1,len(entrylists)):
   entrylists[0].Add(entrylists[i])
#   print "After i=",i," GetN()=",entrylists[i].GetN()

#  print "Remaining Sgn evt ", entrylists[0].GetN() 
  chain_sig.SetEntryList(entrylists[0])




#  here,try to randomizing background
  entrylists=[]
  entrylistindex=[]
 
  chain_bkg.Draw(">>+ myListBkg","", "entrylist")
  k=0
  for lst in ROOT.myListBkg.GetLists():
   entrylists.append(lst)
#   print "Before k=",k," GetN()=",lst.GetN()
   entrylistindex.append(k)
   k=k+1
 
  _numremove=0 # how many elements to remove from entrylists
  _numremove=_bkgnEvt-_nEvtBkg
 
  print "All bkg evt", _bkgnEvt
  print "All bkg evt to remove", _numremove
 
  gg=0
  while gg<_numremove:
   gg=gg+1
   lstind=int(random.uniform(0,len(entrylistindex)))
   lstind2=entrylistindex[lstind]
   if (entrylists[lstind2].GetN()==0):
    del entrylistindex[lstind]
#    print "Removing index ",lstind2, " gg=",gg
    gg=gg-1
    continue

   numevt=int(random.uniform(0,entrylists[lstind2].GetN()))
   numevt=entrylists[lstind2].GetEntry(numevt)
   stat=entrylists[lstind2].Remove(numevt)
   if not stat:
     print "not ok", " numevt=",numevt
     gg=gg-1


#  print "After i=",0," GetN()=",entrylists[0].GetN()
  for i in range(1,len(entrylists)):
#   print "After i=",i," GetN()=",entrylists[i].GetN() 
   entrylists[0].Add(entrylists[i])

#  print "Remaining BKg evt", entrylists[0].GetN()
  chain_bkg.SetEntryList(entrylists[0])


 _vars=[]
 if len(vars)>0 : _vars=vars
 else: _vars=var_names

 for var in _vars:
  sngMin=chain_sig.GetMinimum(var)
  sngMax=chain_sig.GetMaximum(var)
#  print "max=",sngMax
 # print "min=",sngMin
  bkgMin=chain_bkg.GetMinimum(var)
  bkgMax=chain_bkg.GetMaximum(var)
#  print "max=",bkgMax
#  print "min=",bkgMin
#  print "50:%f:%f"%(min(bkgMin,sngMin),min(sngMax,bkgMax))
  plots[var]="50:%f:%f"%(min(bkgMin,sngMin),min(sngMax,bkgMax))

 proof=start_proof("8")




# signal 
 
 chain_sig.SetProof(True,True)
 list_vars=ROOT.TList()
 list_vars.SetName("Variables")
 for var in var_names: list_vars.Add(ROOT.TObjString(var))
 proof.AddInput(list_vars)

 list_wgt=ROOT.TList()
 list_wgt.SetName("Weights")
 for weight in signal_weights: list_wgt.Add(ROOT.TNamed(weight[0],str(weight[1])) )
 proof.AddInput(list_wgt)


 list_plots=ROOT.TList()
 list_plots.SetName("Plots")
 for var in  plots: list_plots.Add(ROOT.TNamed(var,plots[var]))
 proof.AddInput(list_plots)

 proof.AddInput(ROOT.TNamed("Prefix","_S"))

 fileXML=ROOT.TNamed("fileXML",fileXML)
 dir=ROOT.TNamed("dir",dir)
 proof.AddInput(fileXML)
 proof.AddInput(dir)
 proof.AddInput(ROOT.TNamed("MVA",mva_method))
 proof.AddInput(ROOT.TNamed("CUT",_cuts))

 chain_sig.Process('TPySelector', 'MyPySelectorPlots' ,_nEvtSig) # nEvt event
 outputS=proof.GetOutputList()
 
 signal_before=[]
 signal_after=[]
 
 for out in outputS:
  if ("_S" and "_before" in out.GetName()): 
   ROOT.SetOwnership(out,False)
   signal_before.append(out)
  if ("_S" and "_after" in out.GetName()): 
   ROOT.SetOwnership(out,False)
   signal_after.append(out)

 proof.ClearInput()
 proof.ClearCache()
 proof.ClearInputData()
 proof.ClearDataSetCache()
#   proof.Close()
 ROOT.TProof.Reset("",1)

# background

 proof=start_proof("8")
 chain_bkg.SetProof(True,True)
 proof.AddInput(list_vars)

 list_wgt2=ROOT.TList()
 list_wgt2.SetName("Weights")
 for weight in bkg_weights: list_wgt2.Add(ROOT.TNamed(weight[0],str(weight[1])) )
 proof.AddInput(list_wgt2)


 proof.AddInput(list_plots)
 proof.AddInput(ROOT.TNamed("Prefix","_B"))
 proof.AddInput(fileXML)
 proof.AddInput(dir)
 proof.AddInput(ROOT.TNamed("MVA",mva_method))
 proof.AddInput(ROOT.TNamed("CUT",_cuts))

 chain_bkg.Process('TPySelector', 'MyPySelectorPlots' ,_nEvtBkg) # nEvt event
 outputB=proof.GetOutputList()

 bkg_before=[]
 bkg_after=[]
 for out in outputB:
  if ("_B" and "_before" in out.GetName()): 
   ROOT.SetOwnership(out,False)
   bkg_before.append(out)
  if ("_B" and "_after" in out.GetName()): 
   ROOT.SetOwnership(out,False)
   bkg_after.append(out)


 proof.ClearInput()
 proof.ClearCache()
 proof.ClearInputData()
 proof.ClearDataSetCache()
#   proof.Close()
 ROOT.TProof.Reset("",1)


# data

 if (doData): 
  proof=start_proof("8")
  chain_data.SetProof(True,True)
  proof.AddInput(list_vars)

  list_wgt3=ROOT.TList()
  list_wgt3.SetName("Weights")
  for weight in data_weights: list_wgt3.Add(ROOT.TNamed(weight[0],str(weight[1])) )
  proof.AddInput(list_wgt3)


  proof.AddInput(list_plots)
  proof.AddInput(ROOT.TNamed("Prefix","_Data"))
  proof.AddInput(fileXML)
  proof.AddInput(dir)
  proof.AddInput(ROOT.TNamed("MVA",mva_method))
  proof.AddInput(ROOT.TNamed("CUT",_cuts))

  chain_data.Process('TPySelector', 'MyPySelectorPlots' ,-1) # nEvt event
  outputData=proof.GetOutputList()

  data_before=[]
  data_after=[]
  for out in outputData:
   if ("_Data" and "_before" in out.GetName()): 
    ROOT.SetOwnership(out,False)
    data_before.append(out)
   if ("_Data" and "_after" in out.GetName()): 
    ROOT.SetOwnership(out,False)
    data_after.append(out)


  proof.ClearInput()
  proof.ClearCache()
  proof.ClearInputData()
  proof.ClearDataSetCache()
#   proof.Close()
  ROOT.TProof.Reset("",1)




# calculate some quantities
 eff_S=[]
 eff_B=[]
 B_over_S=[]
 for i in range(len(signal_before)):
  if (signal_before[i].GetEntries()>0): eff_S.append(float(signal_after[i].GetEntries())/float(signal_before[i].GetEntries()))
  else : eff_S.append(0.)
  if (bkg_before[i].GetEntries()>0) : eff_B.append(float(bkg_after[i].GetEntries())/float(bkg_before[i].GetEntries()))
  else: eff_B.append(0.)
  if (signal_after[i].GetEntries()>0 and bkg_before[i].GetEntries()>0): B_over_S.append( float(bkg_after[i].GetEntries())/ float(signal_after[i].GetEntries()) * float(signal_before[i].GetEntries())/float(bkg_before[i].GetEntries()) )
  else:  B_over_S.append(0.)
 
 if (doData): return (signal_before,signal_after,bkg_before,bkg_after,eff_S,eff_B,B_over_S,data_before,data_after)
 return (signal_before,signal_after,bkg_before,bkg_after,eff_S,eff_B,B_over_S)


def TestMVAOutPut(mva_method="",tree_name="",weighted=True,nEvt=-1,doProof=True):
 """ performs a test of mva:

     mva_method is like 'BDT_id'
     if weighted == True : it uses weights
     if len(mva_method) == 0 : it uses original files processed during training!
     if len(tree_name) == 0 :  it uses TMVA_"mva_method".root file having test trees!

 """

 if (len(mva_method)<=0) : return

 var_names=ProcessXML(mva_method)
 vars_Test={}
 vars_Train={}

 for var in var_names:
  vars_Test[var]=array.array('f',[0])
  vars_Train[var]=array.array('f',[0])

 wgt_Test=array.array('f',[0])
 wgt_Train=array.array('f',[0])
 
  ## create readers
 reader_Test=ROOT.TMVA.Reader()
 reader_Train=ROOT.TMVA.Reader()


 dir=os.getcwd()+"/weights/"
 fileXML="TMVAClassification_"
 fileXML+=mva_method+".weights.xml"

 for var in var_names:
  reader_Test.AddVariable(var, vars_Test[var])
  reader_Train.AddVariable(var, vars_Train[var])

 print "mva_method in reader ",mva_method
 reader_Test.BookMVA(ROOT.TString(mva_method),ROOT.TString(dir+fileXML))
 reader_Train.BookMVA(ROOT.TString(mva_method),ROOT.TString(dir+fileXML))

## Test MVA output
 mva_Test_S=ROOT.TH1F("mva_Test_S","mva_Test_S",100,-2.0,2.0)
 mva_Test_B=ROOT.TH1F("mva_Test_B","mva_Test_B",100,-2.0,2.0)
 mva_Test_S.SetLineColor(ROOT.kBlue)
 mva_Test_B.SetLineColor(ROOT.kRed)
 mva_Test_S.Sumw2()
 mva_Test_B.Sumw2()
  
## Train MVA output
 mva_Train_S=ROOT.TH1F("mva_Train_S","mva_Train_S",50,-0.6,0.6)
 mva_Train_B=ROOT.TH1F("mva_Train_B","mva_Train_B",50,-0.6,0.6)
 mva_Train_S.SetLineColor(ROOT.kBlue)
 mva_Train_B.SetLineColor(ROOT.kRed)
 mva_Train_S.Sumw2()
 mva_Train_B.Sumw2()


 if (len(mva_method)>0 and len(tree_name)>0):

  democtratic_xsect=GetXSection(tanb,mass_for_mix)

  signal_files=[]
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
   if (not os.path.exists(filesnew[0])):   ReWeight(tree_name, list_of_files=item, weight=newwgts)
   signal_files+=filesnew


 # background processing
  bkg_files=[]
  if (doProof):
   files=[ GetListFiles(trees_path+"/*"+ptbin+scenario_template,trees_path) for ptbin in   BkgOvertrain ]
  else:
   files=[ GetListFiles(trees_path+"/*"+ptbin+scenario_template,trees_path) for ptbin in ptbins ]
  for item in files:
#   print item
   if (len(item)==0): continue
   (item,numevts)=GetNumEvt(item)
   (item,lumiwgts)=GetLumiWeight(item)
   newwgts=GetNewWeight(1e3,lumiwgts,numevts)
   filesnew=map(lambda x: item[x].replace(".root","_update.root") ,range(len(item)))
   if (not os.path.exists(filesnew[0])):   ReWeight(tree_name, list_of_files=item, weight=newwgts)
   bkg_files+=filesnew


  chain_sig=ROOT.TChain(tree_name)
  chain_bkg=ROOT.TChain(tree_name)

 # it helps to solve the overtraining?
  random.shuffle(signal_files)
  random.shuffle(bkg_files)


  for file in signal_files:
   chain_sig.Add(file)

  for file in bkg_files:
   chain_bkg.Add(file)


####Proof support here
  if doProof:
   canv1=ROOT.TCanvas("mva_test_%d"%random.uniform(1,1000),"test")
   _signEvt=chain_sig.GetEntries()
   _bkgnEvt=chain_bkg.GetEntries()


   if (nEvt<0):    _nEvtSig=nEvt
   elif (nEvt>_signEvt): _nEvtSig=_signEvt
   else:  _nEvtSig=nEvt

   if (nEvt<0):    _nEvtBkg=nEvt
   elif (nEvt>_bkgnEvt): _nEvtBkg=_bkgnEvt
   else:  _nEvtBkg=nEvt


   proof=start_proof("8")

# signal 
   chain_sig.SetProof(True,True)
   proof.AddInput(mva_Test_S)
   list_vars=ROOT.TList()
   list_vars.SetName("Variables")
   for var in var_names: list_vars.Add(ROOT.TObjString(var))
   proof.AddInput(list_vars)
   fileXML=ROOT.TNamed("fileXML",fileXML)
   dir=ROOT.TNamed("dir",dir)
   proof.AddInput(fileXML)
   proof.AddInput(dir)
   proof.AddInput(ROOT.TNamed("MVA",mva_method))
   chain_sig.Process('TPySelector', 'MyPySelector' ,_nEvtSig) # nEvt event
   output=proof.GetOutputList()
   if (output):
    result=output.FindObject("mva_Test_S")
    if (result): mva_Test_S=result
      
   proof.ClearInput()
   proof.ClearCache()
   proof.ClearInputData()
   proof.ClearDataSetCache()
#   proof.Close()
   ROOT.TProof.Reset("",1)
# background
   
   proof=start_proof("8")
   chain_bkg.SetProof(True,True)
   proof.AddInput(mva_Test_B)
   proof.AddInput(list_vars)
   proof.AddInput(fileXML)
   proof.AddInput(dir)
   proof.AddInput(ROOT.TNamed("MVA",mva_method))
   chain_bkg.Process('TPySelector', 'MyPySelector' ,_nEvtBkg) # nEvt event
   output=proof.GetOutputList()
   if (output):
    result=output.FindObject("mva_Test_B")
    if (result): mva_Test_B=result
   
   proof.ClearInput()
   
   print mva_Test_S.Integral()
   print mva_Test_B.Integral()

  
   mva_Test_S.DrawNormalized()
   mva_Test_B.DrawNormalized("same")

   ROOT.SetOwnership(mva_Test_S,False)
   ROOT.SetOwnership(mva_Test_B,False)
   ROOT.SetOwnership(canv1,False)
   return (mva_Test_S,mva_Test_B,canv1)
#   return (mva_Test_S,mva_Test_B)




  for var in var_names:
   chain_sig.SetBranchAddress(var,vars_Test[var])
   chain_bkg.SetBranchAddress(var,vars_Train[var])

  chain_sig.SetBranchAddress("weight",wgt_Test)
  chain_bkg.SetBranchAddress("weight",wgt_Train) 
 
  signEvt=chain_sig.GetEntries()
  bkgnEvt=chain_bkg.GetEntries()

  doMix=True
  if (nEvt<=0) : 
   print "signEvt=",signEvt
   print "bkgnEvt=",bkgnEvt
   nEvt=min(signEvt,bkgnEvt)
   doMix=False

  entry=0

  while True:
   if (entry%100==0): print "entry: ",entry
   entry+=1
   if (doMix):
    nSigEvt=int(random.uniform(0,signEvt))
    nBkgEvt=int(random.uniform(0,bkgnEvt))
   else:
    nSigEvt=entry-1
    nBkgEvt=entry-1

   chain_sig.GetEntry(nSigEvt)
   chain_bkg.GetEntry(nBkgEvt)

   if (weighted):
    mva_Test_S.Fill(reader_Test.EvaluateMVA(mva_method),wgt_Test[0])
    mva_Test_B.Fill(reader_Train.EvaluateMVA(mva_method),wgt_Train[0])
   else:
    mva_Test_S.Fill(reader_Test.EvaluateMVA(mva_method))
    mva_Test_B.Fill(reader_Train.EvaluateMVA(mva_method))

   if (entry==nEvt) : break

  canv1=ROOT.TCanvas("mva_test_%d"%random.uniform(1,1000),"test")

  _min=mva_Test_S.GetXaxis().GetXmin()
  _max=mva_Test_S.GetXaxis().GetXmax()
  _min*=2.
  _max*=2.
  print _min
  mva_Test_S.GetXaxis().SetRangeUser(_min,_max)

  mva_Test_S.DrawNormalized()
  mva_Test_B.DrawNormalized("same")


  ROOT.SetOwnership(canv1,False)

  ROOT.SetOwnership(mva_Test_S,False)
  ROOT.SetOwnership(mva_Test_B,False)
  return (canv1,None)

 if (len(mva_method)>0 and len(tree_name)<=0):
  file=ROOT.TFile("TMVA_"+mva_method+".root")
  if (not file): return
  TestTree=file.Get("TestTree")
  TrainTree=file.Get("TrainTree")
  if not (TestTree and TrainTree): return
  

  for var in var_names:
   TestTree.SetBranchAddress(var,vars_Test[var])
   TrainTree.SetBranchAddress(var,vars_Train[var])

   
  TestTree.SetBranchAddress("weight",wgt_Test)
  TrainTree.SetBranchAddress("weight",wgt_Train)

  id_Test=array.array('i',[0])
  id_Train=array.array('i',[0])
  TestTree.SetBranchAddress("classID",id_Test)
  TrainTree.SetBranchAddress("classID",id_Train)

  ROOT.TH1F.__init__._creates = False

  print "test"
  entry=0
  nEvt_S=0
  nEvt_B=0
  while TestTree.GetEntry(entry):
   entry += 1

   if (nEvt>0 and nEvt_S>=nEvt and nEvt_B>=nEvt): break

   if (entry%1000==0): print "entry %d"%entry
 
   if (nEvt>0 and nEvt_S<nEvt and id_Test[0]==0 ): nEvt_S+=1
   if (nEvt>0 and nEvt_S>=nEvt and id_Test[0]==0 ): continue
   if (nEvt>0 and nEvt_B<nEvt and id_Test[0]==1 ): nEvt_B+=1
   if (nEvt>0 and nEvt_B>=nEvt and id_Test[0]==1 ): continue

   if (weighted):
    if (id_Test[0]==0 ): mva_Test_S.Fill(reader_Test.EvaluateMVA(mva_method),wgt_Test[0])
    if (id_Test[0]==1): mva_Test_B.Fill(reader_Test.EvaluateMVA(mva_method),wgt_Test[0])
   else:
    if (id_Test[0]==0): mva_Test_S.Fill(reader_Test.EvaluateMVA(mva_method))
    if (id_Test[0]==1): mva_Test_B.Fill(reader_Test.EvaluateMVA(mva_method))

  print "train"  

  entry=0
  nEvt_S=0
  nEvt_B=0
  while TrainTree.GetEntry(entry):
   entry += 1

   if (nEvt>0 and nEvt_S>=nEvt and nEvt_B>=nEvt): break

   if (entry%1000==0): print "entry %d"%entry
   if (nEvt>0 and nEvt_S<nEvt and id_Test[0]==0 ): nEvt_S+=1
   if (nEvt>0 and nEvt_S>=nEvt and id_Test[0]==0 ): continue
   if (nEvt>0 and nEvt_B<nEvt and id_Test[0]==1 ): nEvt_B+=1
   if (nEvt>0 and nEvt_B>=nEvt and id_Test[0]==1 ): continue

   if (weighted):
    if (id_Train[0]==0): mva_Train_S.Fill(reader_Train.EvaluateMVA(mva_method),wgt_Train[0])
    if (id_Train[0]==1): mva_Train_B.Fill(reader_Train.EvaluateMVA(mva_method),wgt_Train[0])
   else:
    if (id_Train[0]==0): mva_Train_S.Fill(reader_Train.EvaluateMVA(mva_method))
    if (id_Train[0]==1): mva_Train_B.Fill(reader_Train.EvaluateMVA(mva_method))

  print mva_Test_S,mva_Test_B,mva_Train_S,mva_Train_B

  canv1=ROOT.TCanvas("mva_test_%d"%random.uniform(1,1000),"test")
  _min=mva_Test_S.GetXaxis().GetXmin()
  _max=mva_Test_S.GetXaxis().GetXmax()
  _min*=2.
  _max*=2.
  mva_Test_S.GetXaxis().SetRangeUser(_min,_max)
  mva_Test_S.DrawNormalized()
  mva_Test_B.DrawNormalized("same")

  canv2=ROOT.TCanvas("mva_train_%d"%random.uniform(1,1000),"train")
  _min=mva_Train_S.GetXaxis().GetXmin()
  _max=mva_Train_S.GetXaxis().GetXmax()
  _min*=2.
  _max*=2.
  mva_Train_S.GetXaxis().SetRangeUser(_min,_max)
  mva_Train_S.DrawNormalized()
  mva_Train_B.DrawNormalized("same")

  ROOT.SetOwnership(canv1,False)
  ROOT.SetOwnership(canv2,False)

  ROOT.SetOwnership(mva_Test_S,False)
  ROOT.SetOwnership(mva_Test_B,False)
  ROOT.SetOwnership(mva_Train_S,False)
  ROOT.SetOwnership(mva_Train_B,False)
 

  print mva_Test_S
  print mva_Test_B
  print mva_Train_S
  print mva_Train_B

  return (canv1, canv2,mva_Test_S,mva_Test_B ,mva_Train_S,mva_Train_B)

# return (None,None,None,None)

 return None,None

def ProcessVariables(order="Correlation",varstable=[],doSelection=False,doInversion=False):
 """ test all variables """

 democtratic_xsect=GetXSection(tanb,mass_for_mix)

 signal_files=[]
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


 democtratic_xsect=GetXSection(tanb,mass_for_mix)


 # signal processing
 signal_files=[]
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


def RunMVAfromConfig_Id(id="",path2DB=""):
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


def Prepare_Regression_Computers(methods=[]):

 """ prepare regression analysers for MVA optimization """

 if not os.path.exists("./OptimizeTrees.root"): return


 analysers=""
 if (len(methods)>0):
  for method in methods: analysers+=method+","
  analysers=analysers[:-1]
 else: analysers="BDT,LD,SVM,MLP"


 funs=ROOT.gROOT.GetListOfGlobalFunctions()
 isOk=funs.FindObject("TMVARegression") # 
 print "isOK=",isOk
 if (isOk==None): ROOT.gROOT.ProcessLine('.L TMVARegression.C')
 ROOT.TMVARegression(analysers)


 return


class Regression_MVA_Functor():
 """ to represent MVA regressor """

 # args
 """
  0 -- method name 

 """
 def __init__(self,method):
  
  self._method=method
  self.order=[]
  if (method==""): self._method="BDT"
  dir=os.getcwd()+"/regression_weights/"
  fileXML="TMVARegression_"
  fileXML+=method+".weights.xml"
  if not os.path.exists(dir+fileXML): return
  self.var_names=ProcessXML(self._method,dir+fileXML)
  self.reader = ROOT.TMVA.Reader(  )
  self.vars={}
  for var in self.var_names:  
   self.vars[var]=array.array('f',[0])
   self.order.append(var)
  for var in self.var_names:   self.reader.AddVariable(var, self.vars[var])
  self.reader.BookMVA(self._method+" method",  dir+fileXML );


 def __call__(self,*args):
 
  k=0
  for arg in args:
   var=self.order[k]
   self.vars[var][0]=arg
   k+=1

  return  self.reader.EvaluateRegression(self._method+" method")[0]
 

class Regression_MVA_Functor_V2():
 """ to represent MVA regressor """

 # args
 """
  0 -- method name 

 """
 def __init__(self,method,name=""):

  if (name==""): self.name=method
  else : self.name=name
  self._negate_call = False 
  self._method=method
  self.order=[]
  if (method==""): self._method="BDT"
  dir=os.getcwd()+"/regression_weights/"
  fileXML="TMVARegression_"
  fileXML+=method+".weights.xml"
  if not os.path.exists(dir+fileXML): return
  self.var_names=ProcessXML(self._method,dir+fileXML)
  self.reader = ROOT.TMVA.Reader(  )
  self.vars={}
  for var in self.var_names:  
   self.vars[var]=array.array('f',[0])
   self.order.append(var)
  for var in self.var_names:   self.reader.AddVariable(var, self.vars[var])
  self.reader.BookMVA(self._method+" method",  dir+fileXML );


 def __neg__(self):
   other = copy.copy(self)
   other._negate_call = not other._negate_call
   return other


 def __call__(self,args):
 
  k=0
  for arg in args:
   var=self.order[k]
   self.vars[var][0]=arg
   k+=1

  return  -self.reader.EvaluateRegression(self._method+" method")[0] if  self._negate_call else self.reader.EvaluateRegression(self._method+" method")[0]
 
 


def Interpolate_Regression_MVA(method="",version="V1"):

 """ return interpolator based on TMVA regression
     It should be started after Prepare_Regression_Computers:

     CreateTreesForOptimization --> Prepare_Regression_Computers --> Interpolate_Regression_MVA

 """
 
 _method=method

 if (method==""): _method="BDT"

 dir=os.getcwd()+"/regression_weights/"
 fileXML="TMVARegression_"
 fileXML+=method+".weights.xml"
 if not os.path.exists(dir+fileXML): return

 var_names=ProcessXML(_method,dir+fileXML)
 reader = ROOT.TMVA.Reader(  )

 vars={}
 for var in var_names:  vars[var]=array.array('f',[0])
 for var in var_names:   reader.AddVariable(var, vars[var])
 reader.BookMVA(_method+" method",  dir+fileXML );
 """
 test={'var5': 0.3297764942091308, 'var4': 0.98695694217756258, 'var7': 0.46851848941178653, 'var6': 0.5853009627975162, 'var1': 337.76613239599948, 'var3': 0.68810721425259258, 'var2': 0.6436265339490953, 'var9': 0.25983654514784249, 'var8': 0.41959588960370375, 'var10': 0.39998202469554989} 
 
 for var in var_names: vars[var][0]=test[var]
 res=reader.EvaluateRegression(_method+" method")[0]


 print "interpolated res=",res
 print "orig res=",0.094545401116643515



 test={'var5': 0.27209119876073651, 'var4': 0.73815248927527166, 'var7': 0.10318414364610329, 'var6': 0.30027452748598638, 'var1': 527.34600804594936, 'var3': 0.36563526598085527, 'var2': 0.45861942619132223, 'var9': 0.3557260240897816, 'var8': 0.87727468102271378, 'var10': 0.12363231209729375}

 for var in var_names: vars[var][0]=test[var]
 res=reader.EvaluateRegression(_method+" method")[0]


 print "2 interpolated res=",res
 print "2 orig res=",0.08956975044080058
 """
 if version=="V1" :  return Regression_MVA_Functor(_method)
 elif version=="V2": return Regression_MVA_Functor_V2(_method) 


def CreateTreesForOptimization(mva_method="",fileout="OptimizeTrees.root"):
 """ creates the tree for regression analysis needed by optimization """


 if (len(mva_method)<=0) : return None
 results=[]
 if os.path.exists(mva_method+"_result.gz"):
  f=open(mva_method+"_result"+".gz",'rb')
  data=zlib.decompress(f.read())
  results=pickle.loads(data)
  f.close()
  
 if os.path.exists("grid/"+mva_method+"_result.gz"):
  f=open(mva_method+"_result"+".gz",'rb')
  data=zlib.decompress(f.read())
  results+=pickle.loads(data)
  f.close()

 results=sorted(results,key=lambda x: x[2] ,reverse=True)
 results=[x for x in results if not x[0] == "000000"]
 results=[x for x in results if not x[2] == 0] # additional filtering

 file=ROOT.TFile(fileout,"RECREATE")
 tree=ROOT.TTree("optimization","optimization")
 vars=PrintVariableNames(mva_method,True)
 container={}
 for var in vars:
  container.update({var:array.array('f',[0])})
  tree.Branch(var,container[var],var+"/F");

 container.update({"result":array.array('f',[0])}) 
 tree.Branch("result",container["result"],"result/F");

 for res in results:
  varmap=res[1]
  separarion=res[2]
  for i,j in varmap.items():    
   try:
    container[i][0]=j 
   except KeyError:
    pass

  container["result"][0]=separarion
  tree.Fill()

 tree.Write()
 file.Close()

 return


def GetsBKGPeaks(mva_mehtod="",id="",path_to_files="./"):
 """ tries to find peaks in Test BKG MVA output, and return cut selections

  like   val1<=cut<val2 \n  val3<=cut<val4 \n 

 """

 if (len(id)<=0): return ""
 if (len(mva_mehtod)<=0): return ""


 file2read=path_to_files+"TMVA_"+mva_mehtod+"_"+id+".root"

 print "file2read = ",file2read
 fileFound=True
 if not os.path.exists(file2read):
  fileFound=False

# check if it's in dcache scratch
  fileInDcache=Check_TMVA_outputIn_dCache(mva_mehtod,id,path_to_files)
  if (fileInDcache):
# try to obtain it 
   res=Download_TMVA_outputFrom_dCache(mva_mehtod,id,path_to_files)
# if some trouble are
   if (res==None): return ""  
   else : fileFound=True

#  print "Let's go to grid"
# check if it's in grid subfolders in dCache
  if  os.path.exists(path_to_files+"grid/"+"TMVA_"+mva_mehtod+"_"+id+".root"):
   cmd="mv `pwd`/"+path_to_files+"grid/"+"TMVA_"+mva_mehtod+"_"+id+".root  `pwd`/"  +file2read
   p=subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
   p.wait()
   fileFound=True

  if (not fileFound):
#   print "file is ", path_to_files+"grid/"
#   print mva_method,id
   fileInDcache=Check_TMVA_outputGzipped(mva_mehtod,id,path_to_files+"grid/")
   if (fileInDcache):
    res=Download_TMVA_outputGzipped(mva_mehtod,id,path_to_files+"grid/")
    if (res==None): return ""
    else:
     fileFound=True
     cmd="mv `pwd`/"+path_to_files+"grid/"+"TMVA_"+mva_mehtod+"_"+id+".root  `pwd`/"  +file2read
     p=subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
     p.wait()

# test again if file is here
 if (fileFound):
   if not os.path.exists(file2read): fileFound=False
 if (not fileFound): return ""

 file=ROOT.TFile(file2read)
 if (not file): return ""
 bkg=file.Get("Method_"+mva_mehtod+"/"+mva_mehtod+"_"+id+"/MVA_"+mva_mehtod+"_"+id+"_B")
 if (not bkg): return ""

 spec=ROOT.TSpectrum(500,3)
 spec.SetResolution(100)
 nfound = spec.Search(bkg,1e-5,"goff nobackground new",0.1)
 xpos=spec.GetPositionX()
 nbins=bkg.GetNbinsX()
 nbinspeak=nbins/nfound/10 # 10 % of all bins per peak
 peaksbin=[]
 for i in range(nfound): 
  peaksbin.append(bkg.GetXaxis().FindBin(xpos[i]))
 # try to find min distance
 peaksbin2,size=sorted(peaksbin),len(peaksbin)
 res = [peaksbin2[i + 1] - peaksbin2[i] for i in range(size) if i+1 < size]
 mindiff=min(res)
 if (nbinspeak>mindiff/2) : nbinspeak=mindiff/2
 str=""
 for i in range(nfound):
#  print i
#  print "nbinspeak=",nbinspeak
#  print "bin center  ",bkg.GetBinCenter(peaksbin[i])
#  print "bin center - ",bkg.GetBinCenter(peaksbin[i]-nbinspeak)
#  print "bin center + ",bkg.GetBinCenter(peaksbin[i]+nbinspeak)
#  print "bin width/2 ",bkg.GetBinWidth(peaksbin[i])/2
  
#  str+="%f<=cut<=%f\n"%(bkg.GetBinCenter(peaksbin[i]-nbinspeak) - bkg.GetBinWidth(peaksbin[i])/2., 
#   bkg.GetBinCenter(peaksbin[i]+nbinspeak) + bkg.GetBinWidth(peaksbin[i])/2.)
  str+="%f<cut && cut<%f\n"%(bkg.GetBinCenter(peaksbin[i]-nbinspeak),    bkg.GetBinCenter(peaksbin[i]+nbinspeak) )

 return str[:-1]

def TestMVAGUI(mva_mehtod="",id="",outputdir="static",type=-1,onlyfilenames=False,path_to_files="./"):
 """ Create plots with performance of MVA 

	possible types of the plots:

		0: input variables
		1: correlations 
		2: Plots the output of each classifier for the test data
		3: Plots the output of each classifier for the test (histograms) and training (dots) data
		4: Plots the probability of each classifier for the test data 
		5: Plots the Rarity of each classifier for the test data
		6:  Plots B/S 'before cut' efficiencies
		7: Plots B/S, purity vs efficiency for 'before cut' case
        98: Distribution of MVA discriminator for test of overtraining
		99: Distribution of MVA separation
 """

 
 

 if (len(id)<=0): return
 if (len(mva_mehtod)<=0): return
 if (type<0): return

 if (type==99):
  if (not onlyfilenames):
   th1=GetDistributionOfResult(mva_mehtod)
   canv=ROOT.TCanvas("MVA Separation","MVA Separation",1000,800)
   th1.Draw()
   canv.Print(outputdir+"/separation"+"_"+mva_mehtod+"_"+id+".png","png")
   canv.Close()
  # [file mask, title]
  return [outputdir+"/separation"+"_"+mva_mehtod+"_"+id+".png","separation"]



 file2read=path_to_files+"TMVA_"+mva_mehtod+"_"+id+".root"

 fileFound=True
 if not os.path.exists(file2read) and  (not onlyfilenames):
  fileFound=False

# check if it's in dcache scratch
  fileInDcache=Check_TMVA_outputIn_dCache(mva_mehtod,id,path_to_files)
  if (fileInDcache):
# try to obtain it 
   res=Download_TMVA_outputFrom_dCache(mva_mehtod,id,path_to_files)
# if some trouble are
   if (res==None): return  [outputdir+"/cant_download_the_file.png",file2read+" can't be downloaded"]
   else : fileFound=True

#  print "Let's go to grid"
# check if it's in grid subfolders in dCache
  if  os.path.exists(path_to_files+"grid/"+"TMVA_"+mva_mehtod+"_"+id+".root"):
   cmd="mv `pwd`/"+path_to_files+"grid/"+"TMVA_"+mva_mehtod+"_"+id+".root  `pwd`/"  +file2read
   p=subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
   p.wait()
   fileFound=True


  if (not fileFound):
#   print "file is ", path_to_files+"grid/"
#   print mva_method,id   
   fileInDcache=Check_TMVA_outputGzipped(mva_mehtod,id,path_to_files+"grid/")
   if (fileInDcache):
    res=Download_TMVA_XML_outputGzipped(mva_mehtod,id,path_to_files+"grid/")
#    print "res=",res
    if (res==None): return  [outputdir+"/cant_download_the_file.png",file2read+" can't be downloaded"]
    else:
     fileFound=True
     cmd="mv `pwd`/"+path_to_files+"grid/"+"TMVA_"+mva_mehtod+"_"+id+".root  `pwd`/"  +file2read
#     print "cmd=",cmd
     p=subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
     p.wait()
     cmd="mv `pwd`/"+path_to_files+"grid/weights/TMVAClassification_"+mva_mehtod+"_"+id+"*  `pwd`/"+path_to_files+"weights; rm -r `pwd`/" + path_to_files+"grid/weights"
#     print "cmd=",cmd
     p=subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
     p.wait()
     

# test again if file is here
 if (fileFound):
   if not os.path.exists(file2read): fileFound=False   
 if (not fileFound): return [outputdir+"/cant_download_the_file.png",file2read+" can't be downloaded"]

 if (type==98):
  if (not onlyfilenames):
   print "mva_mehtod is ", mva_mehtod
   print "tree_name is ", tree_name
   print "id is ", id
   th1,th2,canv1=TestMVAOutPut(mva_mehtod+"_"+id,tree_name,True,1000000,True)

   PrintPlot([th1,th2],[],True,False,False,["kBlue","kRed"],["MVA Signal","MVA Background"],outputdir+"/overtrain_test"+"_"+mva_mehtod+"_"+id)
  return [outputdir+"/overtrain_test"+"_"+mva_mehtod+"_"+id+".png","Overtraining test"] 


 funs=ROOT.gROOT.GetListOfGlobalFunctions()
#void TMVAGuiForPython( const char* fName = "TMVA.root" , const char * outputdir="plots", int type=-1 ) ///usage:
 isOk=None
 if (not onlyfilenames):
  isOk=funs.FindObject("TMVAGuiForPython") # this function is used in TMVAGuiForPython.C. We need to have only one copy in the memory 
  if (isOk==None): ROOT.gROOT.ProcessLine('.L TMVAGuiForPython.C')
  ROOT.TMVAGuiForPython(file2read,outputdir,type)

 if (type==0):
  os.system("cd " + outputdir+";" + "ls "+ "variables_id_*png" + " | xargs -I {} mv {} " +  id + "_{} ;" + "cd - ;")
# [file mask, title]
  return [outputdir+"/"+id+"_variables_id_*png","variables"]

 if (type==1):
  os.system("cd " + outputdir+";" + "ls "+ "CorrelationMatrix*png" + " | xargs -I {} mv {} " +  id + "_{} ;" + "cd - ;")
# [file mask, title]
  return [outputdir+"/"+id+"_CorrelationMatrix*png","Correlations"]


 if (type==2):
# [file mask, title]
  return [outputdir+"/" + "mva_" +mva_mehtod+"_"+id +  "*png","Test MVA output"]

 if (type==3):
# [file mask, title]
  return [outputdir+"/" + "overtrain_" +mva_mehtod+"_"+id +  "*png","Overtraining for  MVA output"]

 if (type==6):
# [file mask, title]
  return [outputdir+"/" + "mvaeffs_" +mva_mehtod+"_"+id +  "*png","Efficiencies,  B/S vs MVA discriminator"]

 if (type==7):
# [file mask, title] mvaeffsPur_
  return [outputdir+"/" + "mvaeffsPur_" +mva_mehtod+"_"+id +  "*png","Purity, B/S vs efficiency "]









def ProcessMVA(doOptimize=False,myvars={}):
 """ example of the whole chain for MVA training 

  added on 30.05.2013:

    the new feature : optimization support

 """
 ###Settings begin

# trees_path="/data/user/marfin/CMSSW_5_3_3/src/Analysis/HbbMSSMAnalysis/test/Analysis2012/trees_for_training"
# tanb=20.

# democtratic_mix=True
# mass_for_mix=140.
 democtratic_xsect=GetXSection(tanb,mass_for_mix)

# mva_method="BDT"

 ###Settings end

 # signal processing # now support updated files, which can be downloaded from dcache
 signal_files=[]
 files=[ GetListFiles(trees_path+"/*"+m+scenario_template,trees_path) for m in mass ]
 if os.path.exists(files[0][0].replace(".root","_update.root") ): 
  files=[ GetListFiles(trees_path+"/*"+m+scenario_template.replace(".root","_update.root"),trees_path) for m in mass ]
  for item in files: signal_files+=item
 else:
  for item in files:
 # print item
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
 files=[ GetListFiles(trees_path+"/*"+ptbin+scenario_template,trees_path) for ptbin in ptbins ]
 if os.path.exists(files[0][0].replace(".root","_update.root") ): 
  files=[ GetListFiles(trees_path+"/*"+ptbin+scenario_template.replace(".root","_update.root"),trees_path) for ptbin in ptbins ]
  for item in files: bkg_files+=item

 else:
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


# print "CONFIGSSSSS!!!"
# print ReadConfigs(mva_method)

 

 #create config
 (config,_vars)=CreateConfig(mva_method,doOptimize,myvars)

 print "CONFIG"
 print config
 print _vars

 #run mva
 RunMVAFromConfig(signal_files,bkg_files,mva_method,config)

 #save config to db
 UpLoadConfig(mva_method,config) 
 print "CONFIGSSSSS 22222!!!"
# print ReadConfigs(mva_method)


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
 return _separation


def GetDistributionOfResult(mva_method=""):
 """ return a distribution of mva_method """

 if (len(mva_method)<=0) : return None
 f=open(mva_method+"_result"+".gz",'rb')
 data=zlib.decompress(f.read())
 results=pickle.loads(data)
 results=sorted(results,key=lambda x: x[2],reverse=True)
 results=[x for x in results if not x[0] == "000000"]

 maxSeparation=results[0][2]
 minSeparation=results[-1][2]
# print maxSeparation
# print minSeparation

#  mva_Test_S=ROOT.TH1F("mva_Test_S","mva_Test_S",50,-0.1,0.1)
 nBins=50
 binSize = (maxSeparation - minSeparation)/nBins
 maxSeparation+=0.5*binSize
 minSeparation-= 0.5*binSize
 mva_Separation=ROOT.TH1F("mva_Separation","mva_Separation",nBins+1,minSeparation, maxSeparation)
 mva_Separation.Sumw2()
 for i in results:
  mva_Separation.Fill(i[2])

 canv1=ROOT.TCanvas("mva_separation_%d"%random.uniform(1,1000),"mva_separation")
 mva_Separation.Draw()


 ROOT.SetOwnership(canv1,False)
 ROOT.SetOwnership(mva_Separation,False) 
 return mva_Separation


def GetResults(mva_method="", ID=""):
 """ return result for some ID """


 if (len(mva_method)<=0 or ID=="") : return None
 results=[]
 if (os.path.exists(mva_method+"_result"+".gz")):
  f=open(mva_method+"_result"+".gz",'rb')
  data=zlib.decompress(f.read())
  results=pickle.loads(data)

 if (os.path.exists("grid/"+mva_method+"_result"+".gz" )):
  f2=open("grid/"+mva_method+"_result"+".gz",'rb')
  data2=zlib.decompress(f2.read())
  results2=pickle.loads(data2)
  results+=results2

 
 return filter(lambda x: ID in x[0],results)[0]


def FindOptimalResult(mva_method="",pos=0):
 """ return optimal parameter point """

 if (len(mva_method)<=0) : return None
 results=[]
 if (os.path.exists(mva_method+"_result"+".gz")):
  f=open(mva_method+"_result"+".gz",'rb')
  data=zlib.decompress(f.read())
  results=pickle.loads(data)

# if (os.path.exists("grid/"+mva_method+"_result"+".gz" )):
#  f2=open("grid/"+mva_method+"_result"+".gz",'rb')
#  data2=zlib.decompress(f2.read())
#  results2=pickle.loads(data2)
#  results+=results2


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
 """ return KS of test/train outputs for signal and background MVA  """
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
 """ return separation of the current 'test' MVA """

 if (len(mva_method)<=0): return 0
 if (not isinstance(config,tuple)  ) : return 0
 if ( list(config).count(None)>0) : return 0

 f=ROOT.TFile("TMVA_"+mva_method+"_"+config[0]+".root")
 if (not f): return

 prefix="Method_"+mva_method+"/"

 method=mva_method+"_"+config[0]
 sgn=f.Get(prefix+method+"/"+"MVA_"+method+"_S")
 bkg=f.Get(prefix+method+"/"+"MVA_"+method+"_B")


 if (not (sgn and bkg)) : return 0
 tools=ROOT.TMVA.Tools.Instance()

 return tools.GetSeparation(sgn,bkg)


def GetSummarySeparationMVA(mva_method,what="train"):
 """ return [(id,Separation)] list for train/test (what==test) entries used for the method
    the summary can be used for test of overtraining """

 if (len(mva_method)<=0): return []
 results=[]
 bestvars=[] 
 if os.path.exists(mva_method+"_result"+".gz"):
  results=ReadResults(mva_method)
 if os.path.exists(mva_method+"_bestvariables"+".gz"):
  bestvars=ReadBestVariables(mva_method)

 output=[]
 if (what=="train"):
  for config in results:    output.append([config[0],GetSeparationMVATrain(mva_method,config)])
  for config in bestvars:   output.append([config[0],GetSeparationMVATrain(mva_method,config)])
 if (what=="test"):
  for config in results:    output.append([config[0],GetSeparationMVA(mva_method,config)])
  for config in bestvars:   output.append([config[0],GetSeparationMVA(mva_method,config)])
 output=sorted(output,key=lambda x: x[1], reverse=True)

 return output

def GetSeparationMVATrain( mva_method="",config=()):
 """ return separation of the current 'train' MVA """

 if (len(mva_method)<=0): return 0
 if (not isinstance(config,tuple) ) : return 0
 if ( list(config).count(None)>0) : return 0

 f=ROOT.TFile("TMVA_"+mva_method+"_"+config[0]+".root")
 if (not f): return 0

 prefix="Method_"+mva_method+"/"

 method=mva_method+"_"+config[0]
 sgn=f.Get(prefix+method+"/"+"MVA_"+method+"_Train"+"_S")
 bkg=f.Get(prefix+method+"/"+"MVA_"+method+"_Train"+"_B")


 if (not (sgn and bkg)) : return 0
 tools=ROOT.TMVA.Tools.Instance()

 return tools.GetSeparation(sgn,bkg)



  

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

#  print "sig_variables ",sig_variables[i]   
  min_i=min(chain_sig.GetMinimum(sig_variables[i]), chain_bkg.GetMinimum(bkg_variables[i]))  
  max_i=max(chain_sig.GetMaximum(sig_variables[i]), chain_bkg.GetMaximum(bkg_variables[i]))  

#  proof=start_proof("8")
#  chain_sig.SetProof(True,True)

  _tmph1=ROOT.TH1D(sig_variables[i]+"_s",sig_variables[i]+"_s",50,min_i,max_i)
  chain_sig.Draw(sig_variables[i]+">>"+sig_variables[i]+"_s","weight*("+sig_variables[i]+">-1e9)")
#  print "_tmph1 =",_tmph1.Integral()
  sig_vars.append(_tmph1)
#  proof.ClearInput()
#  proof.ClearCache()
#  proof.ClearInputData()
#  proof.ClearDataSetCache()
##   proof.Close()
#  ROOT.TProof.Reset("",1)

  for j in range(i+1,len(sig_variables)):
   print "var=",sig_variables[j]
   min_j=min(chain_sig.GetMinimum(sig_variables[j]), chain_bkg.GetMinimum(bkg_variables[j]))  
   max_j=max(chain_sig.GetMaximum(sig_variables[j]), chain_bkg.GetMaximum(bkg_variables[j]))  

#   proof=start_proof("8")
#   chain_sig.SetProof(True,True)

#   _tmph2=ROOT.TH2D("_tmph2"+sig_variables[i]+sig_variables[j]+"_s","_tmph2"+sig_variables[i]+sig_variables[j]+"_s",50,min_i, max_i, 50,min_j,max_j)
#   print "_tmph2",_tmph2

#   chain_sig.Draw(sig_variables[i]+":"+ sig_variables[j]+">>_tmph2"+sig_variables[i]+sig_variables[j]+"_s","weight*("+sig_variables[i]+">-1e9 && " + sig_variables[j] +  ">-1e9)")
   chain_sig.Draw(sig_variables[i]+":"+ sig_variables[j]+">>"+sig_variables[i]+sig_variables[j]+"_s","weight*("+sig_variables[i]+">-1e9 && " + sig_variables[j] +  ">-1e9)")
#   print "corr=", ROOT.__getattr__(sig_variables[i]+sig_variables[j]+"_s").GetCorrelationFactor()
#   print "int=", ROOT.__getattr__(sig_variables[i]+sig_variables[j]+"_s").Integral()
#   correlation_sig.append([sig_variables[i],sig_variables[j],_tmph2.GetCorrelationFactor()])
   correlation_sig.append([sig_variables[i],sig_variables[j],ROOT.__getattr__(sig_variables[i]+sig_variables[j]+"_s").GetCorrelationFactor()])
#   proof.ClearInput()
#   proof.ClearCache()
#   proof.ClearInputData()
#   proof.ClearDataSetCache()
##   proof.Close()
#   ROOT.TProof.Reset("",1)



# bkg processing


# print bkg_variables


# proof=start_proof("8")
# chain_bkg.SetProof(True,True)

 for i in range(len(bkg_variables)):
  min_i=min(chain_sig.GetMinimum(sig_variables[i]), chain_bkg.GetMinimum(bkg_variables[i]))
  max_i=max(chain_sig.GetMaximum(sig_variables[i]), chain_bkg.GetMaximum(bkg_variables[i]))

#  print "bkg_variables ",bkg_variables[i]   

  _tmph1=ROOT.TH1D(bkg_variables[i]+"_b",bkg_variables[i]+"_b",50,min_i,max_i)
  chain_bkg.Draw(bkg_variables[i]+">>"+bkg_variables[i]+"_b","weight*("+bkg_variables[i]+">-1e9)")
  
  bkg_vars.append(_tmph1)
  for j in range(i+1,len(bkg_variables)):

   min_j=min(chain_sig.GetMinimum(sig_variables[j]), chain_bkg.GetMinimum(bkg_variables[j]))
   max_j=max(chain_sig.GetMaximum(sig_variables[j]), chain_bkg.GetMaximum(bkg_variables[j]))

   _tmph2=ROOT.TH2D("_tmph2"+sig_variables[i]+sig_variables[j]+"_b","_tmph2",50,min_i, max_i, 50,min_j,max_j)
   chain_bkg.Draw(sig_variables[i]+":"+ sig_variables[j]+">>_tmph2"+sig_variables[i]+sig_variables[j]+"_b","weight*("+sig_variables[i]+">-1e9 && " + sig_variables[j] +  ">-1e9)")
   print "bkg correlation ",bkg_variables[i]," ",bkg_variables[j]," ",_tmph2.GetCorrelationFactor()," ",_tmph2.Integral()
   correlation_bkg.append([bkg_variables[i],bkg_variables[j],_tmph2.GetCorrelationFactor()])


 #proof.ClearInput()
 #proof.ClearCache()
 #proof.ClearInputData()
 #proof.ClearDataSetCache()
##   proof.Close()
 #ROOT.TProof.Reset("",1)
  
 #print correlation_bkg

 assert(len(bkg_vars) == len(sig_vars))

 KS=[]

# print "KS test==> name : distance : probabilty: Nsig : Nbkg : CL"
 for i in range(len(sig_vars)):
  dist=sig_vars[i].KolmogorovTest(bkg_vars[i],"M N")
  sig_int=sig_vars[i].Integral()
  bkg_int=bkg_vars[i].Integral()

#  print bkg_variables[i], ":", dist,":",ROOT.TMath.KolmogorovProb(dist),":", sig_int,":",bkg_int,":",ROOT.TMath.KolmogorovProb(dist*math.sqrt((sig_int+bkg_int)/(sig_int*bkg_int)))
  KS.append([bkg_variables[i],dist])  


 if (not os.path.isfile("./"+tree_name+"_variable.gz")): 
  f=open(tree_name+"_variable"+".gz","wb")
  f.write(zlib.compress(pickle.dumps((correlation_sig,correlation_bkg,KS), pickle.HIGHEST_PROTOCOL),9))
  f.close()


 return (correlation_sig,correlation_bkg,KS,sig_variables)


def Ranking(correlation_sig=[],correlation_bkg=[],KS=[],order="Correlation",varstable=[],doSelection=False,doInversion=False):

 """ do ranking variables """
 if (len(KS)*len(correlation_sig)*len(correlation_bkg)<=0): return

# totalCorr_sig=[0 for i in KS]
# totalCorr_bkg=[0 for i in KS]
 totalCorr_sig={}
 totalCorr_bkg={}

 vars=[i[0] for i in KS]

 # create table of correlation
# sys.path.append( os.getcwd()+"/texttable-0.8.1" )
 #import texttable

 sys.path.append( os.getcwd()+"/HTML.py-0.04" )
 import HTML

 #table_s = texttable.Texttable()
 #table_b = texttable.Texttable()

 header=["   "]
 if (len(varstable)==0):
  header+=vars
 else:
  for var in vars:
   if (var in varstable):
    header.append(var)

 rows_s=[header]
 rows_b=[header]

 #tbl_align=["c"]
 #tbl_valign=["m"]
 #tbl_dtype=['t']

 for var in vars:
 # fill table
 # tbl_align.append("c")
 # tbl_valign.append("m")
 # tbl_dtype.append("f")
  doTable=False
#  print len(varstable)
  if (len(varstable)==0): doTable=True
#  print doTable
  if (doTable or  var in varstable):
#   print var
   row_s=[]
   row_s.append(var)
   row_b=[]
   row_b.append(var)
   for  jj in range(1,len(header)):
    var2=header[jj]
    if var == var2:
     row_s.append("%6.2f"%1.00)
     row_b.append("%6.2f"%1.00)
    else:
     ss=filter(lambda x: (x[0]==var and x[1]==var2 ) or (x[0]==var2 and x[1]==var)  ,correlation_sig)
     row_s.append("%6.2f"%ss[0][2])
     bb=filter(lambda x: (x[0]==var and x[1]==var2 ) or (x[0]==var2 and x[1]==var)  ,correlation_bkg)
     row_b.append("%6.2f"%bb[0][2])

   rows_s.append(row_s)
   rows_b.append(row_b)


  corr_sigs=filter(lambda x: x[0]==var or x[1]==var, correlation_sig)
#  corr_sig=sum(map(lambda x: abs(x[2]),corr_sigs))
#  totalCorr_sig[var]=corr_sig
  corr_sig=sum(map(lambda x: math.pow(abs(x[2]),2),corr_sigs))
  totalCorr_sig[var]=math.sqrt(corr_sig)
 
  
  corr_bkgs=filter(lambda x: x[0]==var or x[1]==var, correlation_bkg)
#  corr_bkg=sum(map(lambda x: abs(x[2]),corr_bkgs))
#  totalCorr_bkg[var]=corr_bkg
  corr_bkg=sum(map(lambda x: math.pow(abs(x[2]),2),corr_bkgs))
  totalCorr_bkg[var]=math.sqrt(corr_bkg)


# print rows_s
# print tbl_align
# print tbl_valign
# print tbl_dtype
 htmlcode_s = HTML.table(rows_s)
 htmlcode_b = HTML.table(rows_b)

# table_s.set_cols_align(tbl_align)
# table_s.set_cols_valign(tbl_valign)
# table_s.set_cols_dtype(tbl_dtype)
# table_s.add_rows(rows_s)

# table_b.set_cols_align(tbl_align)
## table_b.set_cols_valign(tbl_valign)
# table_b.set_cols_dtype(tbl_dtype)
# table_b.add_rows(rows_b)

# do sorting of correlation

# print totalCorr_sig

 totalCorr_sig=sorted([(value,key) for (key,value) in totalCorr_sig.items()])

# print totalCorr_sig

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
#     print "i=",i
#     print "j=",j
#     print "KS_high[j][0]=",KS_high[j][0]
#     print "KS_high[i][0]=",KS_high[i][0]
#     print "corr4=",KS_corr[0][2]
     KS_delete.append(KS_high[j])

#  print KS_output
#  print KS_delete
  KS_output=[s for s in KS_output if not s in KS_delete ]
  for  k in KS_output:
   print k[0]," : ",k[1]
 
  
  print "\n\nlist of excluded variables:\n\n"
  KS_inversed=[]
  for  k in KS:
   if not k in KS_output: 
    print "exclude_list.append(\"%s\\n\")"%k[0]
    KS_inversed.append(k)
  if (doSelection and not doInversion): return KS_output
  if (doSelection and doInversion): return KS_inversed

 if (order=="Table"):
  print "\n\nSignal(correlation table)\n\n " 
#  print table_s.draw()
  correl_s=open("correlation_S.html",'w')
  print >>correl_s,  htmlcode_s

  print " "
  print "\n\n Background(correlation table)\n\n "
#  print table_b.draw()
  correl_b=open("correlation_B.html",'w')
  print >>correl_b,  htmlcode_b

  if (doSelection): return None
 
 if (order=="Correlation"):
  print "\n\nSignal(total correlations)\n\n "
  for x in totalCorr_sig:
   print x[0]," : ",x[1]

#  for  k,v in totalCorr_sig.items():
#   print k," : ",v

  print "\n\nBackground (total correlations)\n\n "
  for x in totalCorr_bkg:
   print x[0]," : ",x[1]

  if (doSelection and not doInversion): return totalCorr_sig

#  for  k,v in totalCorr_bkg.items():
#   print k," : ",v

 if (order=="KS"):
  print "\n\nKS order\n\n"
  for  k in KS:
   print k[0]," : ",k[1]

  if (doSelection): return  KS

 return None
 



def RunMVAFromConfig(signal_files=[],bkg_files=[], mva_method="",config=()):
 """ start mva on config and """


 if (len(mva_method)*len(config)*len(signal_files)*len(bkg_files)<=0): return
 if (not isinstance(config,tuple) ) : return

 if ( list(config).count(None)>0) : return

# it helps to solve the overtraining?
 random.shuffle(signal_files)
 random.shuffle(bkg_files)

 (_id,_exclude_lst,_book_lst,_train_lst)=config


# tree_name="KinVarsBDT"
 exclude_list=_id+"_tmp_exclude.lst" 
 option_book_list=_id+"_tmp_options_book.lst"
 option_train_list=_id+"_tmp_option_train.lst"
 input_list=_id+"_list_of_files"



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

 # here to remove "_tmp" files
 os.remove(input_list)
 os.remove(exclude_list)
 os.remove(option_book_list)
 os.remove(option_train_list) 
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
 stat=file.cd("InputVariables_Id/CorrelationPlots")
 print "stat=",stat
 if (stat):
  objs=ROOT.gDirectory.GetListOfKeys()
  for obj in objs:
 #  print obj.GetName()
   ROOT.gDirectory.Delete(obj.GetName()+";*")
  file.cd(currdir)

 stat=file.cd("InputVariables_Gauss_Deco/CorrelationPlots")
 print "stat=",stat
 if (stat):
  objs=ROOT.gDirectory.GetListOfKeys()
  for obj in objs:
 #  print obj.GetName()
   ROOT.gDirectory.Delete(obj.GetName()+";*")
  file.cd(currdir)

 stat=file.cd("InputVariables_PCA/CorrelationPlots")
 print "stat=",stat
 if (stat):
  objs=ROOT.gDirectory.GetListOfKeys()
  for obj in objs:
 #  print obj.GetName()
   ROOT.gDirectory.Delete(obj.GetName()+";*")
  file.cd(currdir)

 stat=file.cd("InputVariables_Deco/CorrelationPlots")
 print "stat=",stat
 if (stat):
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

 stat=file.cd("Method_"+mva_method+"/"+mva_method+"_"+config[0]+"/CorrelationPlots")
 print "stat=",stat
 if (stat):
  objs=ROOT.gDirectory.GetListOfKeys()
  for obj in objs:
#   print obj.GetName()
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

def test():
 """ perform tests"""


# trees_path="/data/user/marfin/CMSSW_5_3_3/src/Analysis/HbbMSSMAnalysis/test/Analysis2012/trees_for_training"
# tanb=20.

# democtratic_mix=True
# mass_for_mix=140.
 democtratic_xsect=GetXSection(tanb,mass_for_mix)

 # signal processing
 signal_files=[]
# mass=["M-100","M-140","M-300"]
# files=[ GetListFiles(trees_path+"/*"+m+"*/*/*/TripleBtagAnalysis.root",trees_path) for m in mass ]
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
# ptbins=["15To30","30To50","50To150","-150_"]
# files=[ GetListFiles(trees_path+"/*"+ptbin+"*/*/*/TripleBtagAnalysis.root",trees_path) for ptbin in ptbins ]
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

 #run mva
 RunMVATraining(signal_files,bkg_files)
 ROOT.gROOT.ProcessLine('.L TMVAGui.C')
 ROOT.TMVAGu()
 return

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
 """ return a weight list for reweighting 
     lumi - what was  used during production!
 """

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
 i=0
 what_to_delete=[]
 for file in file_names:
  if (not doNumEvt):
   result.append(-1)
   continue
  i+=1
#  print "file=",file
  RootFile=ROOT.TFile(file)
  count=RootFile.Get("countSample/count")
#  print count
  if (count==None):
   what_to_delete.append(i-1)
   continue
  result.append(count.GetBinContent(1))
#  print result[-1]

 print "GetNumEvt:: result=",result
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
 treeroot=os.getcwd()
 if (len(path)!=0): treeroot=path
  
 results = []
 for base, dirs, files in os.walk(treeroot):
    files=map(lambda x: base+"/"+x,files)
    goodfiles = fnmatch.filter(files, pattern)
    results.extend(os.path.join(base, f) for f in goodfiles)

 return list(set(results))


def ReWeight(tree_name="KinVarsBDT",list_of_files=[],weight=[],suffix="_update"):
 """ performs reweighting of the tree"""

 if (len(tree_name) == 0) : return False
 if (len(list_of_files)==0) : return False
 if (len(weight)==0) : return False
 assert (len(list_of_files)==len(weight))

 i=0 
 for file in list_of_files:
  filenew=file.replace(".root",suffix +".root")
  if (not doReweight): 
   os.system("cp "+file+" "+filenew)
   continue

#  RootFile=ROOT.TFile(file,"UPDATE")
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

 if options.vars:  OptimizeVariablesTraining() 
 if options.optimiationMVA: OptimizeMVA()
 if options.download_mva_dcache: Download_MVA_Trees_From_DCACHE()
 if options.prepare_samples: Prepare_samples()

 if options.optimizer: ProcessOptimizer()

 if options.run:
  ProcessMVA()  
 elif not options.vars and not options.optimiationMVA and not options.download_mva_dcache and not options.prepare_samples and  not options.optimizer:
  print """
	
	Help:  

 Here a few examples how to use the package:
 
import prepare_mva
trees_path="/data/user/marfin/CMSSW_5_3_3/src/Analysis/HbbMSSMAnalysis/test/Analysis2012/trees_for_training"
ptbin="30To50"
files=prepare_mva.GetListFiles(trees_path+"/*"+ptbin+"*/*/*/TripleBtagAnalysis.root",trees_path)
(files,numevts)=prepare_mva.GetNumEvt(files)
(files,lumiwgts)=prepare_mva.GetLumiWeight(files)
newwgts=prepare_mva.GetNewWeight(1e3,lumiwgts,numevts)
print "test :"
total=sum(j for j in newwgts)
print total
prepare_mva.ReWeight(tree_name='KinVarsBDT', list_of_files=files, weight=newwgts)
print "test :"
filesnew=map(lambda x: files[x].replace(".root","_update.root") ,range(len(files)))
import ROOT
for i in range(len(files)):
 f=ROOT.TFile(files[i])
 fnew=ROOT.TFile(filesnew[i])
 tree=f.Get("KinVarsBDT")
 treenew=fnew.Get("KinVarsBDT")
 print "Scan first 9 entries"
 print f.GetName()
 tree.Scan("weight","","",9,0)
 print fnew.GetName()
 treenew.Scan("weight","","",9,0)

print "end "
print "test of signal samples"
import prepare_mva
trees_path="/data/user/marfin/CMSSW_5_3_3/src/Analysis/HbbMSSMAnalysis/test/Analysis2012/trees_for_training"
mass="M-140"
tanb=20.
files=prepare_mva.GetListFiles(trees_path+"/*"+mass+"*/*/*/TripleBtagAnalysis.root",trees_path)
(files,masses)=prepare_mva.GetMassFromName(files)
xsects=map(lambda x:  prepare_mva.GetXSection(tanb,float(x)),masses)

print "test of signal sample for few mass ponts"
import prepare_mva
trees_path="/data/user/marfin/CMSSW_5_3_3/src/Analysis/HbbMSSMAnalysis/test/Analysis2012/trees_for_training"
mass=["M-140","M-300"]
tanb=20.
import itertools
files=[ prepare_mva.GetListFiles(trees_path+"/*"+m+"*/*/*/TripleBtagAnalysis.root",trees_path) for m in mass ]
files=list(itertools.chain(*files))
(files,masses)=prepare_mva.GetMassFromName(files)
xsects=map(lambda x:  prepare_mva.GetXSection(tanb,float(x)),masses)


print "test reweighting"
import prepare_mva
trees_path="/data/user/marfin/CMSSW_5_3_3/src/Analysis/HbbMSSMAnalysis/test/Analysis2012/trees_for_training"
mass="M-140"
tanb=20.
files=prepare_mva.GetListFiles(trees_path+"/*"+mass+"*/*/*/TripleBtagAnalysis.root",trees_path)
(files,masses)=prepare_mva.GetMassFromName(files)
(files,numevts)=prepare_mva.GetNumEvt(files)
(files,lumiwgts)=prepare_mva.GetLumiWeight(files)
xsects=map(lambda x:  prepare_mva.GetXSection(tanb,float(x)),masses)

newwgts=prepare_mva.GetNewWeight(1e3,lumiwgts,numevts,xsects)
print "test :"
total=sum(j for j in newwgts)
print total
prepare_mva.ReWeight(tree_name='KinVarsBDT', list_of_files=files, weight=newwgts)
print "test :"
filesnew=map(lambda x: files[x].replace(".root","_update.root") ,range(len(files)))
import ROOT
for i in range(len(files)):
 f=ROOT.TFile(files[i])
 fnew=ROOT.TFile(filesnew[i])
 tree=f.Get("KinVarsBDT")
 treenew=fnew.Get("KinVarsBDT")
 print "Scan first 9 entries"
 print f.GetName()
 tree.Scan("weight","","",9,0)
 print fnew.GetName()
 treenew.Scan("weight","","",9,0)

print "test reweighting of few mass points"
import prepare_mva
trees_path="/data/user/marfin/CMSSW_5_3_3/src/Analysis/HbbMSSMAnalysis/test/Analysis2012/trees_for_training"
mass=["M-140","M-300"]
tanb=20.
files=[ prepare_mva.GetListFiles(trees_path+"/*"+m+"*/*/*/TripleBtagAnalysis.root",trees_path) for m in mass ]
for item in files:
 (item,masses)=prepare_mva.GetMassFromName(item)
 (item,numevts)=prepare_mva.GetNumEvt(item)
 (item,lumiwgts)=prepare_mva.GetLumiWeight(item)
 xsects=map(lambda x:  prepare_mva.GetXSection(tanb,float(x)),masses) 
 print "numevts=",numevts
 print "lumiwgt=",lumiwgts
 print "XS=", xsects
 newwgts=prepare_mva.GetNewWeight(1e3,lumiwgts,numevts,xsects)
 print "new weights=",newwgts
 print "test :"
 total=sum(j for j in newwgts)
 print total
 prepare_mva.ReWeight(tree_name='KinVarsBDT', list_of_files=item, weight=newwgts)
 filesnew=map(lambda x: item[x].replace(".root","_update.root") ,range(len(item)))
 import ROOT
 for i in range(len(item)):
  f=ROOT.TFile(item[i])
  fnew=ROOT.TFile(filesnew[i])
  tree=f.Get("KinVarsBDT")
  treenew=fnew.Get("KinVarsBDT")
  print "Scan first 9 entries"
  print f.GetName()
  tree.Scan("weight","","",9,0)
  print fnew.GetName()
  treenew.Scan("weight","","",9,0)

print "end "


 """
