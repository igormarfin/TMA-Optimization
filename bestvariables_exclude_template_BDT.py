exclude_list.append("nEvt\n")
exclude_list.append("mva\n")
exclude_list.append("flav_cont\n")
exclude_list.append("Pt1\n")
exclude_list.append("Pt2\n")
exclude_list.append("Pt3\n")
exclude_list.append("Pt1_b\n")
exclude_list.append("Pt2_b\n")
exclude_list.append("Pt3_b\n")
exclude_list.append("Pt1_nonb\n")
exclude_list.append("Pt2_nonb\n")
exclude_list.append("Pt3_nonb\n")
exclude_list.append("Eta1_b\n")
exclude_list.append("Eta2_b\n")
exclude_list.append("Eta3_b\n")
exclude_list.append("Eta1_nonb\n")
exclude_list.append("Eta2_nonb\n")
exclude_list.append("Eta3_nonb\n")
exclude_list.append("M12\n")
exclude_list.append("Pt1_c\n")
exclude_list.append("Pt2_c\n")
exclude_list.append("Pt1_q\n")
exclude_list.append("Pt2_q\n")
exclude_list.append("Eta1_c\n")
exclude_list.append("Eta2_c\n")
exclude_list.append("Eta1_q\n")
exclude_list.append("Eta2_q\n")
exclude_list.append("Et1\n")
exclude_list.append("Et2\n")
exclude_list.append("Et3\n")
exclude_list.append("nPV\n")


_allvars=ProcessVariables("ks_1.0_corr_1.0")

#_allvars.remove("nPV")
#_allvars.remove("Et1")
#_allvars.remove("Et2")
#_allvars.remove("Et3")

#_allvars.remove("mindijetmass")
#_allvars.remove("maxdijetmass")
#exclude_list.append("mindijetmass\n")
#exclude_list.append("maxdijetmass\n")


_val1=int(random.uniform(0,len(_allvars)))
#print "_val1=",_val1

for _val11 in range(_val1):
 _vall22=int(random.uniform(0,len(_allvars)))
 print "_val22=",_vall22
 print "_allvars[_vall22]=",_allvars[_vall22]
 exclude_list.append("%s\n"%_allvars[_vall22])
 del _allvars[_vall22]

