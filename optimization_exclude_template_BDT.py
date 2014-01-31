# flavor dependent
exclude_list.append("nEvt\n")
# (27.11.12)
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


#correlated
exclude_list.append("sphericity_boost\n")
exclude_list.append("aplanarity\n")

# (27.11.12)
#exclude_list.append("mindijetmass\n")
exclude_list.append("maxdijetmass\n")
exclude_list.append("isotropy\n")
exclude_list.append("Et1\n")
exclude_list.append("Et2\n")
exclude_list.append("Et3\n")
exclude_list.append("dphijet1jet2\n")

#(29.11.12)
# new variable of PU
exclude_list.append("nPV\n")

var11=_vars["var11"]

if (var11<=0.33):
# (27.11.12)
 exclude_list.append("mindijetmass\n")

 exclude_list.append("D\n")
 exclude_list.append("Et3byEt2\n")
 exclude_list.append("dptjet1jet3\n")
 exclude_list.append("dphijet2jet3_boost12\n")

 exclude_list.append("thetajet3_boost12\n")
 exclude_list.append("dphijet1jet2_boost\n")
 exclude_list.append("djet1jet2pt\n")
 exclude_list.append("Et2byEt1\n")

 exclude_list.append("dptjet1jet2\n")
 exclude_list.append("Eta3\n")
 exclude_list.append("dphijet1jet3\n")
 exclude_list.append("detajet3jet4\n")

if (var11>0.33 and var11<=0.66):
 exclude_list.append("thetajet3_boost12\n")
 exclude_list.append("dphijet1jet2_boost\n")
 exclude_list.append("djet1jet2pt\n")
 exclude_list.append("Et2byEt1\n")

 exclude_list.append("dptjet1jet2\n")
 exclude_list.append("Eta3\n")
 exclude_list.append("dphijet1jet3\n")
 exclude_list.append("detajet3jet4\n")

if (var11>0.66):
 exclude_list.append("dptjet1jet2\n")
 exclude_list.append("Eta3\n")
 exclude_list.append("dphijet1jet3\n")
 exclude_list.append("detajet3jet4\n")

# print "var11 = ", var11
_vars["var11"]=var11



