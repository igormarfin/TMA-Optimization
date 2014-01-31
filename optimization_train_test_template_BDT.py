var21=_vars["var21"]


option_train_list.append("nTrain_Signal=100000:nTrain_Background=100000:SplitMode=Random:SplitSeed=0\n")
option_train_list.append("nTest_Signal=100000:nTest_Background=100000\n")

if (var21<=0.33):
 option_train_list.append("NormMode=None\n")
if (var21>0.33 and var21<=0.66):
 option_train_list.append("NormMode=EqualNumEvents\n")
if (var21>0.66 and var21<=1.0):
 option_train_list.append("NormMode=NumEvents\n")

_vars["var21"]=var21



