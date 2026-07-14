<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="logo-wrap">
        <svg width="32" height="32" viewBox="0 0 40 40" fill="none">
          <rect width="40" height="40" rx="10" fill="url(#g1)"/>
          <path d="M9 22l9-9 9 9 5-5" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M9 30l9-9 9 9 5-5" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity=".5"/>
          <defs>
            <linearGradient id="g1" x1="0" y1="0" x2="40" y2="40">
              <stop stop-color="#667eea"/><stop offset="1" stop-color="#764ba2"/>
            </linearGradient>
          </defs>
        </svg>
        <span class="logo-title">FogTraffic</span>
      </div>

      <nav class="nav">
        <router-link v-for="n in nav" :key="n.to" :to="n.to"
          class="nav-item" :class="{ active: route.path === n.to }">
          <el-icon><component :is="n.icon"/></el-icon>
          <span>{{ n.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar-foot">
        <div class="collapse-btn">
          <el-icon><DArrowLeft/></el-icon>
          <span>收起侧栏</span>
        </div>
      </div>
    </aside>

    <div class="body">
      <header class="topbar">
        <span class="page-title">{{ title }}</span>
        <div class="top-actions">
          <el-tooltip content="通知">
            <el-icon class="top-icon"><Bell/></el-icon>
          </el-tooltip>
          <el-dropdown @command="onCmd">
            <div class="avatar-wrap">
              <div class="avatar">{{ initial }}</div>
              <span class="uname">{{ user?.username || '小明同学' }}</span>
              <el-icon style="font-size:12px;color:#94a3b8"><ArrowDown/></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="settings">系统设置</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const route  = useRoute()
const router = useRouter()
const auth   = useAuthStore()
const user   = computed(() => auth.user)
const initial = computed(() => (user.value?.username || '小')[0])

const nav = [
  { to: '/app/chat',      icon: 'ChatDotRound', label: '智能对话'   },
  { to: '/app/training',  icon: 'TrendCharts',  label: '模型训练'   },
  { to: '/app/detection', icon: 'Search',       label: '检测工作台' },
  { to: '/app/dashboard', icon: 'DataAnalysis', label: '数据看板'   },
  { to: '/app/history',   icon: 'Clock',        label: '历史记录'   },
  { to: '/app/settings',  icon: 'Setting',      label: '系统设置'   }
]

const titleMap = {
  '/app/chat':'智能对话', '/app/training':'模型训练',
  '/app/detection':'检测工作台', '/app/dashboard':'数据看板',
  '/app/history':'历史记录', '/app/settings':'系统设置'
}
const title = computed(() => titleMap[route.path] || 'FogTraffic')

function onCmd(cmd) {
  if (cmd === 'logout') { auth.logout(); router.push('/login'); ElMessage.success('已退出登录') }
  if (cmd === 'settings') router.push('/app/settings')
}
</script>

<style lang="scss" scoped>
.layout { display:flex; height:100vh; background:#0f1535; overflow:hidden; }

.sidebar {
  width:180px; flex-shrink:0;
  background:#090d28;
  border-right:1px solid rgba(102,126,234,.15);
  display:flex; flex-direction:column;
}

.logo-wrap {
  display:flex; align-items:center; gap:10px;
  padding:18px 16px 14px;
  border-bottom:1px solid rgba(102,126,234,.1);
  .logo-title { font-size:17px; font-weight:700; color:#fff; }
}

.nav {
  flex:1; padding:10px 8px;
  display:flex; flex-direction:column; gap:2px;
  overflow-y:auto;
}

.nav-item {
  display:flex; align-items:center; gap:9px;
  padding:9px 12px; border-radius:8px;
  color:rgba(148,163,184,.75); text-decoration:none;
  font-size:13.5px; transition:all .2s; position:relative;
  .el-icon { font-size:16px; flex-shrink:0; }
  &:hover { color:#e2e8f0; background:rgba(102,126,234,.1); }
  &.active {
    color:#fff; background:rgba(102,126,234,.18); font-weight:500;
    &::before {
      content:''; position:absolute; left:-8px; top:50%; transform:translateY(-50%);
      width:3px; height:18px;
      background:linear-gradient(180deg,#667eea,#764ba2);
      border-radius:0 2px 2px 0;
    }
    .el-icon { color:#667eea; }
  }
}

.sidebar-foot {
  padding:14px 8px;
  border-top:1px solid rgba(102,126,234,.1);
}
.collapse-btn {
  display:flex; align-items:center; gap:7px;
  padding:8px 10px; border-radius:7px; cursor:pointer;
  color:rgba(148,163,184,.4); font-size:12px; transition:all .2s;
  &:hover { color:rgba(148,163,184,.7); background:rgba(255,255,255,.04); }
}

.body { flex:1; display:flex; flex-direction:column; overflow:hidden; }

.topbar {
  height:56px; display:flex; align-items:center; justify-content:space-between;
  padding:0 24px;
  background:rgba(9,13,40,.8);
  border-bottom:1px solid rgba(102,126,234,.12);
  flex-shrink:0;
}
.page-title { font-size:16px; font-weight:600; color:#e2e8f0; }
.top-actions { display:flex; align-items:center; gap:16px; }
.top-icon { font-size:18px; color:rgba(148,163,184,.7); cursor:pointer; &:hover { color:#667eea; } }
.avatar-wrap {
  display:flex; align-items:center; gap:8px; cursor:pointer;
  padding:4px 10px; border-radius:20px; transition:background .2s;
  &:hover { background:rgba(102,126,234,.1); }
}
.avatar {
  width:28px; height:28px; border-radius:50%;
  background:linear-gradient(135deg,#667eea,#764ba2);
  color:#fff; font-size:12px; font-weight:700;
  display:flex; align-items:center; justify-content:center;
}
.uname { font-size:13px; color:#cbd5e1; }

.content { flex:1; overflow:hidden; }
</style>
