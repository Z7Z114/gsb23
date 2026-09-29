# 水族馆水下声学分析系统

利用水下声学网络进行水族馆动物行为分析和会议纪要生成的全栈系统。

## 功能特性

### 🔊 声学分析
- **声谱图生成**：使用 librosa 对水下录音进行时频分析
- **声源分离**：自动分离动物发声与水泵噪音
- **动物发声检测**：识别和分析海洋动物的发声模式
- **环境噪音评估**：监测水泵等设备的噪音水平

### 🎙️ 会议处理
- **语音转写**：使用 OpenAI Whisper 转写饲养员与兽医的讨论内容
- **说话人识别**：使用 pyannote.audio 识别不同参会人员
- **多语言支持**：支持中文、英文、日文、韩文等多种语言

### 🤖 AI 智能分析
- **健康评估**：基于声学数据和会议讨论生成动物健康报告
- **丰容计划**：自动生成动物丰容方案建议
- **展览调整**：提出展区声学环境优化建议
- **会议纪要**：自动整理结构化的会议记录

### 📧 通知系统
- 自动发送 Markdown 格式邮件
- 支持教育部门和饲养团队分别通知
- HTML 富文本邮件格式

## 技术栈

### 后端
- **FastAPI**：高性能 Python Web 框架
- **librosa**：音频分析和处理（可选）
- **OpenAI Whisper**：语音识别（可选）
- **pyannote.audio**：说话人分离（可选）
- **OpenAI GPT-4**：智能摘要生成（可选）
- **Pandas**：数据处理

### 前端
- **React 18**：用户界面框架
- **Vite**：构建工具
- **Tailwind CSS**：样式框架
- **Chart.js**：图表可视化
- **React Router**：路由管理

## 项目结构

```
aquarium/
├── backend/                    # 后端服务
│   ├── __init__.py
│   ├── main.py                # FastAPI 主服务与全部路由
│   ├── audio_processor.py     # 音频处理模块（可选 DSP）
│   ├── meeting_transcriber.py # 会议转写模块（可选推理）
│   ├── ai_summarizer.py       # AI 摘要模块（可选云端）
│   ├── email_sender.py        # 邮件发送模块
│   ├── pytest.ini
│   └── tests/                 # 冒烟测试（只覆盖顺利路径）
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── pages/             # Dashboard / AudioAnalysis / MeetingProcessor / Reports / ReportViewer
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js           # 开发服务器把 /api 代理到 http://localhost:8000
│   ├── tailwind.config.js
│   └── postcss.config.js
├── requirements.txt            # 轻量依赖（后端能起来、测试能跑）
├── requirements-ml.txt         # 可选重型依赖（装齐才会走真实推理）
├── .env.example
└── README.md
```

## 快速开始

### 1. 环境配置

```bash
cp .env.example .env
# 编辑 .env 填入密钥；全部留空即进入离线分支
```

### 2. 后端服务

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
# 需要真实推理时再装重型依赖（可选）：
# pip install -r requirements-ml.txt

cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API 文档：http://localhost:8000/docs

### 3. 前端应用

```bash
cd frontend
npm install
npm run dev
```

访问：http://localhost:3000

### 4. 运行后端测试

```bash
cd backend
python -m pytest
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/audio/upload` | 上传音频文件 |
| POST | `/api/audio/process` | 处理音频并分析 |
| POST | `/api/meeting/process` | 处理会议音频生成报告 |
| GET | `/api/status/{job_id}` | 查询处理状态 |
| GET | `/api/jobs` | 列出所有任务 |
| GET | `/api/download/{filename}` | 下载 `outputs/` 下的输出文件 |
| GET | `/api/outputs` | 列出所有输出文件 |
| POST | `/api/email/send` | 发送邮件（JSON body） |
| GET | `/api/health` | 健康检查 |

## 使用流程

### 声学数据分析
1. 进入「声学分析」页面
2. 上传水族箱录音文件（支持 .wav, .mp3, .m4a, .flac, .aac, .ogg）
3. 可选：上传同期视频用于同步播放
4. 点击「开始分析」
5. 页面用后端返回的 `spectrogram_data.spectrogram` 绘制声谱图，并展示动物发声与环境噪音分析

### 会议处理
1. 进入「会议处理」页面
2. 上传会议录音文件（必填）与同期水族箱声学数据（可选）
3. 选择动物类型和会议语言
4. 点击「开始处理」
5. 前端每 2 秒轮询 `GET /api/status/{job_id}`，直到 `completed` 或 `failed`
6. 在「报告列表」中查看或下载生成的报告

## 生成的报告内容

1. **会议基本信息**（日期、动物类型、录音时长、参会人员）
2. **声学数据分析摘要**（动物发声统计、环境噪音分析）
3. **会议纪要**（议题摘要、关键决策点、行动项）
4. **动物健康评估**
5. **丰容计划**
6. **展览调整建议**
7. **附录：完整会议转录**

---

## 行为规格（验收标准）

> 下面每一条都是可验收点，也是本次修复的唯一验收标准。请逐条让实现与规格一致，
> 不要只修「已知问题」里举的那几个现象。

### A. 音频接口契约

- **A.1** `POST /api/audio/process` 成功（HTTP 200）时，响应必须同时包含 `duration`、
  `animal_analysis`、`pump_analysis`、`output_file`、`separated_audio` 以及 `spectrogram_data`。
  `spectrogram_data` 必须包含 `spectrogram`（二维数组，行是频率、列是时间）、`times`、
  `frequencies`、`sample_rate` 四个键；前端用 `spectrogram_data.spectrogram` 绘制真实声谱图，
  少任何一个键都算契约不满足。
- **A.2** `POST /api/audio/upload`、`POST /api/audio/process`、`POST /api/meeting/process`
  只接受扩展名属于 `.wav`、`.mp3`、`.m4a`、`.flac`、`.aac`、`.ogg`（大小写不敏感）的音频文件。
  其它扩展名（`.exe`、`.txt`、`.png`、无扩展名等）一律返回 **400**，响应体是 JSON 且含 `detail`；
  不得落盘、不得启动处理。
- **A.3** 请求所依赖的可选组件不可用时，接口必须立即返回 **503**，响应体是 JSON 且含 `detail`
  （说明缺了哪个组件），不得返回 5xx HTML，也不得先接受任务再让它在后台失败。具体地：
  - `POST /api/audio/process` 需要 `audio_processor.available == True`；
  - `POST /api/meeting/process` 需要 `meeting_transcriber.available == True`；
  - `POST /api/meeting/process` 若带上了 `tank_audio`，还需要 `audio_processor.available == True`。

### B. 会议处理任务

- **B.1** `POST /api/meeting/process` 的选项必须从 **multipart 表单字段**读取（与前端
  `MeetingProcessor.jsx` 的 `formData.append(...)` 一致）：`animal_type`、`language`、`send_email`
  传什么就按什么处理。例如表单里选 `language=ja`、`animal_type=鱼类`、
  `send_email=false`，报告就必须按日语转写、欄目写成「鱼类健康评估报告」，且不发邮件。
  三个字段都可以缺省，缺省时使用默认值（`海洋哺乳动物` / `zh` / `true`）。
- **B.2** `POST /api/meeting/process` 返回的 `job_id` 必须全局唯一：同一秒内连续多次提交也要各自
  拿到不同的 id，并且每个 id 通过 `GET /api/status/{job_id}` 都能查到自己那一次任务的状态，
  不得相互覆盖。
- **B.3** `POST /api/meeting/process` 的 `language` 只允许 `zh`、`en`、`ja`、`ko`；`animal_type`
  只允许 `海洋哺乳动物`、`鱼类`、`海洋无脊椎动物`、`两栖动物`、`爬行动物`。取值不在集合内时
  返回 **400** JSON（含 `detail`）。
- **B.4** `GET /api/status/{job_id}` 查询不存在的 id 返回 **404** JSON。
- **B.5** 任务结果里的 `email_sent` 必须如实反映投递结果：只有至少一个收件方投递成功时才为
  `true`；`send_email=false`、邮件服务未配置、或全部投递失败时都必须是 `false`。
  `email_results` 必须逐收件方给出真实的布尔结果，不得回显请求里的开关值。

### C. 报告生成与外部服务

- **C.1** 综合报告「录音时长」必须等于音频真实时长的分钟数（保留一位小数），与模板单位一致。
  例如 120 秒的音频必须显示 `2.0分钟`，不能显示 `120.0分钟`。
- **C.2** 外部服务降级语义：
  - 未配置 `OPENAI_API_KEY`（或未装 openai SDK）属于「服务不可用」，走离线分支：报告照常生成，
    任务以 `completed` 结束，正文里提示未配置。
  - **已经配置** `OPENAI_API_KEY` 但调用抛错，属于「服务可用但失败」：任务必须以 `failed` 结束，
    `message` 里给出错误原因，绝不能把错误文本当成报告正文继续报告成功。

### D. 文件下载与目录安全

- **D.1** `GET /api/download/{filename}` 只能下载 `outputs/` 目录内的文件。任何试图越出该目录的
  `filename`（包含路径分隔符、`..`、绝对路径）都必须被拒绝并返回 **400** 或 **404**，绝不能把
  目录外的文件内容返回。合法文件名正常返回 200 与文件内容；不存在的文件返回 404。

### E. 邮件接口

- **E.1** `POST /api/email/send` 接受 **JSON 请求体**：`recipients`（字符串数组，必填）、
  `subject`（字符串，必填）、`body`（字符串，必填）、`attachments`（字符串数组，可选，
  取 `outputs/` 下的文件名）。字段缺失或类型非法返回 **4xx** JSON；合法请求返回 200，
  并把收件人/主题/正文交给邮件服务。参数必须从请求体读取，不能要求调用方用 query 参数传。
- **E.2** 带附件发信时，最外层 MIME 容器必须是 `multipart/mixed`；正文仍要同时提供
  `text/plain` 与 `text/html` 两个可选部分；每个附件必须是独立的
  `Content-Disposition: attachment` 部分，附件文件名与源文件名逐字一致。

### F. 离线运行与可测试性

- **F.1** 在未安装 librosa / whisper / pyannote / openai 等可选重型依赖、且未配置任何密钥的
  环境里，后端必须仍能 `import` 并启动；不依赖这些组件的接口（`/api/health`、`/api/jobs`、
  `/api/outputs`、`/api/download/*`、`/api/audio/upload`）保持可用。
- **F.2** 各服务通过 `available` 属性声明自身可用性（`AudioProcessor.available`、
  `MeetingTranscriber.available`；未安装对应重型依赖时为 `False`）。注入的替身对象可自行声明
  该属性，接口必须依据被调用服务对象的 `available` 判断是否走离线分支。
- **F.3** 测试中不得真实调用任何外部服务（OpenAI / SMTP / Whisper / pyannote）；
  `AISummarizer.client`、`EmailSender`、`MeetingTranscriber.whisper_model`、`pyannote_pipeline`
  都是可替换的属性，失败路径通过注入会抛异常的假对象来验证。
- **F.4** `backend/tests/` 下的冒烟测试只覆盖顺利路径，必须在修复前后都保持全绿。

---

## 已知问题（现象举例，非完整清单）

最近在真实使用中暴露出一批缺陷，以下是其中一部分现象：

1. 声学分析页面处理完音频后，声谱图区域画出来的不是真实频谱，而是一片随机噪点。
2. 界面提示「邮件已发送至：饲养团队、教育部门」，但收件方其实一封都没收到（邮件服务根本没配）。
3. 同一位同事在同一分钟内连续提交两次会议，报告列表里只剩一条状态，另一条不见了。
4. 一段 120 秒的会议录音，报告开头却写成「录音时长: 120.0分钟」。
5. 有同事把 `demo.txt` 和一张 `logo.png` 误当成音频上传，系统照单全收并开始处理。
6. 有同事在会议处理页选了「鱼类」和「日本语」，生成的报告却还是按「海洋哺乳动物」
   和中文写的；取消勾选「发送邮件通知相关部门」后也一样会发邮件。
7. 运维同事从报告里点「下载」，发现 `GET /api/download/` 后面拼上一些奇怪的路径，居然能把
   服务器上 `outputs/` 目录以外的文件内容读出来。

以上只举了几个例子。验收标准是上面的「行为规格」，请按规格逐条对齐实现。

## 许可证

MIT License
