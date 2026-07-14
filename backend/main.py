from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import random
import time
import json
import asyncio

app = FastAPI(title="FogTraffic API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Constants ──────────────────────────────────────────────────────────────────
CLASSES = ["轿车", "卡车", "行人", "摩托车", "公交车", "自行车"]
COLORS  = ["#667eea", "#f093fb", "#4facfe", "#43e97b", "#f7971e", "#fa709a"]

# ── In-memory mock DB ──────────────────────────────────────────────────────────
fake_tasks = [
    {"id": 1, "name": "fogtraffic_v1", "model": "YOLOv11n", "scene": "交通",
     "epochs": 100, "progress": 100, "status": "done",
     "mAP50": "0.887", "createTime": "2024-06-01 10:20"},
    {"id": 2, "name": "fogtraffic_v2", "model": "YOLOv11s", "scene": "交通",
     "epochs": 150, "progress": 68,  "status": "running",
     "mAP50": "0.821", "createTime": "2024-06-05 14:30"},
    {"id": 3, "name": "remote_v1",     "model": "YOLOv11m", "scene": "遥感",
     "epochs": 80,  "progress": 100, "status": "done",
     "mAP50": "0.763", "createTime": "2024-06-03 09:00"},
]

fake_records = [
    {
        "id": i + 1,
        "filename": f"image_{str(i+1).zfill(3)}.jpg",
        "scene":    ["交通", "遥感", "工业"][i % 3],
        "model":    ["fogtraffic_v1", "fogtraffic_v2", "remote_v1"][i % 3],
        "total":    random.randint(2, 10),
        "inferTime": f"{random.uniform(0.1, 0.5):.2f}s",
        "time":     f"2024-06-{str(i % 6 + 1).zfill(2)} {str(8 + i % 14).zfill(2)}:00",
    }
    for i in range(30)
]

# ── Pydantic Models ────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class ChatRequest(BaseModel):
    message: str
    has_image: Optional[bool] = False

class CreateTaskRequest(BaseModel):
    name: str
    model: str
    scene: str
    epochs: int
    batch: int
    lr: str
    imgSize: str
    device: str

# ── Auth ───────────────────────────────────────────────────────────────────────
@app.post("/api/auth/login")
async def login(req: LoginRequest):
    if not req.username or not req.password:
        raise HTTPException(status_code=400, detail="用户名和密码不能为空")
    return {
        "token": f"mock-token-{int(time.time())}",
        "user":  {"id": 1, "username": req.username, "role": "admin"}
    }

@app.post("/api/auth/register")
async def register(req: RegisterRequest):
    return {"message": "注册成功", "user": {"username": req.username, "email": req.email}}

# ── Detection ──────────────────────────────────────────────────────────────────
@app.post("/api/detect/single")
async def detect_single(file: UploadFile = File(...)):
    await file.read()
    await asyncio.sleep(0.3)  # simulate inference

    cls_indices = random.sample(range(len(CLASSES)), k=random.randint(1, 3))
    classes = []
    total   = 0
    for ci in cls_indices:
        count = random.randint(1, 5)
        total += count
        classes.append({
            "name":  CLASSES[ci],
            "count": count,
            "color": COLORS[ci],
            "pct":   0
        })
    for c in classes:
        c["pct"] = round(c["count"] / total * 100)

    return {
        "success":   True,
        "filename":  file.filename,
        "total":     total,
        "classes":   classes,
        "inferTime": f"{random.uniform(0.1, 0.45):.2f}s",
        "model":     "fogtraffic_v1",
        "imgSize":   "640x640"
    }

@app.post("/api/detect/batch")
async def detect_batch(files: List[UploadFile] = File(...)):
    results = []
    for f in files:
        await f.read()
        cls_indices = random.sample(range(len(CLASSES)), k=random.randint(1, 2))
        classes = [{"name": CLASSES[ci], "count": random.randint(1, 4),
                    "color": COLORS[ci]} for ci in cls_indices]
        total = sum(c["count"] for c in classes)
        results.append({
            "filename":  f.filename,
            "total":     total,
            "classes":   classes,
            "inferTime": f"{random.uniform(0.1, 0.45):.2f}s",
        })
    return {"success": True, "count": len(results), "results": results}

# ── Chat (SSE streaming) ───────────────────────────────────────────────────────
@app.post("/api/chat")
async def chat(req: ChatRequest):
    async def generate():
        if req.has_image:
            # Tool call phase
            tool_start = {"type": "tool_call", "status": "running",
                          "text": "正在调用 YOLO 检测工具..."}
            yield f"data: {json.dumps(tool_start, ensure_ascii=False)}\n\n"
            await asyncio.sleep(1.5)

            tool_done = {"type": "tool_call", "status": "done"}
            yield f"data: {json.dumps(tool_done, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.3)

            # Result
            cls_indices = random.sample(range(len(CLASSES)), k=random.randint(1, 3))
            classes = []
            total   = 0
            for ci in cls_indices:
                count = random.randint(1, 5)
                total += count
                classes.append({"name": CLASSES[ci], "count": count,
                                 "color": COLORS[ci], "pct": 0})
            for c in classes:
                c["pct"] = round(c["count"] / total * 100)

            result_event = {
                "type":    "result",
                "total":   total,
                "classes": classes,
                "time":    f"{random.uniform(0.1, 0.45):.2f}s"
            }
            yield f"data: {json.dumps(result_event, ensure_ascii=False)}\n\n"

            reply = f"检测完成！共识别到 **{total} 个交通目标**，详情见结果卡片。"
        else:
            replies = [
                "您好！请上传交通场景图片，我将调用 YOLO 引擎为您进行目标检测分析。",
                "收到您的消息！您可以点击上方「单图检测」按钮上传图片开始检测。",
                "好的，FogTraffic 支持车辆、行人、交通标志等多类目标检测，请上传图片。",
            ]
            reply = random.choice(replies)

        # Stream text character by character
        for char in reply:
            text_event = {"type": "text", "char": char}
            yield f"data: {json.dumps(text_event, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.025)

        yield "data: {\"type\": \"done\"}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache",
                                      "X-Accel-Buffering": "no"})

# ── Training Tasks ─────────────────────────────────────────────────────────────
@app.get("/api/training/tasks")
async def get_tasks():
    return {"tasks": fake_tasks}

@app.post("/api/training/tasks")
async def create_task(req: CreateTaskRequest):
    new_task = {
        "id":         len(fake_tasks) + 1,
        "name":       req.name,
        "model":      req.model,
        "scene":      {"traffic": "交通", "remote": "遥感", "industry": "工业"}.get(req.scene, req.scene),
        "epochs":     req.epochs,
        "progress":   0,
        "status":     "queued",
        "mAP50":      "—",
        "createTime": time.strftime("%Y-%m-%d %H:%M")
    }
    fake_tasks.insert(0, new_task)
    return {"success": True, "task": new_task}

@app.put("/api/training/tasks/{task_id}/stop")
async def stop_task(task_id: int):
    for t in fake_tasks:
        if t["id"] == task_id:
            t["status"] = "failed"
            return {"success": True}
    raise HTTPException(status_code=404, detail="任务不存在")

@app.get("/api/training/tasks/{task_id}/metrics")
async def get_metrics(task_id: int):
    epochs = list(range(1, 21))
    return {
        "epochs": epochs,
        "box_loss": [round(1.8 - i * 0.08 + random.uniform(-0.02, 0.02), 3) for i in range(20)],
        "cls_loss": [round(1.2 - i * 0.05 + random.uniform(-0.015, 0.015), 3) for i in range(20)],
        "dfl_loss": [round(0.9 - i * 0.03 + random.uniform(-0.01, 0.01), 3) for i in range(20)],
        "mAP50":    [round(min(0.3 + i * 0.03 + random.uniform(0, 0.01), 0.95), 3) for i in range(20)],
        "mAP5095":  [round(min(0.2 + i * 0.022 + random.uniform(0, 0.008), 0.80), 3) for i in range(20)],
    }

# ── History ────────────────────────────────────────────────────────────────────
@app.get("/api/history")
async def get_history(page: int = 1, page_size: int = 20,
                      scene: str = "", model: str = "", search: str = ""):
    data = fake_records
    if scene:  data = [r for r in data if r["scene"]  == scene]
    if model:  data = [r for r in data if r["model"]  == model]
    if search: data = [r for r in data if search in r["filename"]]
    start = (page - 1) * page_size
    return {
        "total":   len(data),
        "records": data[start: start + page_size]
    }

@app.delete("/api/history/{record_id}")
async def delete_record(record_id: int):
    global fake_records
    fake_records = [r for r in fake_records if r["id"] != record_id]
    return {"success": True}

# ── Dashboard ──────────────────────────────────────────────────────────────────
@app.get("/api/dashboard/stats")
async def get_stats():
    return {
        "totalDetections": 12847,
        "todayDetections": 236,
        "availableModels": 6,
        "avgConfidence":   0.873,
        "weeklyTrend": {
            "dates":    ["06-01", "06-02", "06-03", "06-04", "06-05", "06-06", "06-07"],
            "traffic":  [120, 180, 150, 200, 170, 236, 190],
            "remote":   [30, 45, 38, 52, 41, 60, 55],
            "industry": [15, 22, 18, 28, 20, 32, 25],
        },
        "classDistribution": [
            {"name": "轿车",   "value": 5200, "color": "#667eea"},
            {"name": "卡车",   "value": 2800, "color": "#f093fb"},
            {"name": "行人",   "value": 2100, "color": "#4facfe"},
            {"name": "摩托车", "value": 1400, "color": "#43e97b"},
            {"name": "公交车", "value": 900,  "color": "#f7971e"},
        ],
        "modelUsage": [
            {"name": "fogtraffic_v1", "pct": 45, "count": 5781, "color": "#667eea"},
            {"name": "fogtraffic_v2", "pct": 30, "count": 3854, "color": "#f093fb"},
            {"name": "remote_v1",     "pct": 15, "count": 1927, "color": "#4facfe"},
            {"name": "industry_v1",   "pct": 10, "count": 1285, "color": "#43e97b"},
        ]
    }

# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0.0", "time": time.strftime("%Y-%m-%d %H:%M:%S")}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
