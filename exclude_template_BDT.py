mode=0

if os.path.exists("variables.mode"):
 file=open("variables.mode","r")
 mode=int(file.readline())
 file.close()






if os.path.exists(mva_method+"_bestvariables.gz") and mode==6:
 (level1,level2,level3)=prepare_mva.OptimizeVariablesRanking(mva_method,10,False,['000000','NMNone','NMEqNE','NMNumE'])
 if (len(level1)==0 and len(level2)==0 and len(level3)==0): mode=0
 else:
  rank2=random.uniform(0,1)
  rank3=random.uniform(0,1)
  for var in level1: exclude_list.append("%s\n"%var[0])
  if (rank2>0.5):
   for var in level2: exclude_list.append("%s\n"%var[0])
  if (rank3>0.75):
   for var in level3: exclude_list.append("%s\n"%var[0])
elif mode==6:  mode=0


if (mode==0 or mode==1 or mode==2 or mode==3 or mode==4 or mode==5 or mode==6):

 file=open("exclude_for_testing_properties.lst","r")
 lines=file.readlines()
 for line in lines:
  exclude_list.append(line)
 file.close()




# the mode of floating exluding list
# 0 
if (mode==0):
 _allvars=ProcessVariables("ks_1.0_corr_1.0")
 if (not doOptimization):
  _val1=int(random.uniform(0,len(_allvars)))
 else:
  _val1=myvars.get("var11",0)
  print "exlcude for optimization, var11 ", _val1


 for _val11 in range(_val1):
  _vall22=int(random.uniform(0,len(_allvars)))
  exclude_list.append("%s\n"%_allvars[_vall22])
  del _allvars[_vall22]
 _vars["var11"]=_val1

### there are  two different 'fixed' modes defined in the file "variables.mode"

# 1 --  mode when all varibles with ks_0.005_corr_0.30
if (mode==1):
 exclude_vars=ProcessVariables("ks_0.005_corr_0.30",[],True,True)
 for var in exclude_vars:
  exclude_list.append(var[0]+"\n")

# 2 --  mode when all varibles with ks_0.05_corr_1.10
if (mode==2):
 print "mode is ",mode
 exclude_vars=ProcessVariables("ks_0.05_corr_1.10",[],True,True)
 for var in exclude_vars:
  exclude_list.append(var[0]+"\n")


# 3,4,5 -- mode of all variables:
#if (mode==3 or mode==4 or mode==5):
#  exclude_vars= 

