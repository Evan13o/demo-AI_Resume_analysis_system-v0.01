from typing import Dict, Any

from fastapi import FastAPI,File,UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from source.services.pdf_parser import PDFParser
from source.services.cache_service import cache_service
from source.services.info_extractor import process_resume
from source.services.resume_analysis import perform_resume_analysis
from source.services.resume_matcher import match_resume_to_job

app = FastAPI(title="AI简历分析系统")

#配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload/resume")
async def upload_resume(file:UploadFile = File(...)):
    """
    简历上传接口
    """
    #创建临时存储目录
    os.makedirs("temp",exist_ok=True)

    #保存上传文件
    file_location = f"temp/{file.filename}"
    with open(file_location,"wb+") as file_object:
        file_object.write(await file.read())

    #解析PDF
    text = PDFParser.extract_text(file_location)

    #信息提取
    resume_info = process_resume(text)

    #删除临时文件
    os.remove(file_location)

    return {
        "filename":file.filename,
        "resume_info":resume_info
    }

@app.post("/analyze/resume")
async def match_resume(resume_info:Dict[str,Any]):
    try:
        #详细调试信息
        print("Resume Info Type:",type(resume_info))
        print("Resume Info Keys:",resume_info.keys())
        #检查缓存
        cached_result = cache_service.get_cached_resume_analysis(resume_info)
        if cached_result:
            return cached_result
        #执行分析
        analysis_result = perform_resume_analysis(resume_info)

        #缓存结果
        await cache_service.cache_resume_analysis(resume_info,analysis_result)

        return analysis_result
    except Exception as e:
        print(f"Resume analysis error:{e}")
        return{
            "error":"简历分析失败",
            "details":str(e),
            "input_type":str(type(resume_info)),
            "input_keys":list(resume_info.keys()) if isinstance(resume_info,dict) else None
        }

@app.post("/match/resume")
async def match_resume( resume_info:Dict[str,Any],job_description:Dict[str,Any]):
    if isinstance(job_description,str):
        job_description = {
            "job_description":job_description
        }
    cached_result = cache_service.get_cached_resume_match(resume_info,job_description)
    if cached_result:
        return cached_result

    #执行匹配
    match_result = match_resume_to_job(resume_info,job_description)

    #缓存结果
    await cache_service.cache_resume_match_result(resume_info,job_description,match_result)
    print("Resume Info:",resume_info)
    print("Job Description:",job_description)
    return  {
        "match_result":match_result
    }



if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000)) 
    uvicorn.run(app, host="0.0.0.0", port=port)
