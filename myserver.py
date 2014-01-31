#! /usr/bin/env python

""" this is part of the prepare_mva.py

The code is a dispatcher for mva optimization and GUI of the package 
The roles of the dispatcher:
										   (implemented: yes/no/partly)
	1) run mva training in threads localy (yes)
	2) run mva training in batch/grid (yes)
	3) run mva optimization (no)
	4) run best variables finder (yes)
	5) email notifficaction (no)
	6) ?


The GUI does:
										(implemented: yes/no/partly)

	1) 	Plotting control plots of MVA output (yes)
    2)  Download/Upload files from/to dCache (yes)
	3) 	Plotting tunning parameters (partly)
	4)	Starts running mva training (yes)
	5) 	Starts running mva optimization (no)
	6) 	Shows ranking the variables (yes)
    7)  Tests possible overtrainings (yes)
 	8) 	?
	
"""



__author__ =  'Igor Marfin'
__version__=  '1.7'
__nonsense__ = 'HiggsGroup'

import sys
import os 
import time
import re

sys.path.append( os.getcwd()+"/webpy/webpy037/" )
sys.path.append( os.getcwd()+"/grid/" )

import subprocess

import web
from web import form

import prepare_mva
import prepare_mva_grid



# my templates
render = web.template.render('webpy/webpy037/templates/')

# my urls visible by user
urls = (
 '/', 'index',
 '/login', 'Login',
 '/logout', 'Logout',
# "/plots","plots",
 '/image','image',
 '/control','control',
 '/vartesting' , 'vartesting',
 '/processmva','processmva',
 '/processmva2','processmva2',
 '/refresh', 'refresh',
 '/test','test',
 '/test2','test2',
 '/testmva','testmva',
 '/bestpoints','bestpoints',
 '/tableresults', 'tableresults',
 '/grid', 'grid',
 '/ranking','ranking',
 '/optimizevars','optimizevars',
 '/setvarmode','setvarmode',
 '/testovertraining','testovertraining',
 '/testKinematics','testKinematics'    # to plot MC kinematics
)

"""



class plots:
    def GET(self,name):
        ext = name.split(".")[-1] # Gather extension
        cType = {
           "png":"images/png",
            "jpg":"images/jpeg",
            "gif":"images/gif",
            "ico":"images/x-icon"            }
        if name in os.listdir('plots'):  # Security
            web.header("Content-Type", cType[ext]) # Set the Header
            return open('plots/%s'%name,"rb").read() # Notice 'rb' for reading images
        else:
            raise web.notfound()

"""

# do plotting some image
class image:

    def GET(self):

            if (web.input(type=None).type and web.input(ID=None).ID and web.input(MVA=None).MVA):
              return render.myimage(web.input(type=None).type,web.input(ID=None).ID,web.input(MVA=None).MVA)

            return 


# do logging in/logging out  support (as an example), more sophisticated algo is needed
class Login:

    def GET(self):
        return """
        <html>
        <form action="" method="post">
            <input type="text" name="username">
            <input type="submit" value="Login">
        </form>
        </html>
        """


    def POST(self):
        # only set cookie if user login succeeds
        name = web.input(username=None).username
        if name:
            web.setcookie('username', name)
        raise web.seeother('/')




class Logout:

    def GET(self):
        web.setcookie('username', '', expires=-1)
        raise web.seeother('/login')





app = web.application(urls, globals())



  
# Auth Processor
def auth_app_processor(handle):
    path = web.ctx.path
    web.ctx.username = name = web.cookies(username=None).username
    if not name and path != '/login':
        raise web.seeother('/login')
    return handle()



app.add_processor(auth_app_processor)


def prepareplots(mva,id,type):

   if (len(mva)*len(id)<=0): return (None,None)
   (mask,title)=prepare_mva.TestMVAGUI(mva,id,"static",type,True)
   p = subprocess.Popen("ls "+ mask,  stdout=subprocess.PIPE, shell=True)
   mystr,err=p.communicate()
   mystr=mystr.split('\n')
   mystr=mystr[0:-1]
   if len(mystr)<=0:
    mask,title=prepare_mva.TestMVAGUI(mva,id,"static",type,False)
    p = subprocess.Popen("ls "+ mask,  stdout=subprocess.PIPE, shell=True)
    mystr,err=p.communicate()
    mystr=mystr.split('\n')
    mystr=mystr[0:-1]

   return (mystr,title)



############ control:

formMVAControl = form.Form( 
    form.Textbox("type",form.Validator('Must be something from the predifined list', lambda x:x in ['overtrain']) ), 
    form.Textbox("ID", 
        form.notnull,
        form.regexp('\d+', 'Must be a digit'),
        form.Validator('Must be more than 0', lambda x:int(x)>0)),
#    form.Textarea('MVA',form.Validator('Must be something from the predifined list', lambda x:x in ['BDT']),
#    form.Checkbox('curly'), 
    form.Dropdown('MVA', ['BDT', 'BDT', 'BDT'])

)
 
formControl=form.Form(
# Button("action", value="save", html="<b>Save Changes</b>").render()
#    u'<button id="action" value="save" name="action"><b>Save Changes</b></button>'
	form.Button("TESTVAR", html="<b> Go To Variables testing </b>",type="submit"),
	form.Button("TESTMVA", html="<b> Go To MVA output testing </b>",type="submit"),
	form.Button("TRAINMVA",html="<b> Go To MVA training </b>",type="submit")
)


class control:
    def GET(self):
       form = formControl()
       return render.formControl(form)
    
    def POST(self):
       form = formControl()  
       print web.input()
       _testvar=0      
       _testmva=0
       _trainmva=0
       try:
            _b=web.input()["TESTVAR"]
            _testvar=1
       except KeyError, k:
            pass
       try:
            _b= web.input()["TESTMVA"]
            _testmva=1
       except KeyError, k:
            pass
       try:
            _b= web.input()["TRAINMVA"]
            _trainmva=1
       except KeyError, k:
            pass

       if(_trainmva==1): raise web.seeother('/processmva2')
       if (_testvar==1): raise  web.seeother('/vartesting')
       if (_testmva==1): raise  web.seeother('/testmva')

       return render.formControl(form)

############# testKinematics

formKinematics = form.Form(
   form.Dropdown('MVA', ["BDT", "BDT", "BDT"],value="BDT"),
   form.Textbox("Signal pattern",value="M-350",size=50 ),
   form.Textbox("Background pattern",value="30To50*bEnriched_v5,50To150*bEnriched_v5,-150_*bEnriched_v5",size=50 ),
   form.Textbox("Number of events",value="1000",size=50 ),
   form.Textbox("variables",value="M12",size=50 ),
   form.Textarea("Available MC", rows=5, cols=150  ),
   form.Dropdown("ID",args=[],value=""),
   form.Textbox("Cuts",value="",size=50),
   form.Dropdown('Apply MVA?', ["yes", "no"]),
   form.Dropdown('with Data?', ["yes", "no"]),
   form.Dropdown('Type of the plot',["Normalized","Stacked","Filled"],value="Normalized"),
   form.Button("PLOT", html="<b> Plot </b>",type="submit")


)

ID=[]
_sgn=[]
_bkg=[]
class testKinematics:
      text = """ Status: Ready """

      def __init__(self):   
       self.method=""
       self.nums=""
       self.apply=False
       self.data=False
       self.vars=""
       self.paths="" 
       self.cuts=""
       self.type=""

      def GET(self):
       global ID,_sgn,_bkg
       form=formKinematics()
       cmd="ls -d "+prepare_mva.trees_path+"/*/ | xargs -I {} basename {}"
       p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
       self.paths,err=p.communicate()       
       form["Available MC"].value=self.paths
       mva=form["MVA"].value
       results=prepare_mva.ReadResults(mva)
       results=sorted(results,key=lambda x: x[2] ,reverse=True)
       results=[x for x in results if not x[0] == "000000"]
       ID=[x[0] for x in results ]
       form["ID"].args=ID
       form["ID"].value=ID[0]
       form["Cuts"].value=self.cuts
       _sgn=form["Signal pattern"].value
       _sgn=_sgn.split(",") 
       _bkg=form["Background pattern"].value
       _bkg=_bkg.split(",") 
       if (self.apply): form["Apply MVA?"].value="yes"
       else: form["Apply MVA?"].value="no"
       if (self.data): form["with Data?"].value="yes"
       else: form["with Data?"].value="no"
       self.vars=form["variables"].value
       form["Type of the plot"].value=self.type
       return render.formtest6(form,self.text)

      def POST(self):
       global ID,_sgn,_bkg
       form=formKinematics()  
       form["ID"].args=ID

       _isPlot=False
       try:
            _b= web.input()["PLOT"]
            _isPlot=True
       except KeyError, k:
            pass
       method=web.input()["MVA"]
       self.nums=web.input()["Number of events"]
       self.vars=web.input()["variables"] 
       self.paths=web.input()["Available MC"]
       self.cuts=web.input()["Cuts"]
       self.type=web.input()["Type of the plot"]
       if (web.input()["Apply MVA?"]=="yes"): self.apply=True
       else : self.apply=False
       if (web.input()["with Data?"]=="yes"): self.data=True
       else : self.data=False
       form["Available MC"].value=self.paths
       form["variables"].value=self.vars
       form["Number of events"].value= self.nums
       form["Cuts"].value=self.cuts
 
       if (not _isPlot): return render.formtest6(form,self.text)
       vars=self.vars.split(",")
       _id =web.input()["ID"]
       _sgn2=web.input()["Signal pattern"]
       _sgn=_sgn2.split(",") 
       _bkg2=web.input()["Background pattern"]
       _bkg=_bkg2.split(",") 
       print "id ",_id
       print "sgn",_sgn
       print "bkg",_bkg
       
       if (not self.data):
        (grS_before,grS_after,grB_before,grB_after,eff_S,eff_B,B_over_S)=prepare_mva.TestMVACuts(method+"_"+_id,"KinVars"+method,vars,self.cuts, _sgn,_bkg,[],int(self.nums),1e3,False,False)
       else : 
        (grS_before,grS_after,grB_before,grB_after,eff_S,eff_B,B_over_S,grD_before,grD_after)=prepare_mva.TestMVACuts(method+"_"+_id,"KinVars"+method,vars,self.cuts, _sgn,_bkg,[],int(self.nums),1e3,False,True)

       titles=[]
       plotsS=[]
       plotsB=[]
       plotsD=[]
       files=[] 
       titlesMain=[]
       if (not self.apply):
         plotsS=grS_before
         plotsB=grB_before
         titles.append("Sgn (MVA off)")
         titles.append("Bckg (MVA off)")
         if (self.data):
          plotsD=grD_before
          titles.append("Data (MVA off)")
       else:
         plotsS=grS_after
         plotsB=grB_after
         titles.append("Sgn (MVA on)")
         titles.append("Bckg (MVA on)")
         if (self.data):
          plotsD=grD_after
          titles.append("Data (MVA on)")

       Normalized=True if self.type=="Normalized" else False
       doStack=True if self.type=="Stacked" else False
       doFilled=True if self.type=="Filled" else False
       for i in range(len(plotsS)):
        print "plot ",plotsS[i].GetName()
        print "plot ",plotsB[i].GetName()

        print "integ ",plotsS[i].Integral()
        print "integ ",plotsB[i].Integral()

        varname=plotsS[i].GetName().split("_")
        varname=varname[0]
        titlesMain.append(_id+" : "+varname)
        fileout="static/kinematics_"+varname+"_"+self.type
        titles=[ varname+" "+x for x in titles]
        plotsS[i].Rebin(2)
        plotsB[i].Rebin(2)
        if (not self.data):      
         prepare_mva.PrintPlot([plotsS[i],plotsB[i]],[],Normalized,doStack,doFilled,["kBlue","kRed"],titles,fileout)
        else:
         plotsD[i].Rebin(2)
         prepare_mva.PrintPlot([plotsS[i],plotsB[i],plotsD[i]],[],Normalized,doStack,doFilled,["kBlue","kRed","kBlack"],titles,fileout)

        files.append(fileout+".png")
       return render.formtest55(form,files,titlesMain,"")





############# testovertraining


formOvertrain = form.Form(
 		     form.Dropdown('MVA', ["BDT", "BDT", "BDT"]),
 		     form.Dropdown('Number', ['1', '2', '3','4','5','6','7','8','9','10']),
             form.Button("GET", html="<b> Test for overtraining </b>",type="submit")


)

class testovertraining:

     help="""
                do test of first N (upto 10) TMVA results  for overtraing.
                It starts TMVA selection over 1M events for Signal and Background.
                It uses TProof to speed up the process. Can take a few minutes to calculate
                
     """
     method=""
     nums="" 

     def GET(self):
      form=formOvertrain()
      self.method=form["MVA"].value
      self.nums=form["Number"].value
      return render.formtest10(form,[],["no plots available"],[self.help])

     def POST(self):
      form=formOvertrain()
      _isGet=False
      try:
            _b= web.input()["GET"]
            _isSet=True
      except KeyError, k:
            pass
      mva=web.input()["MVA"]
      self.nums=web.input()["Number"]

# get test/train separations
      trains=prepare_mva.GetSummarySeparationMVA(mva,"train")
      tests=prepare_mva.GetSummarySeparationMVA(mva,"test")
      table=[]
      for train in trains:
       tests2=filter(lambda x: x[0] == train[0], tests)
       table.append([train[0],train[1],tests2[0][1] ])

# get plots of possible overtrainings
      allplots=[]
      alltitles=[]
      for i in range(int(self.nums)):
       _id=str(table[i][0])
       plots,title=prepareplots("BDT",_id,98)
#       plots,title=prepareplots(mva,_id,98)
#       plots,title=prepare_mva.TestMVAGUI(self.method,table[i][0],"static",98,False)
       allplots+=plots
       alltitles.append(_id)
# output results
#      print "alltitles=",alltitles
#      print "allplots=",allplots
#      print "table=",table

      self.method=mva
     
      return render.formtest10(form,table,allplots,alltitles)

######## setvarmode
formSetRanking = form.Form(
             form.Dropdown('RankingMode', ['0','1','2','6']),
             form.Dropdown('NormMode', ['0', '3', '4','5']),
             form.Button("SET", html="<b> Set the modes </b>",type="submit"),

)


class setvarmode:

    help="""
    The class sets the mode of variable ranking and NormMode option of TMVA.

    Possible modes for variable ranking:

	0 -- randomly exclude  all variables  used in TMVA training for 3 ranking system
    1 -- ks_0.005_corr_0.30
    2 -- ks_0.05_corr_1.10
    3,4,5  -- not supported for TMVA training (the modes can be used only for ranking studies)
    6 -- 3 ranking excluded variable system
    
    if file .normmode exists, it can contain the modes

    0,3,4,5 where 0 -- for randomly chosen mode,3 -- None, 4-EqualNumEvents ,5 - NumEvents modes accordingly


    """


    def GET(self):
     form=formSetRanking()
     cmd="cat variables.mode" 
     p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
     rankmode,err=p.communicate()
     cmd="cat .normmode" 
     p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
     normmode,err=p.communicate()   
     return render.formtest9(form,"The current modes: ranking is %s and NormMode is %s"%(rankmode,normmode),self.help)

    def POST(self):
      form=formSetRanking()

      _isSet=False
      try:
            _b= web.input()["SET"]
            _isSet=True
      except KeyError, k:
            pass

      rankmode =web.input()["RankingMode"]
      normmode=web.input()["NormMode"]

      cmd="echo %s > variables.mode; cp variables.mode grid/" % rankmode
      p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
      mystr,err=p.communicate()
      cmd="echo %s > .normmode; cp .normmode grid/" % normmode
      p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
      mystr,err=p.communicate()
      return render.formtest9(form,"The current modes: ranking is %s and NormMode is %s"%(rankmode,normmode),self.help)
     

##########ranking
"""
		do ranking of variables
        there are possible modes and plottings:

        mode = 1, run randomly TMVA with fixed exluded variable set aka "not ks_0.005_corr_0.30", 
		 	supported only partly by myserver. This mode requires standalone study
        mode = 2, run randomly TMVA with fixed exluded  variable set aka "not ks_0.05_corr_1.10"
			supported  only partly by myserver. This mode requires standalone study
        mode = 3, or "NMNone" mode, run TMVA once to get KS distances when "NumMode=None"
        mode = 4, or "NMEqNE" mode, run TMVA once to get KS distances when "NumMode=EqualNumberEvents"
        mode = 5, or "NMNumE" mode, run TMVA once to get KS distances when "NumMode=NumberEvents"
        mode =0 , .........

"""

formRanking = form.Form(
			 form.Dropdown('mode', ['0','1','2','3', '4', '5']),
 		     form.Dropdown('MVA', ['BDT', 'BDT', 'BDT']),
             form.Button("GET", html="<b> Get properties of the input variables  </b>",type="submit"),
             form.Button("SET",html="<b> Set the possible mode of variable ranking  </b>",type="submit")

)


class ranking:
   
    text="""

        <p>  Status: Ready  </p>


    """
   
    def GET(self):
     form=formRanking()
     return render.formtest7(form,[],[],"")

    def POST(self):
     form=formRanking()
     _isGet=False
     _isSet=False
     try:
            _b= web.input()["GET"]
            _isGet=True
     except KeyError, k:
            pass
     try:
            _b= web.input()["SET"]
            _isSet=True
     except KeyError, k:
            pass
		
     mode =web.input().mode
     mva=web.input().MVA

     if (_isSet):
      myout= """
         <script type = "text/javascript" >     window.open('/setvarmode', '_blank', '');   

         </script>
         """
      return myout

     if (int(mode)==0 ):
      cmd="echo %s > variables.mode" % mode
      p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
      mystr,err=p.communicate()
      configs=prepare_mva.ReadBestVariables(mva)
      # find all entries except ones for mode=3,4,5
      configs=filter(lambda x: not x[0] in ['000000','NMNone','NMEqNE','NMNumE'], configs)
      print "len(config)=",len(configs)
      if (len(configs)<20): 
      # need processing (at least 100 times) 
#       raise web.seeother('/optimizevars')
       myout= """
         <script type = "text/javascript" >     window.open('/optimizevars', '_blank', '');        </script>
         """
       return myout
      else:
        titlePage=" 3-ranking system: \n         total number of trainings used --> %d \n         the best KS  --> %f  for id --> %s            "
        configs=sorted(configs,key=lambda x: x[4],reverse=True)
        plots=[]
        title=""
        plots,title=prepareplots(mva,configs[0][0],0)
        plots2,title=prepareplots(mva,configs[0][0],3)
        titlePage=titlePage%(len(configs),configs[0][4],configs[0][0])

        (level1,level2,level3)=prepare_mva.OptimizeVariablesRanking(mva,10,False,['000000','NMNone','NMEqNE','NMNumE'])
        myKS1=[]
        myKS2=[]
        myKS3=[]
        allvars=prepare_mva.ProcessVariables("ks_0.00_corr_1.10",[],True,False)
        for var in level1: 
         allvars1=filter(lambda x: x[0]==var[0],allvars)
         myKS1.append([var[0],allvars1[0][1]])
        for var in level2: 
         allvars1=filter(lambda x: x[0]==var[0],allvars) 
         myKS2.append([var[0],allvars1[0][1]])
        for var in level3: 
         allvars1=filter(lambda x: x[0]==var[0],allvars) 
         myKS3.append([var[0],allvars1[0][1]])
        print "plots=",plots
        return render.formtest8(form,myKS1,myKS2,myKS3, plots+plots2,titlePage)

     if (int(mode)<=2 and int(mode)>0 ):
      myKS=[]
      KS=[]
      titlePage=""" KS >= %f and correlation<= %f """
      if (int(mode)==1):  
       KS=prepare_mva.ProcessVariables("ks_0.005_corr_0.30",[],True,False)
       titlePage=titlePage%(0.005,0.30)
      if (int(mode)==2):  
       KS=prepare_mva.ProcessVariables("ks_0.05_corr_1.10",[],True,False)
       titlePage=titlePage%(0.05,1.0)
      for var in KS: myKS.append([var[0],var[1]])
      myKS=sorted(myKS,key=lambda x: x[1],reverse=True)
      print myKS
      print titlePage	
      return render.formtest7(form,myKS, ["No plots available"],titlePage)

     cmd="echo %s > variables.mode" % mode
     p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
     mystr,err=p.communicate()
     KS=[]
     if os.path.exists(mva+"_bestvariables.gz"):
      KS=prepare_mva.GetKSNumMode(mva,int(mode),[],False)
     else:
      prepare_mva.OptimizeVariablesTraining()
     if len(KS)==0:
      prepare_mva.OptimizeVariablesTraining()
      KS=prepare_mva.GetKSNumMode(mva,int(mode),[],False)
     print "KS is ", KS

     myKS=[]
     for var in KS: myKS.append([var,KS[var]])
     myKS=sorted(myKS,key=lambda x: x[1],reverse=True)
# prepare plots of variables
     id="blabla"
     titlePage=""" NormMode = %s """
     if (int(mode)==3): 
      id="NMNone"
      titlePage=titlePage%"""'None'"""
     elif (int(mode)==4): 
      id="NMEqNE" 
      titlePage=titlePage%"""'EqualNumEvents'"""

     elif (int(mode)==5): 
      id="NMNumE" 
      titlePage=titlePage%"""'NumEvents'"""

     plots=[]
     title=""
     (mask,title)=prepare_mva.TestMVAGUI(mva,id,"static",0,True)        
     p = subprocess.Popen("ls "+ mask,  stdout=subprocess.PIPE, shell=True)
     mystr,err=p.communicate()
     mystr=mystr.split('\n')
     mystr=mystr[0:-1]
     print "mystr=",mystr
     if len(mystr)<=0:
         mask,title=prepare_mva.TestMVAGUI(mva,id,"static",0,False)
         p = subprocess.Popen("ls "+ mask,  stdout=subprocess.PIPE, shell=True)
         mystr,err=p.communicate()
         mystr=mystr.split('\n')
         mystr=mystr[0:-1]
     plots=mystr
     print plots
     
     return render.formtest7(form,myKS, plots,titlePage)
   

######### optimizevars
class optimizevars:

     def GET(self):
       global progress,logfiles,runs,maxruns,progress2,progressbar
       cmd="ls mylog*"
       p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
       mystr,err=p.communicate()
       mystr=mystr.split('\n')       
       mylogs=mystr       
       cmd="cat .varoptimizer.rc  | grep -v \"#\" | awk '{print $0}'"
       p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
       mystr,err=p.communicate()
       mystr=mystr.split('\n')
       mystatus=mystr
#       print mylogs
#       print mystatus
       form = formProcessMVA()
       progress3=[]
       for logfile in mylogs:
        if len(logfile)<=0: continue
        cmd="cat "+ logfile + " | grep \"%\"  | awk '{print $0}' |  sed -r \"s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]//g\" "
        p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
        mystr,err=p.communicate()
        mystr2=mystr.split('\r')
        progress3.append(logfile+" processing... : ")
        if (len(mystr2)>1):   progress3[-1]+=mystr2[-2]
       
       return render.mvarun2(form,mystatus,progress3,"<br> <p>help: type \" Submit Query leaving default or empty fields\" </p>")


     def POST(self):
       form = formProcessMVA()
       if not form.validates():
          print "wrong"
          help="""
             help:     if you want to change ntreads, you can do it when runs=0 otherwise use the value of ntreads > the current value always
          """
          return render.mvarun2(form,[],[],help)
       cmd="cat .varoptimizer.rc | grep \"_runs_\" | grep -v \"#\" | awk '{print $2}'"
       p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
       mystr,err=p.communicate()
       runs2=int(mystr)
       runs3=int(mystr)
       runs3+=int(form["how_many_runs"].value)
       cmd="cat .varoptimizer.rc | grep \"_maxrun_\" | grep -v \"#\" | awk '{print $2}'"
       p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
       mystr,err=p.communicate()
       maxruns3=int(mystr)
       maxruns3+=int(form["how_many_runs"].value)
       numthreads3=int(form["how_many_threads"].value)
       cmd="cat .varoptimizer.rc | grep \"_ntreads_\" | grep -v \"#\" | awk '{print $2}'"
       p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
       mystr,err=p.communicate()
       if (numthreads3<int(mystr) and runs2>0 ): numthreads3=int(mystr)
        

       if not web.input().has_key('see_only_status'):
        myfile = open('.varoptimizer.rc', 'r+w')
        data = myfile.read()
        data=re.sub("\n.*_runs_.*\n","\n_runs_  " + str(runs3) +  "\n",data)
        data=re.sub("\n.*_maxrun_.*\n","\n_maxrun_  " + str(maxruns3) + "\n",data)
        data=re.sub("\n.*_ntreads_.*\n","\n_ntreads_  " + str(numthreads3) + "\n",data)
        myfile.seek(0)
        myfile.write(data)
        myfile.close()                
       refresh=""
       if (int(form["Look_at_log"].value)>-1) and web.input().has_key('see_only_status'):
        refresh="""
        <script type = "text/javascript" >
        window.open('/refresh?file=%s', '_blank', '');
        </script>
        """ % ( "mylog" + form["Look_at_log"].value ) 
       """ """

       return render.mvarun2(form,[],["progressing log files"],refresh)



######### grid


formGrid=form.Form(

	form.Button("LOG", html="<b> View Log of the latest CRAB run  </b>",type="submit"),
	form.Button("START", html="<b> Start the  CRAB run  </b>",type="submit"),
	form.Button("GET", html="<b> Get and Merge the output of the latest  CRAB run  </b>",type="submit"),
    form.Textbox("Base pathname","some vaule",size=150 ),
    form.Textbox("Base pathname in crab.cfg","some vaule",size=150),
    form.Textbox("suffix",size=50 ),
    form.Dropdown('MVA', ['BDT', 'BDT', 'BDT']),
    form.Textbox("Events",value="100",size=50 ),
    form.Textbox("Number of jobs",value="20",size=50 ),
    form.Textarea("Available pathes", rows=5, cols=150  )
   
)

class grid:
    text="""
 
        <p>  Status: Ready  </p>


    """

    def GET(self):
     form=formGrid()
     cmd="cat grid/dcache_scratch | grep \"_basepathname_\" | awk '{print $2}'"
     p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
     mystr,err=p.communicate()
     mystr.replace("\n","")
     form["Base pathname"].value=mystr
     cmd="cat grid/dcache_scratch | grep \"_basepathnameCRAB_\" | awk '{print $2}'"
     p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
     mystr,err=p.communicate()
     mystr.replace("\n","")
     form["Base pathname in crab.cfg"].value=mystr

     cmd="cat grid/dcache_scratch | grep \"_path_\" | awk '{print $2}'"
     p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
     mystr,err=p.communicate()
     form["Available pathes"].value=mystr

     return render.formtest6(form,self.text)

    def POST(self):
     form=formGrid()
     cmd="cat grid/dcache_scratch | grep \"_basepathname_\" | awk '{print $2}'"
     p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
     mystr,err=p.communicate()
     mystr.replace("\n","")
     form["Base pathname"].value=mystr
     cmd="cat grid/dcache_scratch | grep \"_basepathnameCRAB_\" | awk '{print $2}'"
     p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
     mystr,err=p.communicate()
     mystr.replace("\n","")     
     form["Base pathname in crab.cfg"].value=mystr

     cmd="cat grid/dcache_scratch | grep \"_path_\" | awk '{print $2}'"
     p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
     mystr,err=p.communicate()
     form["Available pathes"].value=mystr


#     form=formGrid()
     _isLog=False
     _isStart=False
     _isGet=False
     try:
            _b= web.input()["LOG"]
            _isLog=True
     except KeyError, k:
            pass
     try:
            _b= web.input()["START"]
            _isStart=True
     except KeyError, k:
            pass
     try:
            _b= web.input()["GET"]
            _isGet=True
     except KeyError, k:
            pass

     if (_isLog):
             p = subprocess.Popen(" voms-proxy-init -voms cms -valid 192:00 -pwstdin < grid_init", stdout=subprocess.PIPE,shell=True)
             p.wait()
             if web.input()["suffix"] != "":
              pathname=str(web.input()["Base pathname"]+web.input()["suffix"]).replace("\n","")
              pathnameCRAB=str(web.input()["Base pathname in crab.cfg"]+web.input()["suffix"]).replace("\n","")
              print pathnameCRAB
              f=open('grid/dcache_scratch','r')
              keys=[]
              vals=[]
              lines=f.readlines()
              f.close()
              for line in lines:
               key,val=line.split()
               if (key=="_defaultpath_"): vals.append(pathname)
               elif (key=="_defaultpathCRAB_"): vals.append(pathnameCRAB)
               else: vals.append(val)
               keys.append(key) 
              f=open('grid/dcache_scratch','w')
              for i in range(len(vals)): f.write("%s  %s\n"%(keys[i],vals[i]))
              f.close()
              cmd2="""cd grid; ls -d crab_*/log/crab.log | xargs -I {} echo " grep -l  \"`cat dcache_scratch | grep _defaultpathCRAB_ | awk '{print $2}'`\" {} " |sh |  awk -F'/' '{print "crab -c",  $1 , "-status" }' """
              p2 = subprocess.Popen(cmd2,  stdout=subprocess.PIPE, shell=True)
              print "cmd2=",cmd2
              mystr2,err=p2.communicate()
              mystr2=mystr2.replace("\n" , "; ")
              print "mystr2=",mystr2
              cmd="cd grid;"+ mystr2
             else:
              cmd="cd grid; crab -status"
             print "cmd=",cmd
             p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
             mystr,err=p.communicate()
             print "mystr=",mystr
             print "err=",err
             self.text="""
             <pre><code>
               %s
             </code></pre>
             """ % mystr 
             """ """

     if (_isGet):
      
         cmd="cd grid;  ./copySrmFilesNoRecursive `cat dcache_scratch | grep _defaultpath_ | awk '{print $2}'` _result"
         print cmd
         p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
         mystr1,err=p.communicate()
         print mystr1
         cmd="cd grid;  ./copySrmFilesNoRecursive `cat dcache_scratch | grep _defaultpath_ | awk '{print $2}'` _config"
         print cmd
         p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
         mystr2,err=p.communicate()
         cmd="cd grid;  ./copySrmFilesNoRecursive `cat dcache_scratch | grep _defaultpath_ | awk '{print $2}'` root_files"
         p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
         mystr3,err=p.communicate()
         mva_method=web.input()["MVA"]
         prepare_mva_grid.MergeConfigs(mva_method,"grid/")
         prepare_mva_grid.MergeResults(mva_method,"grid/")
         self.text="""
             <pre><code>
               %s
             </code></pre>
             """ % (mystr1+mystr2+mystr3)
         """ """
  


     if (_isStart):
             pathname=str(web.input()["Base pathname"]+web.input()["suffix"]).replace("\n","")
             pathnameCRAB=str(web.input()["Base pathname in crab.cfg"]+web.input()["suffix"]).replace("\n","")

             print pathnameCRAB
             f=open('grid/dcache_scratch','r')
             keys=[]
             vals=[]
             lines=f.readlines()
             f.close()
             for line in lines:
              key,val=line.split()
              if (key=="_defaultpath_"): vals.append(pathname)
              elif (key=="_defaultpathCRAB_"): vals.append(pathnameCRAB)
              else: vals.append(val)
              keys.append(key) 
             vals.append(pathname)
             keys.append("_path_")
             f=open('grid/dcache_scratch','w')
             for i in range(len(vals)): f.write("%s  %s\n"%(keys[i],vals[i]))
             f.close()

             nevts=web.input()["Events"].replace("\n","")
             njobs=web.input()["Number of jobs"].replace("\n","")
             p = subprocess.Popen(" voms-proxy-init -voms cms -valid 192:00 -pwstdin < grid_init", stdout=subprocess.PIPE,shell=True)
             p.wait()

             cmd="cd grid; crab  -USER.user_remote_dir=`cat dcache_scratch | grep _defaultpathCRAB_ | awk '{print $2}'` -CMSSW.total_number_of_events=%s -CMSSW.number_of_jobs=%s -create -submit"%(nevts,njobs)
             p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
             mystr,err=p.communicate()
             print "mystr=",mystr
             print "err=",err

             self.text="""
             <pre><code>
               %s
             </code></pre>
             """ % mystr
             """ """

    
     return render.formtest6(form,self.text)


######tableresults:


formTableRes=form.Form(
		form.Dropdown('MVA', ['BDT', 'BDT', 'BDT'])

)


class tableresults:

         help="""

         <h3 style="margin-left:2em"> Legenda </h3>
         
         <p style="color:red; margin-left: 2em"> Results obtained from local trainings </p> 
         <p style="color:green; margin-left: 2em"> Results obtained from grid trainings </p> 



         """

         def GET(self):
         
          form=formTableRes()
          return render.table(form,[],self.help)


         def POST(self):
         
          form=formTableRes()
          mva_method=web.input().MVA
          print "mva_method=",mva_method
          mvaPoints=prepare_mva.GetNumPoints(mva_method)
# local results
          results=[]
          for i in range(mvaPoints): 
           result=prepare_mva.FindOptimalResult(mva_method,i)
           if len(result)==5:   results.append([result[0],result[2],result[3],result[4],"None","local"]) 
           elif len(result)==6: results.append([result[0],result[2],result[3],result[4],result[5],"local"])

# grid results
          mvaPoints=prepare_mva.GetNumPoints("grid/"+mva_method)
          results2=[]
          for i in range(mvaPoints): 
           result=prepare_mva.FindOptimalResult("grid/"+mva_method,i)           
           if len(result)==5:  results2.append([result[0],result[2],result[3],result[4],"None","grid"]) 
           elif len(result)==6: results2.append([result[0],result[2],result[3],result[4],result[5],"grid"])
       
          results+=results2
          results_sorted=sorted(results,key=lambda x: x[1],reverse=True)      
          return render.table(form,results_sorted,self.help)



########### bestpoints

formBestPoints=form.Form(
			form.Dropdown('MVA', ['BDT', 'BDT', 'BDT']),
			form.Dropdown("Num_of_points",['1','2','3','4','5','6','7','8','9','10']),
			form.Dropdown('type',['-2','-1','0','1','2','3','6','7','98','99'])

) # end of formBestPoints


class bestpoints:
          
         help="""
                       
         the check and validation of first N optimal points (Num_of_points, Num_of_points<=10) of 
         TMVA response with the highest KS distances
               possible types of the plots:

         0: input variables
         1: correlations
         2: Plots the output of each classifier for the test data
         3: Plots the output of each classifier for the test (histograms) and training (dots) data
         4: Plots the probability of each classifier for the test data
         5: Plots the Rarity of each classifier for the test data
         6: Plots B/S 'before cut' efficiencies
         7: Plots B/S, purity vs efficiency for 'before cut' mva selection
         99: Distribution of MVA separation

         WARNING: please, remember

         if type=-1 then all plots will be created

         """

         mva_method=""
         num=1
         _type=-2

         def GET(self):
          form=formBestPoints()
          return render.formtest(form)

         def POST(self):
          form=formBestPoints()
          plots=[]
          titles=[]
 
          mva_method=web.input().MVA
          print "mva_method = ",mva_method
          results=prepare_mva.ReadResults(mva_method)

  # read grid results
          if os.path.exists("grid/"+mva_method+"_result.gz"):          
           results2=prepare_mva.ReadResults("grid/"+mva_method)
           results+=results2

          results=sorted(results,key=lambda x: x[2] ,reverse=True)
          results=[x for x in results if not x[0] == "000000"]
          # select result having root files
          # results=[x for x in results  if os.path.isfile("TMVA_"+mva_method+"_"+x[0]+".root") ]
          num=int(web.input()["Num_of_points"])
          _type=int(web.input()["type"])
          idsplot=[]

          if (_type==-2):     return render.formtest5(form,plots,titles,idsplot,self.help)

          for i in range(num):  idsplot.append(results[i][0])
          if _type<0:
           for type in ['0','1','2','3','6','7','98','99']:
            plotstype=[]
            title=""
            mask=""
            for id in idsplot:
             print "id=",id
             (mask,title)=prepare_mva.TestMVAGUI(mva_method,id,"static",int(type),True)
             p = subprocess.Popen("ls "+ mask,  stdout=subprocess.PIPE, shell=True)
             mystr,err=p.communicate()
             mystr=mystr.split('\n')
             mystr=mystr[0:-1]
             print "mystr=",mystr
             if len(mystr)<=0:
              mask,title=prepare_mva.TestMVAGUI(mva_method,id,"static",int(type),False)
              p = subprocess.Popen("ls "+ mask,  stdout=subprocess.PIPE, shell=True)
              mystr,err=p.communicate()
              mystr=mystr.split('\n')
              mystr=mystr[0:-1]
             plotstype.append(mystr)
            plots.append(plotstype)
            titles.append(title)
          else : # _type<0
           plotstype=[]
           for id in idsplot:
            (mask,title)=prepare_mva.TestMVAGUI(mva_method,id,"static",int(_type),True)
            p = subprocess.Popen("ls "+ mask,  stdout=subprocess.PIPE, shell=True)
            mystr,err=p.communicate()
            mystr=mystr.split('\n')
            mystr=mystr[0:-1]
            if len(mystr)<=0: 
             (mask,title)=prepare_mva.TestMVAGUI(mva_method,id,"static",int(_type),False)
             p = subprocess.Popen("ls "+ mask,  stdout=subprocess.PIPE, shell=True)
             mystr,err=p.communicate()
             mystr=mystr.split('\n')
             mystr=mystr[0:-1]
            plotstype.append(mystr)
           plots.append(plotstype)
           titles.append(title)


          print plots
          print titles
          print idsplot
          return render.formtest5(form,plots,titles,idsplot,self.help)



############ testmva:



formMVATest1 = form.Form(
			form.Dropdown('MVA', ['BDT', 'BDT', 'BDT']),
			 form.Button("BESTPOINT",html="<b> Go To 'best points' dialog </b>",type="submit")

) # end of formMVATest

class testmva:

      help="""
      possible types of the plots:

      0: input variables
      1: correlations 
      2: Plots the output of each classifier for the test data
      3: Plots the output of each classifier for the test (histograms) and training (dots) data
      4: Plots the probability of each classifier for the test data 
      5: Plots the Rarity of each classifier for the test data
      6: Plots B/S 'before cut' efficiencies
      7: Plots B/S, purity vs efficiency for 'before cut' mva selection
      99: Distribution of MVA separation

	  WARNING: please, remember 
			
		if type=-1 then all plots will be created
		if id=-1 then plots for all mva computers will be created
		TRY to AVOID to use id=-1 because of possible problems with 
		overloading your socket connection!!!!

		type/id=-2 are the default values leading to empty requests.
	
      """      
      """ the code goes here"""
      mva_method=""
      def GET(self):       
       form1=formMVATest1()
       return render.formtest(form1)

      def POST(self):
       form1=formMVATest1()
       """ """
       plots=[]
       titles=[]

       _bestpoint=0
       try:
            _b=web.input()["BESTPOINT"]
            _bestpoint=1
       except KeyError, k:
           pass
       if (_bestpoint==1): 
        myout= """
         <script type = "text/javascript" >     window.open('/bestpoints', '_blank', '');        </script>        
         """
        return myout
        """ """


       mva_method=web.input().MVA       
       results=prepare_mva.ReadResults(mva_method)
  # read grid results
       results2=prepare_mva.ReadResults("grid/"+mva_method)
       results+=results2
       results=sorted(results,key=lambda x: x[2] ,reverse=True)
       results=[x for x in results if not x[0] == "000000"] 
       ids=[x[0] for x in results ]
           

       ids2=prepare_mva.ReadBestVariables(mva_method)
       ids2=[x[0] for x in ids2 ]
       ids+=ids2
      
       print ids

       idsplot=ids
       ids=['-2','-1']+ids
       form2=form.Form(
            form.Dropdown('id', ids),
            form.Dropdown('type',['-2','-1','0','1','2','3','6','7','98','99'])
       )
       _id=-2
       _type=-2
       try:
        _id=web.input()["id"]
        _type=int(web.input()["type"])
       except  KeyError, k:
        pass
       print _id,_type       
       if (_type==-2 and _id==-2):     return render.formtest4(form1,form2,plots,titles,self.help)
       if _type<0:
        for type in ['0','1','2','3','6','7','98','99']:    
         plotstype=[]
         title=""
         mask=""
         if int(_id)<0:
          for id in idsplot:
           (mask,title)=prepare_mva.TestMVAGUI(mva_method,id,"static",int(type),True)
           p = subprocess.Popen("ls "+ mask,  stdout=subprocess.PIPE, shell=True)
           mystr,err=p.communicate()
           mystr=mystr.split('\n')
           mystr=mystr[0:-1]
           if len(mystr)<=0: 
            mask,title=prepare_mva.TestMVAGUI(mva_method,id,"static",int(type),False)
            p = subprocess.Popen("ls "+ mask,  stdout=subprocess.PIPE, shell=True)
            mystr,err=p.communicate()
            mystr=mystr.split('\n')
            mystr=mystr[0:-1]
           plotstype.append(mystr)
         else:   # _id<0
          print "_id=",_id
          (mask,title)=prepare_mva.TestMVAGUI(mva_method,str(_id),"static",int(type),True)
          p = subprocess.Popen("ls "+ mask,  stdout=subprocess.PIPE, shell=True)
          mystr,err=p.communicate()
          mystr=mystr.split('\n')
          mystr=mystr[0:-1]
          if (type==99) : mystr=""
          if len(mystr)<=0:
           mask,title=prepare_mva.TestMVAGUI(mva_method,str(_id),"static",int(type),False)
           p = subprocess.Popen("ls "+ mask,  stdout=subprocess.PIPE, shell=True)
           mystr,err=p.communicate()
           mystr=mystr.split('\n')
           mystr=mystr[0:-1]
          plotstype.append(mystr)
         plots.append(plotstype)
         titles.append(title)
       else : # _type<0
         plotstype=[]
         if int(_id)<0:
          for id in idsplot:
           (mask,title)=prepare_mva.TestMVAGUI(mva_method,str(id),"static",int(_type),True)
           p = subprocess.Popen("ls "+ mask,  stdout=subprocess.PIPE, shell=True)
           mystr,err=p.communicate()
           mystr=mystr.split('\n')
           mystr=mystr[0:-1]
           if len(mystr)<=0: 
            (mask,title)=prepare_mva.TestMVAGUI(mva_method,str(id),"static",int(_type),False)
            p = subprocess.Popen("ls "+ mask,  stdout=subprocess.PIPE, shell=True)
            mystr,err=p.communicate()
            mystr=mystr.split('\n')
            mystr=mystr[0:-1]
           plotstype.append(mystr)
         else:   # _id<0
          print "_id=",_id
          (mask,title)=prepare_mva.TestMVAGUI(mva_method,str(_id),"static",int(_type),True)
          p = subprocess.Popen("ls "+ mask,  stdout=subprocess.PIPE, shell=True)
          mystr,err=p.communicate()
          mystr=mystr.split('\n')
          mystr=mystr[0:-1]
          if (int(_type)==99) : mystr=""
          if len(mystr)<=0:
           mask,title=prepare_mva.TestMVAGUI(mva_method,str(_id),"static",int(_type),False)
           p = subprocess.Popen("ls "+ mask,  stdout=subprocess.PIPE, shell=True)
           mystr,err=p.communicate()
           mystr=mystr.split('\n')
           mystr=mystr[0:-1]
          plotstype.append(mystr)
         plots.append(plotstype)
         titles.append(title)
 
#       print "titles=",titles
#       print "plots=",plots

       return render.formtest4(form1,form2,plots,titles,self.help)
       


############ vartesting:



formVarTest = form.Form( 
#    form.Textbox("interpolator",form.Validator('Must be something from the predifined list', lambda x:x in ['overtrain']) ), 
     form.Dropdown('interpolator', ['Rbf', 'Rbf-gaussian', 'Rbf-inverse']),
    form.Textbox("position", 
        form.notnull#,
#        form.regexp('\w+', 'Must be a digit')#,
#        form.Validator('Must be more than 0', lambda x:int(x)>0) 
         ),
    form.Textbox(name="smooth",value="0.00005",
        validators=form.notnull
    ),
    form.Dropdown("options",["undefined","robust"]),
    form.Dropdown('MVA', ['BDT', 'BDT', 'BDT'])
)

	



class vartesting:

    def GET(self):
       form=formVarTest()
       return render.myform(form,[],[],[])
    
    def POST(self):
       form = formVarTest()
       if not form.validates():
            return render.myform(form,[],[],[])
       else:
# interpolation="Rbf",_smooth=0.00005,options="robust"
        myinterpolator=prepare_mva.Interpolate_MVA(form["MVA"].value,form["interpolator"].value,_smooth=float(form["smooth"].value),options=form["options"].value)
        (canvs,grs)=prepare_mva.DrawVariables(form["MVA"].value,myinterpolator)
        (canvs2,grs2)=prepare_mva.DrawOptimalPoints(form["MVA"].value,myinterpolator)
        vars=prepare_mva.PrintVariableNames(form["MVA"].value,True)
        pos=int(form["position"].value)
        picts=[]
        help_title=["exclude_template_BDT.py","option_book_template_BDT.py","option_train_test_template_BDT.py"]
        help_content=[]
        for help in help_title:
         p = subprocess.Popen("cat "+ help,  stdout=subprocess.PIPE, shell=True)
         mystr,err=p.communicate()
         help_content.append(mystr) 
        if pos>=0:
          pict=vars[pos]
          gr=prepare_mva.PlotAllPoints(form["MVA"].value,pos)
          if (pos>0): grs3=[gr  for i in range(pos+1)]
          else: grs3=[gr] 
          print grs3
          prepare_mva.DrawVariables2File([grs3,grs,grs2],[pos],"test-"+pict)
          picts.append("test-"+pict)
          os.system(" mv "+"test-"+pict+".png  static/" )  
        else:
          for i in range(len(vars)):
           pict=vars[i]
           gr=prepare_mva.PlotAllPoints(form["MVA"].value,i)
           grs3=[gr  for i in range(i+1)]
           prepare_mva.DrawVariables2File([grs3,grs,grs2],[i],"test-"+pict)
           picts.append("test-"+pict)
           os.system(" mv "+"test-"+pict+".png  static/" )  
        return render.myform(form,picts,help_title,help_content)    


ii=int(0)

############ refresh:

	
class refresh:

    def GET(self):
     global ii
     ii+=1
     cmd="cat mylog0"
     if (web.input(file=None).file):
      cmd="cat "+web.input(file=None).file
     p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
     mystr,err=p.communicate()  
     return  render.refresh(mystr)




############# test2:


formTest2=form.Form(
          
		    form.Checkbox('curly',checked=True)

) # end of 


class test2:

    def GET(self):
       form=formTest2()
       return render.formtest(form)


    def POST(self):
       form=formTest2()
       print form.d.curly
       return  """

				%s
                %s
       """    % (form['curly'].get_value(),web.input().has_key('curly'))


""" """



############ test:


class test:

    def GET(self):
       return """
       <script type = "text/javascript" >    
       window.open('/', '_blank', 'toolbar=0,location=0,menubar=0');
       </script>
       """    

""" """


############ processmva:

formProcessMVA=form.Form(
        form.Textbox("how_many_runs",
        form.notnull,
        form.regexp('\d+', 'Must be a digit'),
        form.Validator('Must be more than 0', lambda x:int(x)>0)
        ),
       form.Textbox("how_many_threads",
        form.notnull,
        form.regexp('\d+', 'Must be a digit'),
        form.Validator('Must be more than 0', lambda x:int(x)>0)
        ),       
        form.Checkbox('see_only_status',checked=False),        
        form.Textbox("Look_at_log",form.notnull, form.Validator('Must be more than -2', lambda x:int(x)>-2),
        value="-1"
       ),

)





logfiles=[] # contain a list of log files used by system for local runs
runs=0
maxruns=0
numthreads=0
progress=[]
progress2="Runs(left)=%d     Progress:  %d%%    %s"
progressbar=""


class processmva2:

     def GET(self):
       global progress,logfiles,runs,maxruns,progress2,progressbar
       cmd="ls mylog*"
       p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
       mystr,err=p.communicate()
       mystr=mystr.split('\n')       
       mylogs=mystr       
       cmd="cat .monitor2.rc  | grep -v \"#\" | awk '{print $0}'"
       p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
       mystr,err=p.communicate()
       mystr=mystr.split('\n')
       mystatus=mystr
#       print mylogs
#       print mystatus
       form = formProcessMVA()
       progress3=[]
       for logfile in mylogs:
        if len(logfile)<=0: continue
        cmd="cat "+ logfile + " | grep \"%\"  | awk '{print $0}' |  sed -r \"s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]//g\" "
        p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
        mystr,err=p.communicate()
        mystr2=mystr.split('\r')
        progress3.append(logfile+" processing... : ")
        if (len(mystr2)>1):   progress3[-1]+=mystr2[-2]
       
       return render.mvarun2(form,mystatus,progress3,"<br> <p>help: type \" Submit Query leaving default or empty fields\" </p>")


     def POST(self):
       form = formProcessMVA()
       if not form.validates():
          print "wrong"
          help="""
             help:     if you want to change ntreads, you can do it when runs=0 otherwise use the value of ntreads > the current value always
          """
          return render.mvarun2(form,[],[],help)
       cmd="cat .monitor2.rc | grep \"_runs_\" | grep -v \"#\" | awk '{print $2}'"
       p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
       mystr,err=p.communicate()
       runs2=int(mystr)
       runs3=int(mystr)
       runs3+=int(form["how_many_runs"].value)
       cmd="cat .monitor2.rc | grep \"_maxrun_\" | grep -v \"#\" | awk '{print $2}'"
       p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
       mystr,err=p.communicate()
       maxruns3=int(mystr)
       maxruns3+=int(form["how_many_runs"].value)
       numthreads3=int(form["how_many_threads"].value)
       cmd="cat .monitor2.rc | grep \"_ntreads_\" | grep -v \"#\" | awk '{print $2}'"
       p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
       mystr,err=p.communicate()
       if (numthreads3<int(mystr) and runs2>0 ): numthreads3=int(mystr)
        

       if not web.input().has_key('see_only_status'):
        myfile = open('.monitor2.rc', 'r+w')
        data = myfile.read()
        data=re.sub("\n.*_runs_.*\n","\n_runs_  " + str(runs3) +  "\n",data)
        data=re.sub("\n.*_maxrun_.*\n","\n_maxrun_  " + str(maxruns3) + "\n",data)
        data=re.sub("\n.*_ntreads_.*\n","\n_ntreads_  " + str(numthreads3) + "\n",data)
        myfile.seek(0)
        myfile.write(data)
        myfile.close()                
       refresh=""
       if (int(form["Look_at_log"].value)>-1) and web.input().has_key('see_only_status'):
        refresh="""
        <script type = "text/javascript" >
        window.open('/refresh?file=%s', '_blank', '');
        </script>
        """ % ( "mylog" + form["Look_at_log"].value ) 
       """ """

       return render.mvarun2(form,[],["progressing log files"],refresh)


class processmva:

    def GET(self):
        global progress,logfiles,runs,maxruns,progress2,progressbar
#        print logfiles
#        print progress  
        for i in range(len(logfiles)):
# get the current status
         cmd="cat "+ logfiles[i] + " | grep \"%\"  | awk '{print $0}' |  sed -r \"s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]//g\" "
         p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
         mystr,err=p.communicate()  
#         fd = open('mytest.txt','w') # open the result file in write mode
#         old_stdout = sys.stdout   # store the default system handler to be able to restore it
#         sys.stdout = fd # Now your file is used by print as destination 
         mystr2=mystr.split('\r') 
#         print mystr2
#         sys.stdout=old_stdout # here we restore the default behavior
#         fd.close() # to not forget to close your file
         progress[i]=logfiles[i]+" processing... : "
         if (len(mystr2)>1):   progress[i]+=mystr2[-2]

# test if we've been finished 
        what_to_remove=[]
        for i in range(len(logfiles)):
         cmd="cat "+ logfiles[i] + " | grep \"%\"  | awk '{print $0}' |  sed -r \"s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]//g\" | grep Elapsed " 
         p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, shell=True)
         mystr,err=p.communicate()
#         print "mystr=",mystr
         if (len(mystr)>0): 
          what_to_remove.append(i)
          os.system("rm "+logfiles[i])
        logfiles=[logfiles[i] for i in range(len(logfiles)) if not  i  in what_to_remove ]
        progress=[progress[i] for i in range(len(progress)) if not  i  in what_to_remove ]

        if (runs>0):        
         for j in range(numthreads):
          if not os.path.isfile("mylog"+str(j)):   
           logfiles.append("mylog"+str(j))
           os.system("nohup ./prepare_mva.py --run >& " + logfiles[-1]+ " &")
           time.sleep(5)
           progress.append("start processing... "+ logfiles[-1])        
           runs-=1
           progressbar+="="

        form = formProcessMVA()
        # make sure you create a copy of the form by calling it (line above)
        # Otherwise changes will appear globally


     
        if (maxruns>0): return render.mvarun(form,progress, progress2%(runs,100*(maxruns-runs)/maxruns,progressbar),"" )
        else: return render.mvarun(form,progress, progress2%(0,0,""),"")

    def POST(self):
        global progress,logfiles,slots,runs,numthreads,maxruns,progress2
        form = formProcessMVA()
        if not form.validates():
            print "wrong"
            return render.mvarun(form,progress, progress2%(0,0,""),"")
        else:

#import sys  # Need to have acces to sys.stdout
#fd = open('foo.txt','w') # open the result file in write mode
#old_stdout = sys.stdout   # store the default system handler to be able to restore it
#sys.stdout = fd # Now your file is used by print as destination 
#print 'bar' # 'bar' is added to your file
#sys.stdout=old_stdout # here we restore the default behavior
#print 'foorbar' # this is printed on the console
#fd.close() # to not forget to close your file

            
            if not web.input().has_key('see_only_status'):
             runs+=int(form["how_many_runs"].value)
             maxruns+=int(form["how_many_runs"].value)
             numthreads=int(form["how_many_threads"].value)
            else:
             logfiles=[]
             progress=[]

#            print int(form["how_many_threads"].value)
#            print web.input().has_key('see_only_status')

            for j in range(int(form["how_many_threads"].value)):
#             print os.path.isfile("mylog"+str(j))
             if web.input().has_key('see_only_status'): 
              logfiles.append("mylog"+str(j))
              progress.append("start processing... "+ logfiles[-1])
             if not os.path.isfile("mylog"+str(j)) and not  web.input().has_key('see_only_status'):        
#              print "mylog"+str(j)
              logfiles.append("mylog"+str(j))
              os.system("nohup ./prepare_mva.py --run >& " + logfiles[-1]+ " &")
              time.sleep(5)               
              progress.append("start processing... "+ logfiles[-1])

#            print progress
#            print logfiles

            refresh="help: if nothing happens,please, checked \" see_only_status first\" "
            if (int(form["Look_at_log"].value)>-1) and web.input().has_key('see_only_status'):
             refresh="""
             <script type = "text/javascript" >
             window.open('/refresh?file=%s', '_blank', '');
             </script>
             """ % ( "mylog" + form["Look_at_log"].value )
             """ """
            return render.mvarun(form,progress,progress2%(0,0,''),refresh)


############ index:


class index: 
    def GET(self): 
        form = formMVAControl()
        # make sure you create a copy of the form by calling it (line above)
        # Otherwise changes will appear globally
        return render.formtest(form)

    def POST(self): 
        form = formMVAControl() 
        if not form.validates(): 
            return render.formtest(form)
        else:
            # form.d.boe and form['boe'].value are equivalent ways of
            # extracting the validated arguments from the form.

#            return """
#     		<img alt=\"plots/overtrain_BDT_746039.png\" src=\"plots/overtrain_BDT_746039.png\">
#			Crrreat success! boe: %s, bax: %s
#			"""  % (form.d.boe, form['bax'].value)
#	        return render.myplot()
#            return " Crrreat success! boe: %s, bax: %s "% (form.d.boe, form['bax'].value)
             raise web.seeother('/image?type=%s&ID=%s&MVA=%s'%(web.input().type,str(web.input().ID),web.input().MVA))




if __name__=="__main__":
    web.internalerror = web.debugerror
    app.run()


