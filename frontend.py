import streamlit as st
import requests
import json
import os
# FastAPI 后端地址
BACKEND_URL = "http://localhost:8000"

def main():
    st.set_page_config(page_title="AI简历分析系统", page_icon=":robot:")
    st.title("🤖 AI简历分析系统")
    # 侧边栏功能选择
    st.sidebar.header("功能选择")
    app_mode = st.sidebar.selectbox(
        "请选择功能",
        ["简历上传", "简历分析", "职位匹配"]
    )
    if app_mode == "简历上传":
        resume_upload_page()
    elif app_mode == "简历分析":
        resume_analysis_page()
    elif app_mode == "职位匹配":
        job_match_page()

def resume_upload_page():
    st.header("📤 简历上传")
    uploaded_file = st.file_uploader("选择PDF简历", type=["pdf"])
    if uploaded_file is not None:
        # 准备上传文件
        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
        try:
            # 调用后端上传接口
            response = requests.post(f"{BACKEND_URL}/upload/resume", files=files)
            response.raise_for_status()  # 检查是否有错误
            # 解析响应
            result = response.json()
            # 展示结果
            st.success("简历上传成功!")
            st.json(result.get("resume_info", {}))
            # 在会话中保存简历信息
            st.session_state['resume_info'] = result.get("resume_info", {})
        except requests.RequestException as e:
            st.error(f"上传失败: {str(e)}")

def resume_analysis_page():
    st.header("🔍 简历分析")
    # 检查是否已上传简历
    if 'resume_info' not in st.session_state:
        st.warning("请先上传简历")
        return
    resume_info = st.session_state['resume_info']
    if st.button("开始分析"):
        try:
            # 调用后端分析接口
            response = requests.post(
                f"{BACKEND_URL}/analyze/resume",
                json=resume_info,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            # 解析响应
            analysis_result = response.json()
            # 展示结果
            st.success("简历分析完成!")
            st.json(analysis_result)
        except requests.RequestException as e:
            st.error(f"分析失败: {str(e)}")

def job_match_page():
    st.header("🤝 职位匹配")
    # 检查是否已上传简历
    if 'resume_info' not in st.session_state:
        st.warning("请先上传简历")
        return

    # 职位描述输入

    job_description = st.text_area("输入职位描述")
    if st.button("开始匹配"):
        if not job_description:
            st.warning("请输入职位描述")
            return

        resume_info = st.session_state['resume_info']
        try:
            # 调用后端匹配接口
            response = requests.post(
                f"{BACKEND_URL}/match/resume",
                json={
                    "resume_info": resume_info,
                    "job_description": {
                        "description":job_description
                    }
                },
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            # 解析响应
            match_result = response.json()
            # 展示结果
            st.success("职位匹配完成!")
            st.json(match_result.get("match_result", {}))
        except requests.RequestException as e:
            st.error(f"匹配失败: {str(e)}")


if __name__ == "__main__":
    main()