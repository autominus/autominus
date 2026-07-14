<template>
  <div class="training-page">
    <div class="page-header">
      <span class="sub-title">管理并监控您的 YOLO 模型训练任务</span>
      <el-button type="primary" @click="showCreate=true">
        <el-icon><Plus/></el-icon>新建训练任务
      </el-button>
    </div>

    <!-- Task table -->
    <div class="card table-card">
      <div class="card-head">
        <span>训练任务列表</span>
        <el-tag size="small">{{ tasks.length }} 个任务</el-tag>
      </div>
      <el-table :data="tasks" style="width:100%">
        <el-table-column prop="name" label="任务名称" min-width="160">
          <template #default="{ row }">
            <div class="task-name-cell">
              <span>{{ row.name }}</span>
              <el-tag size="small" style="margin-left:6px">{{ row.model }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="scene" label="场景" width="90"/>
        <el-table-column prop="epochs" label="轮次" width="80"/>
        <el-table-column label="进度" width="160">
          <template #default="{ row }">
            <div class="progress-cell">
              <el-progress
                :percentage="row.progress"
                :stroke-width="6"
                :color="progressColor(row.status)"
                :show-text="false"
                style="flex:1"
              />
              <span class="pct-text">{{ row.progress }}%</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <span class="status-dot" :class="row.status">
              <i></i>{{ statusLabel(row.status) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="mAP50" label="mAP50" width="80"/>
        <el-table-column prop="createTime" label="创建时间" width="130"/>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text type="primary" @click="openMonitor(row)">监控</el-button>
            <el-button size="small" text type="danger"
              v-if="row.status==='running'" @click="stopTask(row)">停止</el-button>
            <el-button size="small" text type="success"
              v-if="row.status==='done'" @click="downloadModel(row)">下载</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Monitor panel -->
    <div v-if="activeTask" class="monitor-panel">
      <div class="card-head">
        <div class="monitor-title">
          <el-icon style="color:#667eea"><TrendCharts/></el-icon>
          <span>实时监控 — {{ activeTask.name }}</span>
          <span class="status-dot" :class="activeTask.status"><i></i>{{ statusLabel(activeTask.status) }}</span>
        </div>
        <el-button size="small" text @click="activeTask=null"><el-icon><Close/></el-icon></el-button>
      </div>

      <!-- Metric cards -->
      <div class="metric-cards">
        <div class="metric-card" v-for="m in metricCards" :key="m.key">
          <div class="mc-label">{{ m.label }}</div>
          <div class="mc-value">{{ activeTask[m.key] ?? '—' }}</div>
          <div class="mc-trend" :class="m.trend">
            <el-icon><component :is="m.trend==='up'?'Top':'Bottom'"/></el-icon>
            {{ m.delta }}
          </div>
        </div>
      </div>

      <!-- Charts -->
      <div class="charts-row">
        <div class="card chart-card">
          <div class="chart-title">Loss 曲线</div>
          <div ref="lossChartRef" class="chart-box"></div>
        </div>
        <div class="card chart-card">
          <div class="chart-title">mAP 曲线</div>
          <div ref="mapChartRef" class="chart-box"></div>
        </div>
      </div>

      <!-- Bottom: confusion matrix + model ops -->
      <div class="bottom-row">
        <div class="card matrix-card">
          <div class="card-head"><span>混淆矩阵</span></div>
          <div class="matrix-grid">
            <div class="matrix-labels-y">
              <span v-for="c in confusionClasses" :key="c">{{ c }}</span>
            </div>
            <div class="matrix-cells">
              <div v-for="(row, ri) in confusionMatrix" :key="ri" class="matrix-row">
                <div
                  v-for="(val, ci) in row" :key="ci"
                  class="matrix-cell"
                  :style="{ background: matrixColor(val) }"
                >{{ val }}</div>
              </div>
              <div class="matrix-labels-x">
                <span v-for="c in confusionClasses" :key="c">{{ c }}</span>
              </div>
            </div>
          </div>
          <div class="matrix-legend">
            <span>预测类别</span>
          </div>
        </div>

        <div class="card ops-card">
          <div class="card-head"><span>模型操作</span></div>
          <div class="ops-list">
            <div class="ops-item" @click="showEvalDialog=true">
              <div class="ops-icon" style="background:rgba(102,126,234,.15)">
                <el-icon style="color:#667eea"><DataAnalysis/></el-icon>
              </div>
              <div class="ops-info">
                <span class="ops-name">评估报告</span>
                <span class="ops-desc">查看各类别 AP 详情</span>
              </div>
              <el-icon class="ops-arrow"><ArrowRight/></el-icon>
            </div>
            <div class="ops-item" @click="exportModel">
              <div class="ops-icon" style="background:rgba(240,147,251,.12)">
                <el-icon style="color:#f093fb"><Upload/></el-icon>
              </div>
              <div class="ops-info">
                <span class="ops-name">导出版本</span>
                <span class="ops-desc">导出 ONNX / TorchScript</span>
              </div>
              <el-icon class="ops-arrow"><ArrowRight/></el-icon>
            </div>
            <div class="ops-item" @click="downloadModel(activeTask)">
              <div class="ops-icon" style="background:rgba(79,172,254,.12)">
                <el-icon style="color:#4facfe"><Download/></el-icon>
              </div>
              <div class="ops-info">
                <span class="ops-name">下载权重</span>
                <span class="ops-desc">下载 best.pt 权重文件</span>
              </div>
              <el-icon class="ops-arrow"><ArrowRight/></el-icon>
            </div>
            <div class="ops-item" @click="triggerTestImg">
              <div class="ops-icon" style="background:rgba(67,233,123,.1)">
                <el-icon style="color:#43e97b"><PictureFilled/></el-icon>
              </div>
              <div class="ops-info">
                <span class="ops-name">上传测试图</span>
                <span class="ops-desc">验证模型推理效果</span>
              </div>
              <el-icon class="ops-arrow"><ArrowRight/></el-icon>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Task Dialog -->
    <el-dialog v-model="showCreate" title="新建训练任务" width="520px">
      <el-form :model="createForm" label-width="90px">
        <el-form-item label="任务名称">
          <el-input v-model="createForm.name" placeholder="如：fogtraffic_v2"/>
        </el-form-item>
        <el-form-item label="基础模型">
          <el-select v-model="createForm.model" style="width:100%">
            <el-option v-for="m in modelOptions" :key="m" :label="m" :value="m"/>
          </el-select>
        </el-form-item>
        <el-form-item label="检测场景">
          <el-select v-model="createForm.scene" style="width:100%">
            <el-option label="交通场景" value="traffic"/>
            <el-option label="遥感场景" value="remote"/>
            <el-option label="工业场景" value="industry"/>
          </el-select>
        </el-form-item>
        <el-form-item label="训练轮次">
          <el-input-number v-model="createForm.epochs" :min="1" :max="300" style="width:100%"/>
        </el-form-item>
        <el-form-item label="Batch Size">
          <el-input-number v-model="createForm.batch" :min="4" :max="64" style="width:100%"/>
        </el-form-item>
        <el-form-item label="学习率">
          <el-input v-model="createForm.lr" placeholder="0.01"/>
        </el-form-item>
        <el-form-item label="图像尺寸">
          <el-select v-model="createForm.imgSize" style="width:100%">
            <el-option label="640" value="640"/>
            <el-option label="1280" value="1280"/>
          </el-select>
        </el-form-item>
        <el-form-item label="训练设备">
          <el-select v-model="createForm.device" style="width:100%">
            <el-option label="GPU (cuda:0)" value="cuda:0"/>
            <el-option label="CPU" value="cpu"/>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate=false">取消</el-button>
        <el-button type="primary" @click="createTask">开始训练</el-button>
      </template>
    </el-dialog>

    <!-- Eval Dialog -->
    <el-dialog v-model="showEvalDialog" title="评估报告" width="500px">
      <el-table :data="evalData" style="width:100%">
        <el-table-column prop="cls"  label="类别" />
        <el-table-column prop="ap50" label="AP50" />
        <el-table-column prop="ap"   label="AP50-95" />
        <el-table-column prop="prec" label="Precision" />
        <el-table-column prop="rec"  label="Recall" />
      </el-table>
    </el-dialog>

    <input ref="testImgRef" type="file" accept="image/*" style="display:none" @change="onTestImg"/>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

/* ── Tasks data ── */
const tasks = reactive([
  { id:1, name:'fogtraffic_v1', model:'YOLOv11n', scene:'交通', epochs:100, progress:100, status:'done',    mAP50:'0.887', createTime:'2024-06-01 10:20' },
  { id:2, name:'fogtraffic_v2', model:'YOLOv11s', scene:'交通', epochs:150, progress:68,  status:'running', mAP50:'0.821', createTime:'2024-06-05 14:30' },
  { id:3, name:'remote_v1',     model:'YOLOv11m', scene:'遥感', epochs:80,  progress:100, status:'done',    mAP50:'0.763', createTime:'2024-06-03 09:00' },
  { id:4, name:'industry_test', model:'YOLOv11n', scene:'工业', epochs:50,  progress:30,  status:'queued',  mAP50:'—',     createTime:'2024-06-06 08:00' },
])

const showCreate = ref(false)
const showEvalDialog = ref(false)
const activeTask = ref(null)
const lossChartRef = ref(null)
const mapChartRef  = ref(null)
const testImgRef   = ref(null)

const modelOptions = ['YOLOv11n','YOLOv11s','YOLOv11m','YOLOv11l','YOLOv11x']

const createForm = reactive({
  name:'', model:'YOLOv11n', scene:'traffic',
  epochs:100, batch:16, lr:'0.01', imgSize:'640', device:'cuda:0'
})

const metricCards = [
  { key:'mAP50',    label:'mAP50',     trend:'up',   delta:'+0.023' },
  { key:'mAP5095',  label:'mAP50-95',  trend:'up',   delta:'+0.015' },
  { key:'precision',label:'Precision', trend:'up',   delta:'+0.018' },
  { key:'recall',   label:'Recall',    trend:'down',  delta:'-0.004' },
  { key:'loss',     label:'Box Loss',  trend:'down',  delta:'-0.031' },
]

const confusionClasses = ['car','truck','person','bg']
const confusionMatrix  = [
  [85, 3,  1,  2 ],
  [4,  78, 0,  3 ],
  [2,  0,  91, 1 ],
  [1,  2,  1,  95],
]

const evalData = [
  { cls:'car',    ap50:'0.921', ap:'0.734', prec:'0.912', rec:'0.893' },
  { cls:'truck',  ap50:'0.876', ap:'0.681', prec:'0.867', rec:'0.842' },
  { cls:'person', ap50:'0.934', ap:'0.756', prec:'0.928', rec:'0.911' },
]

function progressColor(status) {
  if (status === 'done')    return '#4ade80'
  if (status === 'running') return '#667eea'
  if (status === 'failed')  return '#f87171'
  return '#94a3b8'
}

function statusLabel(s) {
  return { running:'训练中', done:'已完成', failed:'失败', queued:'排队中' }[s] || s
}

function openMonitor(row) {
  activeTask.value = {
    ...row,
    mAP5095: '0.712', precision: '0.891', recall: '0.873', loss: '0.043'
  }
  nextTick(() => { initCharts() })
}

function stopTask(row) {
  row.status = 'failed'
  ElMessage.warning('已停止任务：' + row.name)
}

function downloadModel(row) {
  ElMessage.success('开始下载 ' + row.name + ' best.pt')
}

function exportModel() {
  ElMessage.success('模型导出为 ONNX 格式成功')
}

function triggerTestImg() {
  testImgRef.value?.click()
}

function onTestImg(e) {
  if (e.target.files[0]) ElMessage.success('测试图片上传成功，推理中...')
}

function createTask() {
  if (!createForm.name) return ElMessage.warning('请输入任务名称')
  tasks.unshift({
    id: Date.now(),
    name: createForm.name,
    model: createForm.model,
    scene: { traffic:'交通', remote:'遥感', industry:'工业' }[createForm.scene],
    epochs: createForm.epochs,
    progress: 0,
    status: 'queued',
    mAP50: '—',
    createTime: new Date().toLocaleString('zh-CN').slice(0,16)
  })
  showCreate.value = false
  ElMessage.success('训练任务已创建！')
}

function matrixColor(val) {
  const max = 100
  const ratio = val / max
  const r = Math.round(102 + (239 - 102) * ratio)
  const g = Math.round(126 - (126 - 68) * ratio)
  const b = Math.round(234 - (234 - 68) * ratio)
  return `rgba(${r},${g},${b},${0.2 + ratio * 0.6})`
}

/* ── ECharts ── */
function initCharts() {
  const epochs = Array.from({ length: 20 }, (_, i) => i + 1)

  // Loss chart
  const lossChart = echarts.init(lossChartRef.value, null, { renderer: 'svg' })
  lossChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', backgroundColor: '#1a2050', borderColor: 'rgba(102,126,234,.3)', textStyle: { color: '#e2e8f0', fontSize: 12 } },
    legend: { data: ['box_loss', 'cls_loss', 'dfl_loss'], textStyle: { color: '#94a3b8', fontSize: 11 }, top: 0 },
    grid: { top: 32, left: 40, right: 16, bottom: 24 },
    xAxis: { type: 'category', data: epochs, axisLine: { lineStyle: { color: 'rgba(102,126,234,.2)' } }, axisLabel: { color: '#64748b', fontSize: 11 } },
    yAxis: { type: 'value', axisLine: { show: false }, splitLine: { lineStyle: { color: 'rgba(102,126,234,.08)' } }, axisLabel: { color: '#64748b', fontSize: 11 } },
    series: [
      {
        name: 'box_loss', type: 'line', smooth: true,
        data: epochs.map((_, i) => +(1.8 - i * 0.08 + Math.random() * 0.05).toFixed(3)),
        lineStyle: { color: '#667eea', width: 2 },
        itemStyle: { color: '#667eea' },
        areaStyle: { color: { type: 'linear', x:0,y:0,x2:0,y2:1, colorStops: [{ offset:0, color:'rgba(102,126,234,.25)' }, { offset:1, color:'rgba(102,126,234,.02)' }] } },
        symbol: 'none'
      },
      {
        name: 'cls_loss', type: 'line', smooth: true,
        data: epochs.map((_, i) => +(1.2 - i * 0.05 + Math.random() * 0.04).toFixed(3)),
        lineStyle: { color: '#f093fb', width: 2 },
        itemStyle: { color: '#f093fb' },
        areaStyle: { color: { type: 'linear', x:0,y:0,x2:0,y2:1, colorStops: [{ offset:0, color:'rgba(240,147,251,.2)' }, { offset:1, color:'rgba(240,147,251,.02)' }] } },
        symbol: 'none'
      },
      {
        name: 'dfl_loss', type: 'line', smooth: true,
        data: epochs.map((_, i) => +(0.9 - i * 0.03 + Math.random() * 0.03).toFixed(3)),
        lineStyle: { color: '#4facfe', width: 2 },
        itemStyle: { color: '#4facfe' },
        areaStyle: { color: { type: 'linear', x:0,y:0,x2:0,y2:1, colorStops: [{ offset:0, color:'rgba(79,172,254,.2)' }, { offset:1, color:'rgba(79,172,254,.02)' }] } },
        symbol: 'none'
      }
    ]
  })

  // mAP chart
  const mapChart = echarts.init(mapChartRef.value, null, { renderer: 'svg' })
  mapChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', backgroundColor: '#1a2050', borderColor: 'rgba(102,126,234,.3)', textStyle: { color: '#e2e8f0', fontSize: 12 } },
    legend: { data: ['mAP50', 'mAP50-95'], textStyle: { color: '#94a3b8', fontSize: 11 }, top: 0 },
    grid: { top: 32, left: 40, right: 16, bottom: 24 },
    xAxis: { type: 'category', data: epochs, axisLine: { lineStyle: { color: 'rgba(102,126,234,.2)' } }, axisLabel: { color: '#64748b', fontSize: 11 } },
    yAxis: { type: 'value', min: 0, max: 1, axisLine: { show: false }, splitLine: { lineStyle: { color: 'rgba(102,126,234,.08)' } }, axisLabel: { color: '#64748b', fontSize: 11 } },
    series: [
      {
        name: 'mAP50', type: 'line', smooth: true,
        data: epochs.map((_, i) => +(0.3 + i * 0.03 + Math.random() * 0.02).toFixed(3)),
        lineStyle: { color: '#43e97b', width: 2 },
        itemStyle: { color: '#43e97b' },
        areaStyle: { color: { type: 'linear', x:0,y:0,x2:0,y2:1, colorStops: [{ offset:0, color:'rgba(67,233,123,.25)' }, { offset:1, color:'rgba(67,233,123,.02)' }] } },
        symbol: 'none'
      },
      {
        name: 'mAP50-95', type: 'line', smooth: true,
        data: epochs.map((_, i) => +(0.2 + i * 0.022 + Math.random() * 0.015).toFixed(3)),
        lineStyle: { color: '#f7971e', width: 2 },
        itemStyle: { color: '#f7971e' },
        areaStyle: { color: { type: 'linear', x:0,y:0,x2:0,y2:1, colorStops: [{ offset:0, color:'rgba(247,151,30,.2)' }, { offset:1, color:'rgba(247,151,30,.02)' }] } },
        symbol: 'none'
      }
    ]
  })
}
</script>

<style lang="scss" scoped>
.training-page {
  height: 100%;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: #0f1535;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  .sub-title { font-size: 13px; color: #64748b; }
}

.card {
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(102,126,234,.15);
  border-radius: 12px;
  overflow: hidden;
}

.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(102,126,234,.1);
  font-size: 14px;
  font-weight: 600;
  color: #e2e8f0;
}

.table-card { overflow: visible; }

.task-name-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #e2e8f0;
  font-size: 13.5px;
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pct-text {
  font-size: 12px;
  color: #94a3b8;
  min-width: 32px;
}

.status-dot {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 500;
  i {
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: currentColor;
  }
  &.running { color: #667eea; i { animation: pulse 1.5s ease-in-out infinite; } }
  &.done    { color: #4ade80; }
  &.failed  { color: #f87171; }
  &.queued  { color: #fb923c; }
}

@keyframes pulse {
  0%,100% { opacity: 1; transform: scale(1); }
  50%      { opacity: .5; transform: scale(1.3); }
}

/* Monitor panel */
.monitor-panel {
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(102,126,234,.15);
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.monitor-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #e2e8f0;
}

/* Metric cards */
.metric-cards {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-bottom: 1px solid rgba(102,126,234,.1);
}

.metric-card {
  flex: 1;
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(102,126,234,.12);
  border-radius: 10px;
  padding: 14px 16px;
  .mc-label { font-size: 11px; color: #64748b; margin-bottom: 6px; font-weight: 500; text-transform: uppercase; letter-spacing: .5px; }
  .mc-value { font-size: 24px; font-weight: 700; color: #e2e8f0; line-height: 1; margin-bottom: 6px; }
  .mc-trend {
    display: flex; align-items: center; gap: 3px;
    font-size: 11px; font-weight: 500;
    .el-icon { font-size: 11px; }
    &.up   { color: #4ade80; }
    &.down { color: #f87171; }
  }
}

/* Charts */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 16px;
  border-bottom: 1px solid rgba(102,126,234,.1);
}

.chart-card { padding: 14px; }

.chart-title {
  font-size: 13px;
  font-weight: 600;
  color: #94a3b8;
  margin-bottom: 10px;
}

.chart-box { height: 200px; }

/* Bottom row */
.bottom-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 16px;
}

.matrix-card { padding: 0; }

.matrix-grid {
  display: flex;
  gap: 8px;
  padding: 14px;
}

.matrix-labels-y {
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  padding-bottom: 24px;
  span { font-size: 11px; color: #94a3b8; text-align: right; min-width: 44px; }
}

.matrix-cells { flex: 1; }

.matrix-row { display: flex; gap: 3px; margin-bottom: 3px; }

.matrix-cell {
  flex: 1;
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  border-radius: 4px;
  min-width: 36px;
  min-height: 36px;
}

.matrix-labels-x {
  display: flex;
  gap: 3px;
  margin-top: 4px;
  span { flex: 1; font-size: 11px; color: #94a3b8; text-align: center; min-width: 36px; }
}

.matrix-legend {
  text-align: center;
  font-size: 11px;
  color: #64748b;
  padding: 0 14px 12px;
}

/* Ops card */
.ops-card { padding: 0; }

.ops-list { padding: 8px; display: flex; flex-direction: column; gap: 2px; }

.ops-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background .2s;
  &:hover { background: rgba(102,126,234,.08); }
}

.ops-icon {
  width: 36px; height: 36px;
  border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  .el-icon { font-size: 17px; }
}

.ops-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  .ops-name { font-size: 13.5px; font-weight: 500; color: #e2e8f0; }
  .ops-desc { font-size: 11.5px; color: #64748b; }
}

.ops-arrow { font-size: 13px; color: rgba(148,163,184,.4); }
</style>
