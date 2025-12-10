import numpy as np
from typing import Dict, List, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import jieba

class ResumeMatcher:
    def __init__(self):
        """
        初始化简历匹配器
        """
        self.tfidf_vectorizer = TfidfVectorizer()

    def preprocess_text(self, text: str) -> str:
        """
        文本预处理
        """
        # 分词
        words = list(jieba.cut(text))
        return ' '.join(words)

    def calculate_skill_match_score(self,
                                    resume_skills: List[str],
                                    job_skills: List[str]) -> float:
        """
        技能匹配度计算
        :param resume_skills: 简历技能列表
        :param job_skills: 职位要求技能列表
        :return: 匹配分数 (0-1)
        """

        # 技能权重映射
        skill_weights = {
            'Python': 1.5,
            'Java': 1.4,
            'machine learning': 1.6,
            'data analysis': 1.5,
            'AI': 1.7,
            'backend': 1.4,
            'frontend': 1.3
        }

        #如果职位没有技能要求，返回0
        if not job_skills:
            return 0.0

        # 技能交集
        matched_skills = set(resume_skills) & set(job_skills)
        # 计算加权匹配度
        total_weight = sum(skill_weights.get(skill.lower(), 1.0) for skill in matched_skills)
        total_job_weight = sum(skill_weights.get(skill.lower(), 1.0) for skill in job_skills)
        return min(total_weight / total_job_weight, 1.0)

    def calculate_experience_match_score(self,
                                         resume_years: int,
                                         job_min_years: int) -> float:
        """
        工作经验匹配度计算
        :param resume_years: 简历工作年限
        :param job_min_years: 职位最低工作年限要求
        :return: 匹配分数 (0-1)
        """

        if resume_years >= job_min_years:
            # 超过最低要求,满分
            return 1.0
        elif resume_years > 0:
            # 部分匹配
            return resume_years / job_min_years
        else:
            return 0.0

    def calculate_semantic_similarity(self,
                                      resume_text: str,
                                      job_description: str) -> float:
        """
        语义相似度计算
        :param resume_text: 简历文本
        :param job_description: 职位描述
        :return: 语义相似度分数 (0-1)
        """

        # 文本预处理
        processed_resume = self.preprocess_text(resume_text)
        processed_job = self.preprocess_text(job_description)

        # 构建TF-IDF向量
        tfidf_matrix = self.tfidf_vectorizer.fit_transform([processed_resume, processed_job])
        # 计算余弦相似度
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return cosine_sim

    def calculate_comprehensive_match_score(self,
                                            resume_info: Dict[str, Any],
                                            job_requirements: Dict[str, Any]) -> Dict[str, float]:

        """
        综合匹配度计算
        :param resume_info: 简历信息
        :param job_requirements: 职位要求
        :return: 匹配度详细信息
        """

        # 技能匹配度
        skill_match_score = self.calculate_skill_match_score(
            resume_info.get('skills', []),
            job_requirements.get('required_skills', [])
        )

        # 工作经验匹配度
        experience_match_score = self.calculate_experience_match_score(
            resume_info.get('work_experience', {}).get('total_work_years', 0),
            job_requirements.get('min_work_years', 0)
        )

        # 语义相似度
        semantic_similarity = self.calculate_semantic_similarity(
            str(resume_info),
            str(job_requirements)
        )

        # 综合评分(可调整权重)
        comprehensive_score = (
                skill_match_score * 0.4 +
                experience_match_score * 0.3 +
                semantic_similarity * 0.3
        )

        return {
            'skill_match_score': skill_match_score,
            'experience_match_score': experience_match_score,
            'semantic_similarity': semantic_similarity,
            'comprehensive_match_score': comprehensive_score
        }


# 使用示例
def match_resume_to_job(resume_info: Dict[str, Any], job_description: Dict[str, Any]):
    """
    简历与职位匹配主函数
    """

    matcher = ResumeMatcher()
    return matcher.calculate_comprehensive_match_score(resume_info, job_description)