"""코드 내 외부 설정/사전 XML파일을 불러올 때 사용하는 모듈

Classes:
    ImportXML
    ERBGrammarXML
    SettingXML
"""
import xml.etree.ElementTree as ET
from util import DataFilter

class ImportXML:
    """XML을 파싱하는 클래스

    Funcitons:
        find_all_tags(tagname,[option_num,parent_tag])
        export_textlist(tags_list)
        export_attriblist(tags_list,[keyword])
    Variables:
        filename
            클래스 호출 당시의 대상 파일명
        xmlroot
            xml 파일의 root값
    """
    def __init__(self,filename):
        self.filename = filename
        self.xmlroot = ET.parse(filename).getroot()

    def find_all_tags(self,tagname,parent_tag=None,option_num=0):
        """tagname, option값, 부모태그 이름을 인자로 받아 하위의 tagname을 가진 tag의 list 반환\n

        option_num:
            0: 하위 요소의 하위 요소 등 모두 포함.
            1: 바로 아래 값만 포함
        """
        find_child_tags = []
        if parent_tag == None:
            parent_tag = self.xmlroot
        if option_num == 0:
            for child_tag in parent_tag.iter(tagname):
                find_child_tags.append(child_tag)
        elif option_num == 1:
            for child_tag in parent_tag.iterfind(tagname):
                find_child_tags.append(child_tag)
        if find_child_tags == []:
            print("아무 값도 찾지 못했습니다.")
        return find_child_tags

    def export_textlist(self,tags_list):
        text_list = []
        for tag in tags_list:
            text_list.append(tag.text)
        return text_list

    def export_attriblist(self,tags_list,keyword=None):
        attrib_list = []
        for tag in tags_list:
            if keyword == None:
                attrib_list.append(tag.attrib)
            else:
                attrib_list.append(tag.attrib[keyword])
        return attrib_list


class ERBGrammarXML(ImportXML):
    # {md문법:ERB문법} 또는 {분류(ex:MASTER):{md문법:ERB문법}}
    def __init__(self,filename='CustomMarkdown.xml'):
        super().__init__(filename)
        self.tags_callname = self.find_all_tags('callname',self.xmlroot.find('callnames'),1)
        self.tags_name = self.find_all_tags('name',self.xmlroot.find('names'),1)
        self.tags_var = self.find_all_tags('var',self.xmlroot.find('vars'),1)

    def znames_dict(self,origin=None,option_num=0):
        # {class,name:{particle:{md:og}}}}
        if option_num in [0,3]: the_list = list(self.tags_callname)+list(self.tags_name)
        elif option_num == 1: the_list = self.tags_callname
        elif option_num == 2: the_list = self.tags_name
        the_dict = {}
        self.zname_comp_dict = {}
        for zname in the_list:
            if zname in list(self.tags_callname): nametag = 'callname'
            elif zname in list(self.tags_name): nametag = 'name'
            else: nametag = None
            if origin == None or zname.attrib['origin'] == origin:
                part_list = self.find_all_tags('particle',zname)
                part_dict = {}
                for particle in part_list:
                    if option_num == 3 and particle.attrib['type'] != 'None': continue
                    md_name = particle.find('mkdn_name').text
                    og_name = particle.find('orig_name').text
                    part_dict[particle.attrib['type']] = {md_name:og_name}
                    self.zname_comp_dict[md_name]=og_name
                the_dict[zname.attrib['class']+','+nametag] = part_dict
            else: continue
        return the_dict

    def vars_dict(self,clas=None):
        # {class:{type:{md:og}}}}
        var_dict = {}
        for var in self.tags_var:
            if clas == None or var.attrib['class'] == clas:
                arg_list = self.find_all_tags('arg',var)
                type_dict = {}
                for arg in arg_list:
                    md_var = arg.find('mkdn_var').text
                    og_var = arg.find('orig_var').text
                    type_dict[arg.attrib['type']] = {md_var:og_var}
                var_dict[var.attrib['class']] = type_dict
            else: continue
        return var_dict

    def crawl_dict(self):
        """f_dict = {'var':vardict,'zname':znamedict} 생성"""
        self.f_dict = {}
        self.v_dict = self.vars_dict()
        self.z_dict = self.znames_dict()
        self.f_dict['var'] = self.v_dict
        self.f_dict['zname'] = self.z_dict
        return self.f_dict

    def classify_dict(self,origin=None,clas=None):
        if origin == None and clas == None:
            print("아무 인자도 입력되지 않았습니다.")
            return None
        elif origin == None and bool(clas):
            return self.vars_dict(clas)
        elif bool(origin) and clas == None:
            return self.znames_dict(origin)
        else:
            v_dict = self.vars_dict(clas)
            z_dict = self.znames_dict(origin)
            clas_dict = {}
            clas_dict.update(z_dict)
            clas_dict.update(v_dict)
            return clas_dict

    def zname_class_list(self,option_num=0):
        callname_classes = self.export_attriblist(self.tags_callname,'class')
        name_classes = self.export_attriblist(self.tags_name,'class')
        merged_list = callname_classes + name_classes
        return merged_list

    def zname_dict_situ(self):
        """상황 명칭 변환용 사전"""
        situ_dict = {}
        class_origin_list = self.export_attriblist(
            self.tags_callname) + self.export_attriblist(self.tags_name)
        for attrib in class_origin_list:
            situ_dict[attrib['class']] = attrib['origin']
        return situ_dict

    def user_dict(self):
        user_dictornary = {}
        userdict_tag = self.xmlroot.find('userdict')
        tags_userdict = self.find_all_tags('element',userdict_tag,1)
        for element in tags_userdict:
            element_cls = element.attrib['class']
            og_word = element.find('orig').text
            mk_word = element.find('mkdn').text
            user_dictornary.update({element_cls:{og_word:mk_word}})
        return user_dictornary


class SettingXML(ImportXML):
    #TODO xml 양식의 세팅값 인식(ex: 기본 디렉토리)
    def __init__(self,filename='EraSetting.xml'):
        super().__init__(filename)
        self.info_tag = self.xmlroot.find('settings').find('information')

    def check_templet(self,era_type):
        templets = self.find_all_tags('temp')
        for temp in templets:
            if temp.attrib['eratype'] == era_type:
                tags = temp.iter()
                templet_dict = {}
                for target in tags:
                    templet_dict[target.tag] = target.text
                return templet_dict

    def show_info(self,info_type):
        info_in_xml = self.info_tag.find(info_type).text
        if info_in_xml == None or info_in_xml.strip() == None:
            info_in_xml = 'N/A'
        return info_in_xml


class VFinderFilterXML(ImportXML):
    #TODO ERBVFinder용 문법 파일 추가
    pass


if __name__ == "__main__":
    pass
