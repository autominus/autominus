<template>
  <div class="chat-page">
    <!-- Left: chat history sidebar -->
    <div class="chat-sidebar">
      <div class="cs-head">
        <span>对话列表</span>
        <el-button size="small" type="primary" @click="newChat">
          <el-icon><Plus/></el-icon>新建
        </el-button>
      </div>
      <div class="chat-list">
        <div
          v-for="item in chatHistory"
          :key="item.id"
          class="chat-item"
          :class="{ active: item.id === activeChatId }"
          @click="activeChatId = item.id"
        >
          <el-icon><ChatDotRound/></el-icon>
          <div class="ci-info">
            <span class="ci-title">{{ item.title }}</span>
            <span class="ci-time">{{ item.time }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Right: main chat -->
    <div class="chat-main">
      <!-- Quick action bar -->
      <div class="quick-bar">
        <button class="quick-btn" @click="triggerFile('single')">
          <el-icon><Camera/></el-icon>单图检测
        </button>
        <button class="quick-btn" @click="triggerFile('batch')">
          <el-icon><Files/></el-icon>批量检测
        </button>
        <button class="quick-btn" @click="triggerFile('zip')">
          <el-icon><FolderOpened/></el-icon>ZIP 检测
        </button>
        <button class="quick-btn danger" @click="clearChat">
          <el-icon><Delete/></el-icon>清空对话
        </button>
      </div>

      <!-- Messages -->
      <div class="msg-list" ref="msgListRef">
        <div
          v-for="msg in messages"
          :key="msg.id"
          class="msg-row"
          :class="msg.role"
        >
          <div v-if="msg.role==='assistant'" class="ai-avatar">
            <svg width="24" height="24" viewBox="0 0 30 30" fill="none">
              <rect width="30" height="30" rx="8" fill="url(#avG)"/>
              <circle cx="11" cy="13" r="2.5" fill="white"/>
              <circle cx="19" cy="13" r="2.5" fill="white"/>
              <path d="M10 19.5 Q15 23 20 19.5" stroke="white" stroke-width="1.8" stroke-linecap="round" fill="none"/>
              <defs>
                <linearGradient id="avG" x1="0" y1="0" x2="30" y2="30">
                  <stop stop-color="#667eea"/><stop offset="1" stop-color="#764ba2"/>
                </linearGradient>
              </defs>
            </svg>
          </div>

          <div class="msg-body">
            <!-- Tool call status -->
            <div v-if="msg.toolCall" class="tool-badge" :class="msg.toolCall.status">
              <el-icon v-if="msg.toolCall.status==='running'" class="spin"><Loading/></el-icon>
              <span v-else>✅</span>
              {{ msg.toolCall.status==='running' ? '🔧 正在调用检测工具...' : '检测工具调用完成' }}
            </div>

            <!-- Text bubble -->
            <div class="bubble" :class="msg.role">
              <div class="bubble-text" v-html="renderMd(msg.content)"></div>
              <span class="btime">{{ msg.time }}</span>
            </div>

            <!-- Uploaded image -->
            <div v-if="msg.image" class="msg-img-wrap">
              <img :src="msg.image" alt="上传图片"/>
            </div>

            <!-- Detection result card -->
            <div v-if="msg.result" class="result-card">
              <div class="rc-head">
                <el-icon><PictureFilled/></el-icon>
                <span>检测结果报告</span>
                <el-tag size="small" type="success">共 {{ msg.result.total }} 个目标</el-tag>
              </div>
              <div class="rc-body">
                <div class="rc-img">
                  <img :src="msg.result.image" alt="检测结果"/>
                </div>
                <div class="rc-info">
                  <div class="rc-info-title">目标类别统计</div>
                  <div class="stat-row" v-for="(cls, i) in msg.result.classes" :key="i">
                    <span class="sdot" :style="{ background: cls.color }"></span>
                    <span class="sname">{{ cls.name }}</span>
                    <div class="sbar"><div class="sbar-fill" :style="{ width: cls.pct+'%', background: cls.color }"></div></div>
                    <span class="scnt">{{ cls.count }}</span>
                  </div>
                  <div class="rc-meta">
                    <span>⏱ 推理耗时：{{ msg.result.time }}</span>
                    <span>📐 置信度：≥ 0.50</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Typing -->
        <div v-if="isTyping" class="msg-row assistant">
          <div class="ai-avatar">
            <svg width="24" height="24" viewBox="0 0 30 30" fill="none">
              <rect width="30" height="30" rx="8" fill="url(#avG2)"/>
              <circle cx="11" cy="13" r="2.5" fill="white"/>
              <circle cx="19" cy="13" r="2.5" fill="white"/>
              <defs>
                <linearGradient id="avG2" x1="0" y1="0" x2="30" y2="30">
                  <stop stop-color="#667eea"/><stop offset="1" stop-color="#764ba2"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div class="typing-dots">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <!-- Input area -->
      <div class="input-area">
        <!-- Pending image preview -->
        <div v-if="pendingImage" class="pending-preview">
          <img :src="pendingImage" alt="待发送图片"/>
          <button class="rm-btn" @click="pendingImage=null"><el-icon><Close/></el-icon></button>
          <span class="pending-label">待发送图片</span>
        </div>

        <div class="input-row">
          <!-- Upload button -->
          <button class="attach-btn" @click="triggerFile('single')" title="上传图片">
            <el-icon><Paperclip/></el-icon>
          </button>

          <!-- Text input -->
          <textarea
            v-model="inputText"
            ref="inputRef"
            placeholder="输入消息，或上传图片进行检测... (Shift+Enter 换行)"
            @keydown.enter.exact.prevent="sendMessage"
            rows="1"
            class="chat-input"
          ></textarea>

          <!-- Send -->
          <button class="send-btn" :disabled="!inputText.trim() && !pendingImage" @click="sendMessage">
            <el-icon><Promotion/></el-icon>
          </button>
        </div>

        <p class="input-hint">Enter 发送 · Shift+Enter 换行 · 支持上传图片 / ZIP</p>
      </div>

      <!-- Hidden file inputs -->
      <input ref="fileInputRef" type="file" accept="image/*" style="display:none" @change="onFileChange"/>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

/* ─── State ─── */
const messages    = ref([
  {
    id: 1, role: 'assistant',
    content: '您好！我是 **FogTraffic AI 助手** 🤖\n\n我可以帮您进行交通目标智能检测分析。您可以：\n- 📷 点击上方按钮进行**单图检测**\n- 📦 上传 ZIP 包进行**批量检测**\n- 💬 用**自然语言**描述您的需求\n\n请开始您的检测任务！',
    time: '09:00'
  }
])
const isTyping    = ref(false)
const inputText   = ref('')
const pendingImage = ref(null)
const msgListRef  = ref(null)
const inputRef    = ref(null)
const fileInputRef = ref(null)
const activeChatId = ref(1)

const chatHistory = reactive([
  { id: 1, title: '交通场景检测分析', time: '10:32' },
  { id: 2, title: '雾天能见度评估',   time: '昨天' },
  { id: 3, title: '批量图片检测任务',  time: '昨天' },
  { id: 4, title: '模型性能对比',      time: '3天前' },
])

/* ─── Markdown render ─── */
function renderMd(text) {
  if (!text) return ''
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n- (.*)/g, '<br/>• $1')
    .replace(/\n/g, '<br/>')
}

/* ─── Scroll to bottom ─── */
function scrollBottom() {
  nextTick(() => {
    if (msgListRef.value) {
      msgListRef.value.scrollTop = msgListRef.value.scrollHeight
    }
  })
}

function now() {
  return new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

/* ─── File trigger ─── */
function triggerFile(mode) {
  if (fileInputRef.value) fileInputRef.value.click()
}

function onFileChange(e) {
  const file = e.target.files[0]
  if (!file) return
  const url = URL.createObjectURL(file)
  pendingImage.value = url
  e.target.value = ''
}

/* ─── Send message ─── */
async function sendMessage() {
  const text = inputText.value.trim()
  const img  = pendingImage.value
  if (!text && !img) return

  // Add user message
  messages.value.push({
    id: Date.now(), role: 'user',
    content: text || '请对这张图片进行目标检测',
    image: img || null,
    time: now()
  })
  inputText.value  = ''
  pendingImage.value = null
  scrollBottom()

  // Simulate AI response
  isTyping.value = true
  scrollBottom()

  if (img) {
    // Detection flow
    await delay(600)
    const toolId = Date.now()
    messages.value.push({
      id: toolId, role: 'assistant',
      content: '好的，我已收到您的图片，正在调用 YOLO 检测引擎进行分析...',
      toolCall: { status: 'running' },
      time: now()
    })
    scrollBottom()

    await delay(1800)
    // Update tool status to done
    const toolMsg = messages.value.find(m => m.id === toolId)
    if (toolMsg) toolMsg.toolCall.status = 'done'

    await delay(400)
    isTyping.value = false
    messages.value.push({
      id: Date.now(), role: 'assistant',
      content: '检测完成！共识别到 **6 个交通目标**，详情见下方结果卡片：',
      result: {
        image: img,
        total: 6,
        time: '0.32s',
        classes: [
          { name: '轿车',   count: 3, pct: 50, color: '#667eea' },
          { name: '卡车',   count: 1, pct: 17, color: '#f093fb' },
          { name: '行人',   count: 2, pct: 33, color: '#4facfe' },
        ]
      },
      time: now()
    })
    scrollBottom()
  } else {
    await delay(1500)
    isTyping.value = false
    const replies = [
      '我理解您的需求。您可以点击上方的**「单图检测」**按钮上传图片，我会自动调用 YOLO 引擎进行分析，并给您详细的检测报告。',
      '好的！FogTraffic 支持对交通场景中的**车辆、行人、交通标志**等多类目标进行精确检测。请上传您的图片开始分析。',
      '收到！我可以帮您分析交通图像中的目标分布情况。请通过上方按钮上传图片，或直接拖拽图片到对话框中。',
    ]
    messages.value.push({
      id: Date.now(), role: 'assistant',
      content: replies[Math.floor(Math.random() * replies.length)],
      time: now()
    })
    scrollBottom()
  }
}

function delay(ms) { return new Promise(r => setTimeout(r, ms)) }

function newChat() {
  const id = Date.now()
  chatHistory.unshift({ id, title: '新对话 ' + chatHistory.length, time: '刚刚' })
  activeChatId.value = id
  messages.value = [{
    id: 1, role: 'assistant',
    content: '新对话已创建，请开始您的检测任务！',
    time: now()
  }]
}

function clearChat() {
  messages.value = [{
    id: 1, role: 'assistant',
    content: '对话已清空，请开始新的检测任务。',
    time: now()
  }]
  ElMessage.success('对话已清空')
}
</script>

<style lang="scss" scoped>
.chat-page {
  display: flex;
  height: 100%;
  background: #0f1535;
  overflow: hidden;
}

/* ─── Chat Sidebar ─── */
.chat-sidebar {
  width: 220px;
  flex-shrink: 0;
  border-right: 1px solid rgba(102,126,234,.15);
  display: flex;
  flex-direction: column;
  background: rgba(9,13,40,.5);
}

.cs-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 14px 12px;
  font-size: 13px;
  font-weight: 600;
  color: #94a3b8;
  border-bottom: 1px solid rgba(102,126,234,.1);
}

.chat-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.chat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: all .2s;
  .el-icon { font-size: 14px; color: #94a3b8; flex-shrink: 0; }
  &:hover { background: rgba(102,126,234,.1); }
  &.active {
    background: rgba(102,126,234,.18);
    .el-icon { color: #667eea; }
    .ci-title { color: #e2e8f0; }
  }
}

.ci-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.ci-title {
  font-size: 12.5px;
  color: #94a3b8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.ci-time { font-size: 11px; color: rgba(148,163,184,.5); }

/* ─── Chat Main ─── */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Quick bar */
.quick-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-bottom: 1px solid rgba(102,126,234,.1);
  background: rgba(9,13,40,.3);
}

.quick-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 14px;
  border-radius: 20px;
  border: 1px solid rgba(102,126,234,.3);
  background: rgba(102,126,234,.1);
  color: #94a3b8;
  font-size: 12.5px;
  cursor: pointer;
  transition: all .2s;
  .el-icon { font-size: 13px; }
  &:hover {
    background: rgba(102,126,234,.2);
    color: #e2e8f0;
    border-color: rgba(102,126,234,.5);
  }
  &.danger {
    border-color: rgba(239,68,68,.3);
    background: rgba(239,68,68,.08);
    &:hover { background: rgba(239,68,68,.15); color: #fca5a5; }
  }
}

/* Messages */
.msg-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.msg-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  &.user { flex-direction: row-reverse; }
}

.ai-avatar {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(102,126,234,.15);
}

.msg-body {
  max-width: 72%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tool-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  &.running {
    background: rgba(102,126,234,.15);
    color: #818cf8;
    border: 1px solid rgba(102,126,234,.25);
  }
  &.done {
    background: rgba(52,199,89,.12);
    color: #4ade80;
    border: 1px solid rgba(52,199,89,.2);
  }
  .spin { animation: spin .8s linear infinite; }
}
@keyframes spin { to { transform: rotate(360deg); } }

.bubble {
  padding: 11px 15px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.65;
  &.assistant {
    background: rgba(255,255,255,.07);
    border: 1px solid rgba(102,126,234,.15);
    color: #e2e8f0;
    border-radius: 4px 12px 12px 12px;
  }
  &.user {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: #fff;
    border-radius: 12px 4px 12px 12px;
  }
  :deep(strong) { font-weight: 600; }
  :deep(code) {
    background: rgba(102,126,234,.2);
    padding: 1px 5px;
    border-radius: 4px;
    font-size: 12.5px;
  }
}

.btime {
  display: block;
  font-size: 11px;
  color: rgba(148,163,184,.5);
  margin-top: 5px;
  text-align: right;
}

.msg-img-wrap {
  border-radius: 10px;
  overflow: hidden;
  max-width: 260px;
  border: 1px solid rgba(102,126,234,.2);
  img { width: 100%; display: block; }
}

/* Result card */
.result-card {
  background: rgba(255,255,255,.05);
  border: 1px solid rgba(102,126,234,.2);
  border-radius: 12px;
  overflow: hidden;
  max-width: 480px;
}

.rc-head {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: rgba(102,126,234,.1);
  border-bottom: 1px solid rgba(102,126,234,.15);
  font-size: 13px;
  font-weight: 600;
  color: #e2e8f0;
  .el-icon { color: #667eea; }
}

.rc-body {
  display: flex;
  gap: 14px;
  padding: 12px;
}

.rc-img {
  width: 160px;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
  background: rgba(0,0,0,.2);
  img { width: 100%; height: 120px; object-fit: cover; display: block; }
}

.rc-info { flex: 1; }
.rc-info-title { font-size: 12px; color: #94a3b8; margin-bottom: 8px; font-weight: 500; }

.stat-row {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-bottom: 6px;
  font-size: 12.5px;
}
.sdot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.sname { color: #cbd5e1; min-width: 36px; }
.sbar {
  flex: 1;
  height: 4px;
  background: rgba(255,255,255,.08);
  border-radius: 2px;
  overflow: hidden;
}
.sbar-fill { height: 100%; border-radius: 2px; transition: width .5s ease; }
.scnt { font-weight: 600; color: #e2e8f0; min-width: 20px; text-align: right; }

.rc-meta {
  display: flex;
  flex-direction: column;
  gap: 3px;
  margin-top: 10px;
  font-size: 11px;
  color: rgba(148,163,184,.6);
}

/* Typing dots */
.typing-dots {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
  background: rgba(255,255,255,.07);
  border: 1px solid rgba(102,126,234,.15);
  border-radius: 4px 12px 12px 12px;
  span {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #667eea;
    animation: bounce 1.2s ease-in-out infinite;
    &:nth-child(2) { animation-delay: .2s; }
    &:nth-child(3) { animation-delay: .4s; }
  }
}
@keyframes bounce {
  0%,60%,100% { transform: translateY(0); }
  30%         { transform: translateY(-6px); }
}

/* Input area */
.input-area {
  padding: 12px 16px 14px;
  border-top: 1px solid rgba(102,126,234,.12);
  background: rgba(9,13,40,.4);
}

.pending-preview {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  padding: 6px 10px;
  background: rgba(102,126,234,.1);
  border: 1px solid rgba(102,126,234,.25);
  border-radius: 8px;
  img { width: 50px; height: 50px; border-radius: 6px; object-fit: cover; }
  .pending-label { font-size: 12px; color: #94a3b8; }
}

.rm-btn {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: none;
  background: #ef4444;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  .el-icon { font-size: 10px; }
}

.input-row {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  background: rgba(255,255,255,.06);
  border: 1px solid rgba(102,126,234,.25);
  border-radius: 12px;
  padding: 6px 8px 6px 12px;
  transition: border-color .2s, box-shadow .2s;
  &:focus-within {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102,126,234,.15);
  }
}

.attach-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: rgba(102,126,234,.15);
  color: #94a3b8;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all .2s;
  .el-icon { font-size: 16px; }
  &:hover { background: rgba(102,126,234,.25); color: #667eea; }
}

.chat-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #e2e8f0;
  font-size: 14px;
  font-family: inherit;
  line-height: 1.5;
  resize: none;
  max-height: 120px;
  overflow-y: auto;
  padding: 5px 0;
  &::placeholder { color: rgba(148,163,184,.45); }
}

.send-btn {
  width: 36px;
  height: 36px;
  border-radius: 9px;
  border: none;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all .2s;
  .el-icon { font-size: 17px; }
  &:hover:not(:disabled) { opacity: .85; transform: scale(1.05); }
  &:disabled { opacity: .35; cursor: not-allowed; }
}

.input-hint {
  font-size: 11px;
  color: rgba(148,163,184,.35);
  text-align: center;
  margin-top: 6px;
}
</style>
