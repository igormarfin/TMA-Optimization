
#option_book_list.append("NTrees=%d\n"%random.uniform(10,1000))
#var1=random.uniform(10,300)
#var1=random.uniform(10,30)

## new production ! increase num of Trees!
#var1=random.uniform(600,3000)

# new range for var1: (10,1000) on 27.11.12
if (not doOptimization): 
 var1=random.uniform(10,1000)
 var2=random.uniform(0,1)
 var3=random.uniform(0,1)
 var4=random.uniform(0,1)
 var5=random.uniform(0,1)
 var6=random.uniform(0,1)
 var7=random.uniform(0,1)
 var8=random.uniform(0,1)
 var9=random.uniform(0,1)
 var10=random.uniform(0,1)
else:
 var1=myvars.get("var1",0)
 var2=myvars.get("var2",0)
 var3=myvars.get("var3",0)
 var4=myvars.get("var4",0)
 var5=myvars.get("var5",0)
 var6=myvars.get("var6",0)
 var7=myvars.get("var7",0)
 var8=myvars.get("var8",0)
 var9=myvars.get("var9",0)
 var10=myvars.get("var10",0)



option_book_list.append("NTrees=%d\n"%var1)

#option_book_list.append("BoostType=AdaBoost:AdaBoostBeta=%f\n"%random.uniform(0,1))
# new (27.11.12): UseRandomisedTrees was added
if (var2<=0.33):
 option_book_list.append("BoostType=AdaBoost\n")
if (var2>0.33 and var2<=0.66):
 option_book_list.append("BoostType=Bagging\n")
if (var2>0.66 and var2<=1.0):
 option_book_list.append("BoostType=AdaBoost:UseRandomisedTrees=True\n")

# (27.11.12)
option_book_list.append("UseWeightedTrees=True\n")

if var3<=0.20:
 option_book_list.append("SeparationType=GiniIndex\n")
if var3>0.20 and var3<=0.40:
 option_book_list.append("SeparationType=GiniIndexWithLaplace\n")
if var3>0.40 and var3<=0.60:
 option_book_list.append("SeparationType=CrossEntropy\n")
if var3>0.60 and var3<=0.80:
 option_book_list.append("SeparationType=SDivSqrtSPlusB\n")
if var3>0.80 and var3<=1.0:
 option_book_list.append("SeparationType=MisClassificationError\n")

if (var4<=0.20):
  option_book_list.append("NNodesMax=%d\n"%(max(3,30*var4)))
if (var4>0.20 and var4<=0.40):
  option_book_list.append("NNodesMax=%d\n"%(50*var4))
if (var4>0.40 and var4<=0.60):
  option_book_list.append("NNodesMax=%d\n"%(250*var4-50))
if (var4>0.60 and var4<=0.80):
  option_book_list.append("NNodesMax=%d\n"%(9000./2.*var4+100-4500.*0.60))
if (var4>0.80 and var4<=1.0):
  option_book_list.append("NNodesMax=%d\n"%(90000./2.*var4+1000-45000.*0.80))

if (var5<=0.20):
  option_book_list.append("MaxDepth=%d\n"%(max(3.,30.*var5)))
if (var5>0.20 and var5<=0.40):
  option_book_list.append("MaxDepth=%d\n"%(50.*var5))
if (var5>0.40 and var5<=0.60):
  option_book_list.append("MaxDepth=%d\n"%(30./0.20*var5+20-30/0.20*0.40))
if (var5>0.60 and var5<=0.80):
  option_book_list.append("MaxDepth=%d\n"%(50./0.20*var5+50-50./0.20*0.60))
if (var5>0.80 and var5<=1.0):
  option_book_list.append("MaxDepth=%d\n"%(900./0.2*var5+100-900./0.20*0.80))

option_book_list.append("Shrinkage=%f\n"%var6)

if (var7<=0.33):
 option_book_list.append("PruneMethod=NoPruning\n")
if (var7>0.33 and var7<=0.66):
 option_book_list.append("PruneMethod=ExpectedError\n")
if (var7>0.66 and var7<=1.):
 option_book_list.append("PruneMethod=CostComplexity\n")

#if (var8<=0.33 and var7>0.50):
if (var7>0.33 and var7<=0.66):
 option_book_list.append("PruneStrength=%f\n"%var8)
if (var7>0.66 and  var7<=1.):
# option_book_list.append("PruneStrength=%f\n"%var8)
#if (var8>0.66 and var8<=1.00 and var7>0.50):
 option_book_list.append("PruneStrength=%d\n"%-1)

if (var9<=0.33):
 option_book_list.append("nEventsMin=%d\n"%(20./0.33*var9+20))
if (var9>0.33 and var9<=0.66):
 option_book_list.append("nEventsMin=%d\n"%(60./0.33*var9-20))
if (var9>0.66 and var9<=1.0):
 option_book_list.append("nEventsMin=%d\n"%(20./0.33*var9+20))

# (27.11.12) nCuts

if (var10<=0.33):
 option_book_list.append("nCuts=%d\n"%(10./0.33*var10+10))
if (var10>0.33 and var10<=0.66):
 option_book_list.append("nCuts=%d\n"%(10./0.33*var10+10))
if (var10>0.66 and var10<=1.0):
 option_book_list.append("nCuts=%d\n"%-1)


_vars["var1"]=var1
_vars["var2"]=var2
_vars["var3"]=var3
_vars["var4"]=var4
_vars["var5"]=var5
_vars["var6"]=var6
_vars["var7"]=var7
_vars["var8"]=var8
_vars["var9"]=var9
_vars["var10"]=var10


