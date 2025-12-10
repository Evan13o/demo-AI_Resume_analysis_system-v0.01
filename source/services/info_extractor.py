import re
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
from typing import Dict, List, Any

class ResumeInfoExtractor:
    def __init__(self, model_path="source/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        初始化NER模型
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # 后续采用文本模型进行提取，目前修改中
        if not model_path:
            model_path = "source/paraphrase-multilingual-MiniLM-L12-v2"
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForTokenClassification.from_pretrained(model_path).to(self.device)

        # 自定义实体类型
        self.entity_types = {
            'NAME': r'([\u4e00-\u9fa5]{2,4})',
            'PHONE': r'(1[3-9]\d{9})',
            'EMAIL': r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            'EDUCATION': r'(大专|本科|硕士|博士|研究生)',
            'WORK_YEAR': r'(\d{1,2})年工作经验'
        }

    def extract_basic_info(self, text: str) -> Dict[str, Any]:
        """
        提取基本信息
        """
        #确保text是字符串
        if not isinstance(text, str):
            print(f"Invalid text type in extract_basic_info:{type(text)}")
            text = str(text)
        if not text:
            return {
                'name':None,
                'phone':None,
                'email':None
            }
        info = {}
        try:
            # 姓名提取
            name_match = re.search(self.entity_types['NAME'], text)
            info['name'] = name_match.group(1) if name_match else None

            # 电话提取
            phone_match = re.search(self.entity_types['PHONE'], text)
            info['phone'] = phone_match.group(1) if phone_match else None

            # 邮箱提取
            email_match = re.search(self.entity_types['EMAIL'], text)
            info['email'] = email_match.group(1) if email_match else None
        except Exception as e:
            print(f"Error in extract_basic_info:{e}")
            info = {
                'name':None,
                'phone':None,
                'email':None
            }
        return info

    def extract_education_info(self, text: str) -> Dict[str, Any]:
        """
        提取教育背景信息
        """
        edu_info = {}
        # 学历提取
        edu_match = re.search(self.entity_types['EDUCATION'], text)
        edu_info['education_level'] = edu_match.group(1) if edu_match else None

        # 学校和专业正则(示例)
        school_pattern = r'([\u4e00-\u9fa5]+(?:大学|学院|学校))'
        major_pattern = r'([\u4e00-\u9fa5]+(?:专业|系))'
        school_match = re.search(school_pattern, text)
        major_match = re.search(major_pattern, text)
        edu_info['school'] = school_match.group(1) if school_match else None
        edu_info['major'] = major_match.group(1) if major_match else None

        return edu_info

    def extract_work_experience(self, text: str) -> List[Dict[str, Any]]:
        """
        提取工作经历
        """

        # 工作经验年限提取
        work_year_match = re.search(self.entity_types['WORK_YEAR'], text)
        work_years = int(work_year_match.group(1)) if work_year_match else 0

        # 公司和职位提取
        company_pattern = r'([\u4e00-\u9fa5]+(?:公司|集团|企业))'
        position_pattern = r'([\u4e00-\u9fa5]+(?:工程师|经理|总监|专员))'
        companies = re.findall(company_pattern, text)
        positions = re.findall(position_pattern, text)
        work_experiences = []

        for i in range(min(len(companies), len(positions))):
            work_experiences.append({
                'company': companies[i],
                'position': positions[i]
            })
        return {
            'total_work_years': work_years,
            'work_experiences': work_experiences
        }

    def extract_skills(self, text: str, top_n: int = 5) -> List[str]:
        """
        技能关键词提取
        """

        # 技能关键词库
        skill_keywords = [
            'Python', 'Java', 'C++', 'JavaScript', 'React', 'Vue',
            '机器学习', '数据分析', '深度学习', 'Docker', 'Kubernetes'
        ]

        # 从文本中找出匹配的技能
        skills = [skill for skill in skill_keywords if skill in text]
        return skills[:top_n]

    def extract_full_resume_info(self, text: str) -> Dict[str, Any]:
        """
        综合信息提取
        """
        # 确保text是字符串
        if not isinstance(text, str):
            print(f"Invalid text type in extract_basic_info:{type(text)}")
            text = str(text)
        if not text:
            return {
                'basic_info':{},
                'education_info':{},
                'work_experience':{},
                'skills':[]
            }
        try:
            return {
                'basic_info': self.extract_basic_info(text),
                'education_info': self.extract_education_info(text),
                'work_experience': self.extract_work_experience(text),
                'skills': self.extract_skills(text)
            }
        except Exception as e:
            print(f"Error in extract_full_resume_info:{e}")
            return {
                'basic_info': {},
                'education_info': {},
                'work_experience': {},
                'skills': []
            }


def process_resume(text: str)->Dict[str,Any]:
    #如果resume_info已经是提取后的字典，直接返回
    if all(key in text for key in ['basic_info','education_info','work_experience','skills']):
        return text

    if not text or not isinstance(text,str):
        print(f"Invalid text input:{text}")
        return {
            'basic_info':{},
            'education_info':{},
            'work_experience':{},
            'skills':[]
        }

    try:
        extractor = ResumeInfoExtractor()
        return extractor.extract_full_resume_info(text)
    except Exception as e:
        print(f"Error in processing resume:{e}")
        return {
            'basic_info': {},
            'education_info': {},
            'work_experience': {},
            'skills': []
        }
