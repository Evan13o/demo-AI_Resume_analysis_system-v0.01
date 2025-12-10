import re
import unicodedata
import jieba #中文分词
import string

class TextCleaner:
    @staticmethod
    def clean_text(text:str)->str:
        """
        文本清洗主方法
        清洗步骤：
        1.统一编码
        2.去除特殊字符
        3.标准化空白
        4.繁简转换
        5.去除无意义字符
        """
        if not text:
            return ""

        #统一编码和标准化
        text = unicodedata.normalize('NFKC',text)
        # 去除特殊符号和无效字符
        text = re.sub(r'[®™©◆△▲◇○●\u2002-\u200f\u2028-\u202f]', '', text)
        # 去除多余空白
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @staticmethod
    def remove_email_and_phone(text: str) -> str:
        """
        移除敏感信息
        """
        # 邮箱正则
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        # 电话号码正则
        phone_pattern = r'(13[0-9]|14[01456879]|15[0-35-9]|16[2567]|17[0-8]|18[0-9]|19[0-35-9])\d{8}'
        text = re.sub(email_pattern, '[EMAIL]', text)
        text = re.sub(phone_pattern, '[PHONE]', text)
        return text

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """
        标准化空白字符
        """
        return ' '.join(text.split())

    @staticmethod
    def remove_punctuation(text: str, keep_chinese_punctuation: bool = True) -> str:
        """
        去除标点符号
        :param text: 输入文本
        :param keep_chinese_punctuation: 是否保留中文标点
        :return: 处理后文本
        """

        if keep_chinese_punctuation:
            # 仅去除英文标点
            punct_set = string.punctuation
            return ''.join(char for char in text if char not in punct_set)
        else:
            # 去除所有标点
            return re.sub(r'[^\w\s]', '', text)

    @staticmethod
    def segment_text(text: str, use_jieba: bool = True) -> list:
        """
        文本分词
        :param text: 输入文本
        :param use_jieba: 是否使用结巴分词
        :return: 分词结果
        """
        if use_jieba:
            return list(jieba.cut(text))
        else:
            return text.split()

    @staticmethod
    def remove_stopwords(words: list, language: str = 'zh') -> list:
        """
        去除停用词
        :param words: 分词列表
        :param language: 语言(zh/en)
        :return: 去除停用词后的列表
        """
        stopwords = set()
        # 中文停用词
        if language == 'zh':
            stopwords = {
                '的', '了', '和', '是', '就', '都', '而', '及', '与',
                '很', '可以', '因为', '但是', '所以', '并', '或者'
            }

        # 英文停用词
        elif language == 'en':
            stopwords = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
                'to', 'for', 'of', 'with', 'by', 'from', 'up', 'down'
            }
        return [word for word in words if word not in stopwords]


# 使用示例
def process_resume_text(raw_text: str) -> str:
    """
    简历文本处理流程
    """
    # 清洗文本
    cleaned_text = TextCleaner.clean_text(raw_text)
    # 移除敏感信息
    safe_text = TextCleaner.remove_email_and_phone(cleaned_text)
    # 分词
    words = TextCleaner.segment_text(safe_text)
    # 去除停用词
    filtered_words = TextCleaner.remove_stopwords(words)
    return safe_text