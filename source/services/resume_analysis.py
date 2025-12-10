from typing import Dict, Any, List

from source.services.info_extractor import process_resume

from source.services.resume_matcher import match_resume_to_job


def perform_resume_analysis(resume_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    综合简历分析函数
    :param resume_info: 简历信息
    :return: 分析结果
    """

    # 1. 信息提取
    extracted_info = process_resume(resume_info)

    # 2. 技能分析
    skills = extracted_info.get('skills', [])
    skill_analysis = {
        'total_skills': len(skills),
        'top_skills': skills[:5],  # 取前5个技能
        'skill_diversity_score': _calculate_skill_diversity(skills)
    }

    # 3. 工作经验分析
    work_experience = extracted_info.get('work_experience', {})
    exp_analysis = {
        'total_years': work_experience.get('total_work_years', 0),
        'companies': [exp.get('company', '') for exp in work_experience.get('work_experiences', [])],
        'experience_depth_score': _calculate_experience_depth(work_experience)
    }

    # 4. 教育背景分析
    education_info = extracted_info.get('education_info', {})
    edu_analysis = {
        'education_level': education_info.get('education_level'),
        'school': education_info.get('school'),
        'major': education_info.get('major'),
        'education_quality_score': _calculate_education_quality(education_info)
    }

    # 5. 综合评分
    comprehensive_score = _calculate_comprehensive_score(
        skill_analysis,
        exp_analysis,
        edu_analysis
    )

    return {
        'basic_info': extracted_info.get('basic_info', {}),
        'skill_analysis': skill_analysis,
        'work_experience_analysis': exp_analysis,
        'education_analysis': edu_analysis,
        'comprehensive_score': comprehensive_score
    }


def _calculate_skill_diversity(skills: List[str]) -> float:
    """
    计算技能多样性得分
    :param skills: 技能列表
    :return: 技能多样性得分 (0-1)
    """

    # 技能权重映射
    skill_categories = {
        'programming': ['Python', 'Java', 'C++', 'JavaScript', 'Go'],
        'data_science': ['Machine Learning', 'Data Analysis', 'AI', 'Statistics'],
        'cloud': ['Docker', 'Kubernetes', 'AWS', 'Azure'],
        'web_frontend': ['React', 'Vue', 'Angular', 'HTML', 'CSS'],
        'web_backend': ['Node.js', 'Django', 'Flask', 'Spring']
    }

    # 计算跨类别技能数
    category_count = sum(
        1 for category in skill_categories.values()
        if any(skill in category for skill in skills)
    )

    # 标准化得分
    return min(category_count / len(skill_categories), 1.0)


def _calculate_experience_depth(work_experience: Dict) -> float:
    """
    计算工作经验深度得分
    :param work_experience: 工作经验信息
    :return: 经验深度得分 (0-1)
    """

    total_years = work_experience.get('total_work_years', 0)
    experiences = work_experience.get('work_experiences', [])

    # 不同公司工作经验的多样性
    unique_companies = len(set(exp.get('company', '') for exp in experiences))

    # 综合评分
    years_factor = min(total_years / 10, 1.0)  # 最多10年满分
    company_diversity = min(unique_companies / 3, 1.0)  # 最多3家公司满分
    return (years_factor * 0.7 + company_diversity * 0.3)


def _calculate_education_quality(education_info: Dict) -> float:
    """
    计算教育背景质量得分
    :param education_info: 教育信息
    :return: 教育质量得分 (0-1)
    """

    # 教育层次权重
    education_level_weights = {
        '专科': 0.6,
        '本科': 0.8,
        '硕士': 0.9,
        '博士': 1.0
    }

    # 知名高校映射
    top_universities = [
        '清华大学', '北京大学', '浙江大学', '复旦大学',
        '中国科学技术大学', '上海交通大学','沈阳航空航天大学'
    ]

    level_score = education_level_weights.get(
        education_info.get('education_level', '本科'),
        0.8
    )

    school_bonus = 1.1 if education_info.get('school') in top_universities else 1.0
    return min(level_score * school_bonus, 1.0)


def _calculate_comprehensive_score(
        skill_analysis: Dict,
        exp_analysis: Dict,
        edu_analysis: Dict

) -> float:
    """
    计算综合得分
    """

    skill_weight = skill_analysis.get('skill_diversity_score', 0.7)
    exp_weight = exp_analysis.get('experience_depth_score', 0.6)
    edu_weight = edu_analysis.get('education_quality_score', 0.7)

    # 加权计算
    comprehensive_score = (
            skill_weight * 0.4 +
            exp_weight * 0.3 +
            edu_weight * 0.3
    )

    return round(comprehensive_score, 2)