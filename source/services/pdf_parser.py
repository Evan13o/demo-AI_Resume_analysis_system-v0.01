import fitz
from typing import List

from source.utils.text_cleaner import process_resume_text


class PDFParser:
    @staticmethod
    def extract_text(file_path:str) -> str:
        """
        从PDF文件提取全文本内容
        :param file_path: PDF文本路径
        :return: 提取的文本内容
        """
        try:
            doc = fitz.open(file_path)
            full_text = ""
            for page in doc:
                text = page.get_text()
                processed_text = process_resume_text(text)
                full_text += processed_text
            return full_text
        except Exception as e:
            print(f"PDF解析错误：{e}")
            return ""
        finally:
            doc.close() if 'doc' in locals() else None
