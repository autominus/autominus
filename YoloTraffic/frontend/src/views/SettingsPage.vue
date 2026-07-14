<template>
  <div class="settings-page">
    <div class="settings-layout">
      <!-- Left nav -->
      <div class="settings-nav">
        <div
          v-for="s in sections"
          :key="s.key"
          class="sn-item"
          :class="{ active: activeSection === s.key }"
          @click="activeSection = s.key"
        >
          <el-icon><component :is="s.icon"/></el-icon>
          <span>{{ s.label }}</span>
        </div>
      </div>

      <!-- Right content -->
      <div class="settings-body">

        <!-- System settings -->
        <div v-if="activeSection === 'system'" class="section-panel">
          <div class="sp-title">系统设置</div>
          <div class="sp-desc">配置平台基础参数与运行环境</div>

          <div class="setting-group">
            <div class="sg-label">平台名称</div>
            <el-input v-model="sys.platformName" style="max-width:320px"/>
          </div>
          <div class="setting-group">
            <div class="sg-label">API 服务地址</div>
            <el-input v-model="sys.apiUrl" style="max-width:320px"/>
          </div>
          <div class="setting-group">
            <div class="sg-label">默认置信度阈值</div>
            <div class="slider-wrap">
              <el-slider v-model="sys.confThreshold" :min="0.1" :max="1" :step="0.05" style="width:240px"/>
              <span class="slider-val">{{ sys.confThreshold }}</span>
            </div>
          </div>
          <div class="setting-group">
            <div class="sg-label">默认 NMS 阈值</div>
            <div class="slider-wrap">
              <el-slider v-model="sys.nmsThreshold" :min="0.1" :max="1" :step="0.05" style="width:240px"/>
              <span class="slider-val">{{ sys.nmsThreshold }}</span>
            </div>
          </div>
          <div class="setting-group">
            <div class="sg-label">默认图像尺寸</div>
            <el-select v-model="sys.imgSize" style="width:160px">
              <el-option label="640 × 640"   value="640"/>
              <el-option label="1280 × 1280" value="1280"/>
            </el-select>
          </div>
          <div class="setting-group">
            <div class="sg-label">启用 GPU 加速</div>
            <el-switch v-model="sys.useGPU" active-color="#667eea"/>
          </div>
          <div class="setting-group">
            <div class="sg-label">结果自动保存</div>
            <el-switch v-model="sys.autoSave" active-color="#667eea"/>
          </div>
          <el-button type="primary" @click="saveSys" style="margin-top:8px">保存设置</el-button>
        </div>

        <!-- LLM settings -->
        <div v-if="activeSection === 'llm'" class="section-panel">
          <div class="sp-title">大模型配置</div>
          <div class="sp-desc">配置 AI 对话使用的大语言模型</div>

          <div class="setting-group">
            <div class="sg-label">模型提供商</div>
            <el-select v-model="llm.provider" style="width:200px" @change="onProviderChange">
              <el-option label="通义千问 (Qwen)"  value="qwen"/>
              <el-option label="OpenAI (GPT-4o)"   value="openai"/>
              <el-option label="Ollama 本地模型"    value="ollama"/>
            </el-select>
          </div>
          <div class="setting-group">
            <div class="sg-label">模型版本</div>
            <el-select v-model="llm.model" style="width:240px">
              <el-option v-for="m in llmModels" :key="m" :label="m" :value="m"/>
            </el-select>
          </div>
          <div class="setting-group" v-if="llm.provider !== 'ollama'">
            <div class="sg-label">API Key</div>
            <div class="api-key-wrap">
              <el-input
                v-model="llm.apiKey"
                :type="showKey ? 'text' : 'password'"
                placeholder="请输入 API Key"
                style="max-width:320px"
              />
              <el-button size="small" @click="showKey=!showKey">
                <el-icon><component :is="showKey ? 'View' : 'Hide'"/></el-icon>
              </el-button>
              <el-button size="small" type="primary" @click="testLLM">测试连接</el-button>
            </div>
          </div>
          <div class="setting-group" v-if="llm.provider === 'ollama'">
            <div class="sg-label">Ollama 地址</div>
            <el-input v-model="llm.ollamaUrl" style="max-width:320px" placeholder="http://localhost:11434"/>
          </div>
          <div class="setting-group">
            <div class="sg-label">Temperature</div>
            <div class="slider-wrap">
              <el-slider v-model="llm.temperature" :min="0" :max="2" :step="0.1" style="width:240px"/>
              <span class="slider-val">{{ llm.temperature }}</span>
            </div>
          </div>
          <div class="setting-group">
            <div class="sg-label">Max Tokens</div>
            <el-input-number v-model="llm.maxTokens" :min="256" :max="8192" :step="256" style="width:160px"/>
          </div>
          <div class="setting-group">
            <div class="sg-label">系统提示词</div>
            <el-input
              v-model="llm.systemPrompt"
              type="textarea"
              :rows="4"
              placeholder="您是一名专业的交通目标检测 AI 助手..."
              style="max-width:480px"
            />
          </div>
          <el-button type="primary" @click="saveLLM" style="margin-top:8px">保存配置</el-button>
        </div>

        <!-- Storage settings -->
        <div v-if="activeSection === 'storage'" class="section-panel">
          <div class="sp-title">存储配置</div>
          <div class="sp-desc">配置 MinIO 对象存储与数据库连接</div>

          <div class="sg-section-title">MinIO 对象存储</div>
          <div class="setting-group">
            <div class="sg-label">Endpoint</div>
            <el-input v-model="storage.minioEndpoint" style="max-width:320px" placeholder="localhost:9000"/>
          </div>
          <div class="setting-group">
            <div class="sg-label">Access Key</div>
            <el-input v-model="storage.minioAK" style="max-width:320px"/>
          </div>
          <div class="setting-group">
            <div class="sg-label">Secret Key</div>
            <el-input v-model="storage.minioSK" type="password" style="max-width:320px"/>
          </div>
          <div class="setting-group">
            <div class="sg-label">Bucket 名称</div>
            <el-input v-model="storage.minioBucket" style="max-width:320px"/>
          </div>
          <el-divider style="border-color:rgba(102,126,234,.15)"/>
          <div class="sg-section-title">数据库连接</div>
          <div class="setting-group">
            <div class="sg-label">数据库地址</div>
            <el-input v-model="storage.dbHost" style="max-width:320px" placeholder="localhost:5432"/>
          </div>
          <div class="setting-group">
            <div class="sg-label">数据库名称</div>
            <el-input v-model="storage.dbName" style="max-width:320px"/>
          </div>
          <div class="setting-group">
            <div class="sg-label">用户名</div>
            <el-input v-model="storage.dbUser" style="max-width:320px"/>
          </div>
          <div class="setting-group">
            <div class="sg-label">密码</div>
            <el-input v-model="storage.dbPwd" type="password" style="max-width:320px"/>
          </div>
          <div style="display:flex;gap:10px;margin-top:8px">
            <el-button type="primary" @click="saveStorage">保存配置</el-button>
            <el-button @click="testDB">测试数据库连接</el-button>
          </div>
        </div>

        <!-- Account settings -->
        <div v-if="activeSection === 'account'" class="section-panel">
          <div class="sp-title">账号设置</div>
          <div class="sp-desc">管理您的账号信息与安全设置</div>

          <div class="avatar-section">
            <div class="big-avatar">{{ userInitial }}</div>
            <div class="avatar-info">
              <span class="av-name">{{ auth.user?.username || '小明同学' }}</span>
              <span class="av-role">管理员</span>
              <el-button size="small" @click="changeAvatar">更换头像</el-button>
            </div>
          </div>

          <div class="setting-group">
            <div class="sg-label">用户名</div>
            <el-input v-model="account.username" style="max-width:320px"/>
          </div>
          <div class="setting-group">
            <div class="sg-label">邮箱地址</div>
            <el-input v-model="account.email" style="max-width:320px"/>
          </div>

          <el-divider style="border-color:rgba(102,126,234,.15)"/>
          <div class="sg-section-title">修改密码</div>
          <div class="setting-group">
            <div class="sg-label">当前密码</div>
            <el-input v-model="account.oldPwd" type="password" style="max-width:320px"/>
          </div>
          <div class="setting-group">
            <div class="sg-label">新密码</div>
            <el-input v-model="account.newPwd" type="password" style="max-width:320px"/>
          </div>
          <div class="setting-group">
            <div class="sg-label">确认新密码</div>
            <el-input v-model="account.confirmPwd" type="password" style="max-width:320px"/>
          </div>
          <div style="display:flex;gap:10px;margin-top:8px">
            <el-button type="primary" @click="saveAccount">保存修改</el-button>
            <el-button type="danger" plain @click="handleLogout">退出登录</el-button>
          </div>
        </div>

        <!-- About -->
        <div v-if="activeSection === 'about'" class="section-panel">
          <div class="sp-title">关于平台</div>
          <div class="sp-desc">FogTraffic YOLO 智能交通检测平台</div>

          <div class="about-card">
            <svg width="56" height="56" viewBox="0 0 56 56" fill="none">
              <rect width="56" height="56" rx="14" fill="url(#aboutG)"/>
              <path d="M12 30l12-12 12 12 8-8" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M12 40l12-12 12 12 8-8" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" opacity=".5"/>
              <defs>
                <linearGradient id="aboutG" x1="0" y1="0" x2="56" y2="56">
                  <stop stop-color="#667eea"/><stop offset="1" stop-color="#764ba2"/>
                </linearGradient>
              </defs>
            </svg>
            <div class="about-info">
              <h2>FogTraffic</h2>
              <p>YOLO 智能交通检测平台 v1.0.0</p>
            </div>
          </div>

          <div class="about-grid">
            <div class="about-item" v-for="item in aboutItems" :key="item.label">
              <span class="ai-label">{{ item.label }}</span>
              <span class="ai-val">{{ item.value }}</span>
            </div>
          </div>

          <div class="tech-stack">
            <div class="ts-title">技术栈</div>
            <div class="ts-tags">
              <span v-for="t in techTags" :key="t.name" class="ts-tag" :style="{ background: t.bg, color: t.color }">
                {{ t.name }}
              </span>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const auth   = useAuthStore()
const userInitial = computed(() => (auth.user?.username || '小')[0])

const activeSection = ref('system')

const sections = [
  { key: 'system',  icon: 'Setting',      label: '系统设置' },
  { key: 'llm',     icon: 'ChatDotRound', label: '大模型配置' },
  { key: 'storage', icon: 'Files',        label: '存储配置'  },
  { key: 'account', icon: 'User',         label: '账号设置'  },
  { key: 'about',   icon: 'InfoFilled',   label: '关于平台'  },
]

const sys = reactive({
  platformName: 'FogTraffic',
  apiUrl: 'http://localhost:8000',
  confThreshold: 0.5,
  nmsThreshold: 0.45,
  imgSize: '640',
  useGPU: true,
  autoSave: true,
})

const showKey = ref(false)
const llm = reactive({
  provider: 'qwen',
  model: 'qwen-max',
  apiKey: '',
  ollamaUrl: 'http://localhost:11434',
  temperature: 0.7,
  maxTokens: 2048,
  systemPrompt: '您是一名专业的交通目标检测 AI 助手，擅长分析交通场景中的车辆、行人等目标。',
})

const llmModelMap = {
  qwen:   ['qwen-max','qwen-plus','qwen-turbo'],
  openai: ['gpt-4o','gpt-4o-mini','gpt-3.5-turbo'],
  ollama: ['llama3','mistral','qwen2']
}
const llmModels = computed(() => llmModelMap[llm.provider] || [])

function onProviderChange() {
  llm.model = llmModels.value[0]
}

const storage = reactive({
  minioEndpoint: 'localhost:9000',
  minioAK: 'minioadmin',
  minioSK: '',
  minioBucket: 'fogtraffic',
  dbHost: 'localhost:5432',
  dbName: 'fogtraffic',
  dbUser: 'postgres',
  dbPwd: '',
})

const account = reactive({
  username: auth.user?.username || '小明同学',
  email: 'admin@fogtraffic.com',
  oldPwd: '', newPwd: '', confirmPwd: ''
})

const aboutItems = [
  { label: '版本号',     value: 'v1.0.0' },
  { label: '前端框架',   value: 'Vue 3 + Element Plus' },
  { label: '后端框架',   value: 'FastAPI + Python 3.10' },
  { label: 'YOLO 版本',  value: 'Ultralytics YOLOv11' },
  { label: 'AI 框架',    value: 'LangChain ReAct Agent' },
  { label: '数据库',     value: 'PostgreSQL + MinIO' },
]

const techTags = [
  { name: 'Vue 3',        bg: 'rgba(67,233,123,.12)', color: '#43e97b' },
  { name: 'FastAPI',      bg: 'rgba(79,172,254,.12)', color: '#4facfe' },
  { name: 'YOLOv11',      bg: 'rgba(102,126,234,.15)', color: '#667eea' },
  { name: 'LangChain',    bg: 'rgba(240,147,251,.12)', color: '#f093fb' },
  { name: 'PostgreSQL',   bg: 'rgba(247,151,30,.12)', color: '#f7971e' },
  { name: 'MinIO',        bg: 'rgba(250,112,154,.12)', color: '#fa709a' },
  { name: 'ECharts',      bg: 'rgba(102,126,234,.1)',  color: '#818cf8' },
  { name: 'Element Plus', bg: 'rgba(64,158,255,.12)',  color: '#409eff' },
]

function saveSys()     { ElMessage.success('系统设置已保存') }
function saveLLM()     { ElMessage.success('大模型配置已保存') }
function saveStorage() { ElMessage.success('存储配置已保存') }
function testDB()      { ElMessage.success('数据库连接成功') }
function testLLM()     { ElMessage.success('大模型连接测试成功') }
function changeAvatar(){ ElMessage.info('头像更换功能开发中...') }

function saveAccount() {
  if (account.newPwd && account.newPwd !== account.confirmPwd) {
    return ElMessage.error('两次密码不一致')
  }
  auth.user && (auth.user.username = account.username)
  ElMessage.success('账号信息已更新')
}

function handleLogout() {
  auth.logout()
  router.push('/login')
  ElMessage.success('已退出登录')
}
</script>

<style lang="scss" scoped>
.settings-page {
  height: 100%;
  padding: 20px;
  background: #0f1535;
  overflow: hidden;
}

.settings-layout {
  display: flex;
  gap: 16px;
  height: 100%;
}

/* Left nav */
.settings-nav {
  width: 160px;
  flex-shrink: 0;
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(102,126,234,.15);
  border-radius: 12px;
  padding: 10px 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  height: fit-content;
}

.sn-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13.5px;
  color: rgba(148,163,184,.75);
  transition: all .2s;
  .el-icon { font-size: 15px; flex-shrink: 0; }
  &:hover { color: #e2e8f0; background: rgba(102,126,234,.1); }
  &.active {
    color: #fff;
    background: rgba(102,126,234,.18);
    font-weight: 500;
    .el-icon { color: #667eea; }
  }
}

/* Body */
.settings-body {
  flex: 1;
  overflow-y: auto;
  min-width: 0;
}

.section-panel {
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(102,126,234,.15);
  border-radius: 12px;
  padding: 24px 28px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sp-title { font-size: 18px; font-weight: 700; color: #e2e8f0; }
.sp-desc  { font-size: 13px; color: #64748b; margin-top: -12px; }

.sg-section-title {
  font-size: 13px;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: .5px;
  border-bottom: 1px solid rgba(102,126,234,.1);
  padding-bottom: 8px;
}

.setting-group {
  display: flex;
  align-items: center;
  gap: 20px;
  .sg-label {
    width: 130px;
    flex-shrink: 0;
    font-size: 13.5px;
    font-weight: 500;
    color: #94a3b8;
  }
}

.slider-wrap {
  display: flex;
  align-items: center;
  gap: 14px;
  .slider-val {
    font-size: 13px;
    font-weight: 600;
    color: #667eea;
    min-width: 36px;
  }
}

.api-key-wrap { display: flex; gap: 8px; align-items: center; }

/* Avatar section */
.avatar-section {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: rgba(102,126,234,.08);
  border: 1px solid rgba(102,126,234,.2);
  border-radius: 12px;
}

.big-avatar {
  width: 64px; height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  font-size: 24px;
  font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

.avatar-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  .av-name { font-size: 18px; font-weight: 700; color: #e2e8f0; }
  .av-role { font-size: 12px; color: #667eea; }
}

/* About */
.about-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(102,126,234,.08);
  border: 1px solid rgba(102,126,234,.2);
  border-radius: 12px;
  h2 { font-size: 20px; font-weight: 700; color: #e2e8f0; }
  p  { font-size: 13px; color: #64748b; margin-top: 4px; }
}

.about-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.about-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 14px;
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(102,126,234,.1);
  border-radius: 8px;
  font-size: 13px;
  .ai-label { color: #64748b; }
  .ai-val   { color: #e2e8f0; font-weight: 500; }
}

.tech-stack { display: flex; flex-direction: column; gap: 10px; }
.ts-title   { font-size: 13px; font-weight: 600; color: #94a3b8; }
.ts-tags    { display: flex; flex-wrap: wrap; gap: 8px; }
.ts-tag {
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 12.5px;
  font-weight: 500;
}
</style>
