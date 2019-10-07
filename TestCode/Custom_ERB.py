# ERB 관련 모듈
from Custom_Main import LoadFile
from Custom_CSV import CSVLoad
class ERBLoad(LoadFile):
    def MakeERBList(self):
        with self.readonly() as Origin_ERB:
            self.ERB_Context_List = []
            ERB_Context = Origin_ERB.readline()
            self.ERB_Context_List.append(ERB_Context)
            return self.ERB_Context_List
    def SearchLine(self,Target):
        self.MakeERBList()
        self.List_Target = []
        for line in self.ERB_Context_List:
            if Target in line:
                self.List_Comment.append(line)
        return self.List_Target
    def SearchFunc(self,Func):
        self.MakeERBList()
        FncList = CSVLoad('CSVfnclist.csv').InfoCSV()
        if Func in FncList:
            pass
class ERBWrite(LoadFile):
    def ExportToERB(self):
        self.ExpERB = open('trans_{0}.erb'.format(self.NameDir),'w',encoding=self.EncodType,newline='')
    def TransERB(self):
        self.ExportToERB()
        with self.readonly() as Origin_TXT:
            TXT_Context_List = []
            TXT_Context = Origin_TXT.readline()
            TXT_Context_List.append(TXT_Context)
        for line in TXT_Context_List:
            pass
        self.ExpERB.close()