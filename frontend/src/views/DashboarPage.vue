<template>
  <div class="dashboard-page">
    <!-- Stat cards row -->
    <div class="stat-cards">
      <div class="stat-card" v-for="s in statCards" :key="s.key">
        <div class="sc-icon" :style="{ background: s.bg }">
          <el-icon :style="{ color: s.color }"><component :is="s.icon"/></el-icon>
        </div>
        <div class="sc-body">
          <span class="sc-label">{{ s.label }}</span>
          <span class="sc-value">{{ s.value }}</span>
          <span class="sc-trend" :class="s.up ? 'up' : 'down'">
            <el-icon><component :is="s.up ? 'Top' : 'Bottom'"/></el-icon>
            {{ s.trend }} 较昨日
          </span>
        </div>
      </div>
    </div>

    <!-- Charts row -->
    <div class="charts-row">
      <!-- Pie chart -->
      <div class="card chart-card">
        <div class="card-head">
          <span>各类别检测占比</span>
          <el-tag size="small">近 30 天</el-tag>
        </div>
        <div ref="pieRef" class="chart-box"></div>
      </div>

      <!-- Bar chart -->
      <div class="card chart-card" style="flex:1.6">
        <div class="card-head">
          <span>近 7 日检测趋势</span>
          <el-tag size="small">按日统计</el-tag>
        </div>
        <div ref="barRef" class="chart-box"></div>
      </div>
    </div>

    <!-- Bottom row -->
    <div class="bottom-row">
      <!-- Model usage -->
      <div class="card">
        <div class="card-head"><span>模型使用分布</span></div>
        <div class="model-list">
          <div class="model-item" v-for="m in modelUsage" :key="m.name">
            <div class="mi-head">
              <span class="mi-name">{{ m.name }}</span>
              <span class="mi-pct">{{ m.pct }}%</span>
            </div>
            <el-progress
              :percentage="m.pct"
              :stroke-width="6"
              :color="m.color"
              :show-text="false"
            />
            <span class="mi-cnt">{{ m.count }} 次调用</span>
          </div>
        </div>
      </div>

      <!-- Recent detections -->
      <div class="card" style="flex:1.8">
        <div class="card-head">
          <span>最近检测记录</span>
          <el-button size="small" text type="primary" @click="$router.push('/app/history')">
            查看全部 <el-icon><ArrowRight/></el-icon>
          </el-button>
        </div>
        <el-table :data="recentRecords" style="width:100%">
          <el-table-column prop="filename" label="文件名" min-width="140"/>
          <el-table-column prop="scene"    label="场景"   width="80"/>
          <el-table-column prop="total"    label="目标数" width="70"/>
          <el-table-column prop="model"    label="模型"   width="130"/>
          <el-table-column prop="time"     label="时间"   width="130"/>
          <el-table-column label="状态" width="80">
            <template #default>
              <span class="status-ok">✅ 完成</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const pieRef = ref(null)
const barRef = ref(null)

const statCards = [
  { key:'total',   label:'总检测次数', value:'12,847', icon:'PictureFilled', bg:'rgba(102,126,234,.15)', color:'#667eea', trend:'+128',  up:true  },
  { key:'today',   label:'今日检测量', value:'236',    icon:'TrendCharts',   bg:'rgba(67,233,123,.12)',  color:'#43e97b', trend:'+34',   up:true  },
  { key:'models',  label:'可用模型数', value:'6',      icon:'Files',         bg:'rgba(240,147,251,.12)', color:'#f093fb', trend:'+1',    up:true  },
  { key:'acc',     label:'平均置信度', value:'0.873',  icon:'Star',          bg:'rgba(247,151,30,.12)',  color:'#f7971e', trend:'+0.02', up:true  },
]

const modelUsage = [
  { name:'fogtraffic_v1 (YOLOv11n)', pct:45, count:5781, color:'#667eea' },
  { name:'fogtraffic_v2 (YOLOv11s)', pct:30, count:3854, color:'#f093fb' },
  { name:'remote_v1 (YOLOv11m)',     pct:15, count:1927, color:'#4facfe' },
  { name:'industry_v1 (YOLOv11n)',   pct:10, count:1285, color:'#43e97b' },
]

const recentRecords = [
  { filename:'traffic_001.jpg', scene:'交通', total:5,  model:'fogtraffic_v1', time:'2024-06-06 10:32' },
  { filename:'highway_fog.jpg', scene:'交通', total:8,  model:'fogtraffic_v2', time:'2024-06-06 10:28' },
  { filename:'batch_0612.zip',  scene:'交通', total:42, model:'fogtraffic_v1', time:'2024-06-06 09:55' },
  { filename:'remote_23.jpg',   scene:'遥感', total:12, model:'remote_v1',     time:'2024-06-06 09:20' },
  { filename:'road_night.jpg',  scene:'交通', total:3,  model:'fogtraffic_v2', time:'2024-06-05 22:11' },
]

onMounted(() => {
  initPie()
  initBar()
})

function initPie() {
  const chart = echarts.init(pieRef.value, null, { renderer: 'svg' })
  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: '#1a2050',
      borderColor: 'rgba(102,126,234,.3)',
      textStyle: { color: '#e2e8f0', fontSize: 12 }
    },
    legend: {
      orient: 'vertical', right: 10, top: 'center',
      textStyle: { color: '#94a3b8', fontSize: 11 },
      itemWidth: 10, itemHeight: 10
    },
    series: [{
      type: 'pie',
      radius: ['42%', '68%'],
      center: ['38%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 6, borderColor: 'transparent', borderWidth: 2 },
      label: { show: false },
      emphasis: {
        label: { show: true, fontSize: 13, fontWeight: 'bold', color: '#e2e8f0' }
      },
      data: [
        { value: 5200, name: '轿车',   itemStyle: { color: '#667eea' } },
        { value: 2800, name: '卡车',   itemStyle: { color: '#f093fb' } },
        { value: 2100, name: '行人',   itemStyle: { color: '#4facfe' } },
        { value: 1400, name: '摩托车', itemStyle: { color: '#43e97b' } },
        { value: 900,  name: '公交车', itemStyle: { color: '#f7971e' } },
        { value: 447,  name: '其他',   itemStyle: { color: '#94a3b8' } },
      ]
    }]
  })
}

function initBar() {
  const chart = echarts.init(barRef.value, null, { renderer: 'svg' })
  const days  = ['06-01','06-02','06-03','06-04','06-05','06-06','06-07']
  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1a2050',
      borderColor: 'rgba(102,126,234,.3)',
      textStyle: { color: '#e2e8f0', fontSize: 12 }
    },
    legend: {
      data: ['交通场景','遥感场景','工业场景'],
      textStyle: { color: '#94a3b8', fontSize: 11 }, top: 0
    },
    grid: { top: 32, left: 40, right: 16, bottom: 24 },
    xAxis: {
      type: 'category', data: days,
      axisLine: { lineStyle: { color: 'rgba(102,126,234,.2)' } },
      axisLabel: { color: '#64748b', fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: 'rgba(102,126,234,.08)' } },
      axisLabel: { color: '#64748b', fontSize: 11 }
    },
    series: [
      {
        name: '交通场景', type: 'bar', stack: 'total', barMaxWidth: 40,
        data: [120,180,150,200,170,236,190],
        itemStyle: { color: { type:'linear',x:0,y:0,x2:0,y2:1, colorStops:[{offset:0,color:'#667eea'},{offset:1,color:'#764ba2'}] }, borderRadius:[4,4,0,0] }
      },
      {
        name: '遥感场景', type: 'bar', stack: 'total', barMaxWidth: 40,
        data: [30,45,38,52,41,60,55],
        itemStyle: { color: '#4facfe', borderRadius:[0,0,0,0] }
      },
      {
        name: '工业场景', type: 'bar', stack: 'total', barMaxWidth: 40,
        data: [15,22,18,28,20,32,25],
        itemStyle: { color: '#43e97b', borderRadius:[0,0,0,0] }
      },
    ]
  })
}
</script>

<style lang="scss" scoped>
.dashboard-page {
  height: 100%;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: #0f1535;
}

.stat-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  flex-shrink: 0;
}

.stat-card {
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(102,126,234,.15);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  transition: all .2s;
  &:hover { border-color: rgba(102,126,234,.3); transform: translateY(-2px); }
}

.sc-icon {
  width: 46px; height: 46px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  .el-icon { font-size: 22px; }
}

.sc-body {
  display: flex; flex-direction: column; gap: 3px;
  .sc-label { font-size: 12px; color: #64748b; }
  .sc-value { font-size: 24px; font-weight: 700; color: #e2e8f0; line-height: 1; }
  .sc-trend {
    display: flex; align-items: center; gap: 3px; font-size: 11px;
    .el-icon { font-size: 10px; }
    &.up   { color: #4ade80; }
    &.down { color: #f87171; }
  }
}

.charts-row {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

.card {
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(102,126,234,.15);
  border-radius: 12px;
  overflow: hidden;
}

.card-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(102,126,234,.1);
  font-size: 14px; font-weight: 600; color: #e2e8f0;
}

.chart-card { display: flex; flex-direction: column; }
.chart-box  { height: 220px; padding: 8px; flex: 1; }

.bottom-row {
  display: flex;
  gap: 12px;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.bottom-row .card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.model-list {
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  overflow-y: auto;
}

.model-item { display: flex; flex-direction: column; gap: 5px; }
.mi-head    { display: flex; justify-content: space-between; }
.mi-name    { font-size: 12.5px; color: #e2e8f0; font-weight: 500; }
.mi-pct     { font-size: 12px; font-weight: 700; color: #667eea; }
.mi-cnt     { font-size: 11px; color: #64748b; }

.status-ok { font-size: 12px; color: #4ade80; }
</style>
