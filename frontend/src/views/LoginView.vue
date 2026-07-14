<template>
  <div class="login-page">
    <div class="blob b1"></div>
    <div class="blob b2"></div>
    <div class="blob b3"></div>

    <div class="card">
      <!-- Left brand -->
      <div class="brand">
        <svg width="52" height="52" viewBox="0 0 52 52" fill="none">
          <rect width="52" height="52" rx="14" fill="url(#lg)"/>
          <path d="M10 28l10-10 10 10 12-10" stroke="white" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M10 38l10-10 10 10 12-10" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" opacity=".5"/>
          <defs>
            <linearGradient id="lg" x1="0" y1="0" x2="52" y2="52">
              <stop stop-color="#667eea"/><stop offset="1" stop-color="#764ba2"/>
            </linearGradient>
          </defs>
        </svg>
        <h1>FogTraffic</h1>
        <p class="slogan">YOLO 智能交通检测平台</p>
        <p class="desc">AI 驱动智慧交通，让城市更安全高效</p>
        <div class="tags">
          <span><i class="dot"></i>高精度检测</span>
          <span><i class="dot"></i>实时分析</span>
          <span><i class="dot"></i>智能决策</span>
        </div>
      </div>

      <!-- Right form -->
      <div class="form-box">
        <div class="form-header">
          <h2>{{ isLogin ? '欢迎回来 👋' : '创建账号 🚀' }}</h2>
          <p>{{ isLogin ? '登录您的账号继续使用' : '注册后即可使用全部功能' }}</p>
        </div>

        <!-- Tab switch -->
        <div class="tabs">
          <button :class="{ active: isLogin }"  @click="isLogin=true">登录</button>
          <button :class="{ active: !isLogin }" @click="isLogin=false">注册</button>
          <div class="tab-bar" :style="{ left: isLogin ? '0' : '50%' }"></div>
        </div>

        <!-- Login -->
        <form v-if="isLogin" @submit.prevent="handleLogin">
          <div class="field">
            <label>邮箱 / 用户名</label>
            <div class="input-row">
              <el-icon><User/></el-icon>
              <input v-model="lf.username" type="text" placeholder="请输入用户名" required/>
            </div>
          </div>
          <div class="field">
            <label>密码</label>
            <div class="input-row">
              <el-icon><Lock/></el-icon>
              <input v-model="lf.password" :type="showPwd?'text':'password'" placeholder="请输入密码" required/>
              <el-icon class="eye" @click="showPwd=!showPwd"><component :is="showPwd?'View':'Hide'"/></el-icon>
            </div>
          </div>
          <div class="row-between">
            <label class="check-label">
              <input type="checkbox" v-model="lf.remember"/>
              <span>记住我</span>
            </label>
            <a href="#" class="link">忘记密码？</a>
          </div>
          <button type="submit" class="submit-btn" :disabled="loading">
            <span v-if="!loading">登 录</span>
            <span v-else class="spinner"></span>
          </button>
          <p class="switch-text">还没有账号？<a href="#" @click.prevent="isLogin=false">立即注册</a></p>
        </form>

        <!-- Register -->
        <form v-else @submit.prevent="handleRegister">
          <div class="field">
            <label>用户名</label>
            <div class="input-row">
              <el-icon><User/></el-icon>
              <input v-model="rf.username" type="text" placeholder="请输入用户名" required/>
            </div>
          </div>
          <div class="field">
            <label>邮箱</label>
            <div class="input-row">
              <el-icon><Message/></el-icon>
              <input v-model="rf.email" type="email" placeholder="请输入邮箱地址" required/>
            </div>
          </div>
          <div class="field">
            <label>密码</label>
            <div class="input-row">
              <el-icon><Lock/></el-icon>
              <input v-model="rf.password" type="password" placeholder="至少8位密码" required/>
            </div>
          </div>
          <div class="field">
            <label>确认密码</label>
            <div class="input-row">
              <el-icon><Lock/></el-icon>
              <input v-model="rf.confirm" type="password" placeholder="再次输入密码" required/>
            </div>
          </div>
          <button type="submit" class="submit-btn" :disabled="loading">
            <span v-if="!loading">注 册</span>
            <span v-else class="spinner"></span>
          </button>
          <p class="switch-text">已有账号？<a href="#" @click.prevent="isLogin=true">立即登录</a></p>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router  = useRouter()
const auth    = useAuthStore()
const isLogin = ref(true)
const showPwd = ref(false)
const loading = ref(false)

const lf = reactive({ username: '', password: '', remember: false })
const rf = reactive({ username: '', email: '', password: '', confirm: '' })

async function handleLogin() {
  if (!lf.username || !lf.password) return ElMessage.warning('请填写完整信息')
  loading.value = true
  await new Promise(r => setTimeout(r, 800))
  auth.login(lf.username)
  ElMessage.success('登录成功，欢迎回来！')
  router.push('/app/chat')
  loading.value = false
}

async function handleRegister() {
  if (!rf.username || !rf.email || !rf.password) return ElMessage.warning('请填写完整信息')
  if (rf.password !== rf.confirm) return ElMessage.error('两次密码不一致')
  loading.value = true
  await new Promise(r => setTimeout(r, 800))
  auth.login(rf.username)
  ElMessage.success('注册成功！')
  router.push('/app/chat')
  loading.value = false
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0e2d 0%, #1a1050 50%, #0d1a40 100%);
  display: flex; align-items: center; justify-content: center;
  position: relative; overflow: hidden;
}

.blob {
  position: absolute; border-radius: 50%; filter: blur(80px); pointer-events: none;
  &.b1 { width:500px; height:500px; background:rgba(102,126,234,.18); top:-100px; left:-100px; animation: drift 8s ease-in-out infinite; }
  &.b2 { width:400px; height:400px; background:rgba(118,75,162,.15); bottom:-80px; right:-80px; animation: drift 10s ease-in-out infinite reverse; }
  &.b3 { width:300px; height:300px; background:rgba(102,126,234,.1); top:50%; left:50%; transform:translate(-50%,-50%); animation: drift 6s ease-in-out infinite 2s; }
}

@keyframes drift {
  0%,100% { transform: translate(0,0) scale(1); }
  50%      { transform: translate(30px,20px) scale(1.05); }
}

.card {
  display: flex;
  background: rgba(255,255,255,.06);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 24px;
  overflow: hidden;
  width: 860px;
  min-height: 520px;
  box-shadow: 0 32px 80px rgba(0,0,0,.4);
  position: relative; z-index: 1;
}

/* Brand panel */
.brand {
  width: 340px; flex-shrink: 0;
  background: linear-gradient(145deg, rgba(102,126,234,.25), rgba(118,75,162,.2));
  border-right: 1px solid rgba(255,255,255,.08);
  padding: 52px 40px;
  display: flex; flex-direction: column; justify-content: center;
  h1 { font-size: 28px; font-weight: 800; color: #fff; margin: 18px 0 6px; }
  .slogan { font-size: 13px; color: rgba(255,255,255,.55); margin-bottom: 16px; }
  .desc { font-size: 14px; color: rgba(255,255,255,.7); line-height: 1.6; margin-bottom: 28px; }
}

.tags {
  display: flex; flex-direction: column; gap: 10px;
  span {
    display: flex; align-items: center; gap: 8px;
    font-size: 13px; color: rgba(255,255,255,.65);
  }
  .dot {
    display: inline-block; width: 7px; height: 7px; border-radius: 50%;
    background: linear-gradient(135deg, #667eea, #764ba2);
  }
}

/* Form panel */
.form-box {
  flex: 1; padding: 48px 44px;
  display: flex; flex-direction: column; justify-content: center;
}

.form-header {
  margin-bottom: 28px;
  h2 { font-size: 22px; font-weight: 700; color: #e2e8f0; margin-bottom: 4px; }
  p  { font-size: 13px; color: #94a3b8; }
}

.tabs {
  display: flex; position: relative;
  background: rgba(255,255,255,.06);
  border-radius: 8px; padding: 3px;
  margin-bottom: 28px; width: 180px;
  button {
    flex: 1; padding: 6px 0; border: none; background: transparent;
    font-size: 13px; color: #94a3b8; cursor: pointer; border-radius: 6px;
    position: relative; z-index: 1; transition: color .2s;
    &.active { color: #fff; font-weight: 600; }
  }
  .tab-bar {
    position: absolute; top: 3px; width: 50%; height: calc(100% - 6px);
    background: linear-gradient(135deg,#667eea,#764ba2);
    border-radius: 6px; transition: left .25s ease;
  }
}

.field {
  margin-bottom: 16px;
  label { display: block; font-size: 12px; color: #94a3b8; margin-bottom: 7px; font-weight: 500; }
}

.input-row {
  display: flex; align-items: center; gap: 10px;
  background: rgba(255,255,255,.06);
  border: 1px solid rgba(102,126,234,.25);
  border-radius: 10px; padding: 0 14px;
  transition: border-color .2s, box-shadow .2s;
  .el-icon { color: #94a3b8; font-size: 16px; flex-shrink: 0; }
  input {
    flex: 1; background: transparent; border: none; outline: none;
    color: #e2e8f0; font-size: 14px; padding: 11px 0;
    font-family: inherit;
    &::placeholder { color: rgba(148,163,184,.5); }
  }
  .eye { cursor: pointer; &:hover { color: #667eea; } }
  &:focus-within {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102,126,234,.2);
  }
}

.row-between {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 20px;
}
.check-label {
  display: flex; align-items: center; gap: 6px; cursor: pointer;
  font-size: 13px; color: #94a3b8;
  input[type=checkbox] { accent-color: #667eea; }
}
.link { font-size: 13px; color: #667eea; text-decoration: none; &:hover { text-decoration: underline; } }

.submit-btn {
  width: 100%; padding: 12px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none; border-radius: 10px;
  color: #fff; font-size: 15px; font-weight: 600;
  cursor: pointer; transition: all .2s;
  display: flex; align-items: center; justify-content: center; gap: 6px;
  margin-bottom: 16px;
  &:hover:not(:disabled) { opacity: .88; transform: translateY(-1px); box-shadow: 0 6px 20px rgba(102,126,234,.4); }
  &:disabled { opacity: .6; cursor: not-allowed; }
}

.spinner {
  width: 18px; height: 18px; border-radius: 50%;
  border: 2px solid rgba(255,255,255,.3);
  border-top-color: #fff;
  animation: spin .7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.switch-text {
  text-align: center; font-size: 13px; color: #94a3b8;
  a { color: #667eea; text-decoration: none; &:hover { text-decoration: underline; } }
}
</style>
