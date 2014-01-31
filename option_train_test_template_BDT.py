# nEvt for testing and training
# suppose for var41 as a free slot for new variable

mode=0

if os.path.exists("variables.mode"):
 file=open("variables.mode","r")
 mode=int(file.readline())
 file.close()


if (not doOptimization):
 var41=random.uniform(1.0,1.1) # 100K as minimal number of  training events events 110K as a maximal number of training events
 var21=random.uniform(0,1)
else:
 var41=myvars.get("var41",0)
 var21=myvars.get("var21",0)



# Background is QCD common
if (mode==3 or mode==4 or mode==5):
 option_train_list.append("nTrain_Signal=%d:nTrain_Background=%d:SplitMode=Random:SplitSeed=0\n"%(var41*100000,var41*100000))
 option_train_list.append("nTest_Signal=%d:nTest_Background=%d\n"%(150000-var41*100000,150000-var41*100000)) # varies from 50K upto 100K
# option_train_list.append("nTrain_Signal=%d:nTrain_Background=%d:SplitMode=Random:SplitSeed=0\n"%(var41*100000,var41*300000))
# option_train_list.append("nTest_Signal=%d:nTest_Background=%d\n"%(150000-var41*100000,350000-var41*300000)) # varies from 50K upto 100K
 _vars["var41"]=var41
else:
 option_train_list.append("nTrain_Signal=%d:nTrain_Background=%d:SplitMode=Random:SplitSeed=0\n"%(100000,100000))
 option_train_list.append("nTest_Signal=%d:nTest_Background=%d\n"%(100000,100000)) # varies from 50K upto 100K
# option_train_list.append("nTrain_Signal=%d:nTrain_Background=%d:SplitMode=Random:SplitSeed=0\n"%(100000,300000))
# option_train_list.append("nTest_Signal=%d:nTest_Background=%d\n"%(100000,300000)) # varies from 50K upto 100K
 

#if file .normmode exists, it can contain the modes
#
#   0,3,4,5 where 0 -- for randomly chosen mode,3 -- None, 4-EqualNumEvents ,5 - NumEvents modes accordingly


normmode=0
if os.path.exists(".normmode"):
 file=open(".normmode","r")
 normmode=int(file.readline())
 file.close()

if (mode==3 or mode==4 or mode==5): normmode=mode

if (normmode==3):
 option_train_list.append("NormMode=None\n")
elif (normmode==4):
 option_train_list.append("NormMode=EqualNumEvents\n")
elif (normmode==5):
 option_train_list.append("NormMode=NumEvents\n")
else: 
 # mode of training
 if (var21<=0.33):
  option_train_list.append("NormMode=None\n")
 if (var21>0.33 and var21<=0.66):
  option_train_list.append("NormMode=EqualNumEvents\n")
 if (var21>0.66 and var21<=1.0):
  option_train_list.append("NormMode=NumEvents\n")
 _vars["var21"]=var21



