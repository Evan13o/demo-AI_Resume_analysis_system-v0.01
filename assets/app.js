const api = axios.create({
  baseURL: 'https://fastapi-service-api-ajqdejroyv.cn-hangzhou.fcapp.run',
  withCredentials: true
})

// 工具函数
async function mock(data) {
  return new Promise(resolve => setTimeout(() => resolve(data), MOCK_DELAY));
}

export async function uploadResume(file) {
  if (!BACKEND) return mock({ resume_info: { name: file.name, size: file.size } });
  const fd = new FormData();
  fd.append('file', file);
  const res = await fetch(`${BACKEND}/upload/resume`, { method: 'POST', body: fd });
  return res.json();
}

export async function analyzeResume(info) {
  if (!BACKEND) return mock({ score: 92, keywords: ['Python', 'Streamlit', 'FastAPI'] });
  const res = await fetch(`${BACKEND}/analyze/resume`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(info)
  });
  return res.json();
}

export async function matchJob(info, jd) {
  if (!BACKEND) return mock({ match_result: { percent: 87, missing: ['Docker', 'K8s'] } });
  const res = await fetch(`${BACKEND}/match/resume`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resume_info: info, job_description: { description: jd } })
  });
  return res.json();
}

// 页面切换
window.show = function (id) {
  document.querySelectorAll('section.page').forEach(sec => sec.style.display = 'none');
  document.getElementById(id).style.display = 'block';
};

// 上传
window.doUpload = async () => {
  const file = document.getElementById('fileInput').files[0];
  if (!file) return alert('请选择文件');
  const json = await uploadResume(file);
  document.getElementById('uploadResult').textContent = JSON.stringify(json, null, 2);
  localStorage.setItem('resume', JSON.stringify(json.resume_info));
};

// 分析
window.doAnalysis = async () => {
  const info = JSON.parse(localStorage.getItem('resume') || 'null');
  if (!info) return alert('请先上传简历');
  const result = await analyzeResume(info);
  document.getElementById('analysisResult').textContent = JSON.stringify(result, null, 2);
};

// 匹配
window.doMatch = async () => {
  const info = JSON.parse(localStorage.getItem('resume') || 'null');
  if (!info) return alert('请先上传简历');
  const jd = document.getElementById('jobDesc').value.trim();
  if (!jd) return alert('请输入职位描述');
  const result = await matchJob(info, jd);
  document.getElementById('matchResult').textContent = JSON.stringify(result, null, 2);
};