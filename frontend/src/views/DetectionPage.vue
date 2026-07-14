<template>
  <div class="detection-page">
    <div class="page-header">
      <span class="sub-title">拖拽或点击上传图片，支持单张、多张、ZIP 批量检测</span>
      <div class="header-actions">
        <el-select v-model="selectedModel" size="small" style="width:160px">
          <el-option v-for="m in modelList" :key="m.value" :label="m.label" :value="m.value" />
        </el-select>
        <el-select v-model="selectedScene" size="small" style="width:130px">
          <el-option label="交通场景" value="traffic" />
          <el-option label="遥感场景" value="remote" />
          <el-option label="工业场景" value="industry" />
        </el-select>
      </div>
    </div>

    <div class="main-area">
      <div class="left-col">
        <div
          class="upload-zone"
          :class="[{ dragging: isDragging }, { 'has-files': uploadedFiles.length > 0 }]"
          @dragover.prevent="isDragging = true"
          @dragleave="isDragging = false"
          @drop.prevent="onDrop"
          @click="triggerUpload"
        >
          <input ref="uploadRef" type="file" multiple accept="image/*,.zip" style="display:none" @change="onFileSelect" />
          <div class="upload-content" v-if="!detecting">
            <div class="upload-icon">
              <el-icon><UploadFilled /></el-icon>
            </div>
            <p class="upload-text">点击或拖拽上传图片 / ZIP</p>
            <p class="upload-hint">支持 JPG、PNG、BMP、ZIP，单次最多 20 张</p>
            <div class="upload-tags">
              <span>单图检测</span>
              <span>批量检测</span>
              <span>ZIP 包检测</span>
            </div>
          </div>
          <div class="detecting-anim" v-else>
            <div class="scan-ring"></div>
            <el-icon class="scan-icon"><Search /></el-icon>
            <p>正在检测中... {{ detectedCount }}/{{ totalCount }}</p>
          </div>
        </div>

        <div v-if="uploadedFiles.length" class="file-list-bar">
          <span class="fl-label">已选 {{ uploadedFiles.length }} 个文件</span>
          <div class="fl-thumbs">
            <div v-for="(f, i) in uploadedFiles.slice(0, 6)" :key="i" class="fl-thumb">
              <img :src="f.preview" :alt="f.name" />
            </div>
            <div v-if="uploadedFiles.length > 6" class="fl-more">+{{ uploadedFiles.length - 6 }}</div>
          </div>
          <div class="fl-actions">
            <el-button size="small" type="primary" :loading="detecting" @click="startDetection">开始检测</el-button>
            <el-button size="small" @click="clearFiles">清空</el-button>
          </div>
        </div>
      </div>

      <div class="right-col">
        <div class="results-header">
          <span class="results-title">检测结果</span>
          <div class="results-meta" v-if="results.length">
            <el-tag size="small" type="success">{{ results.length }} 张已完成</el-tag>
            <el-button size="small" text type="primary" @click="exportAll">
              <el-icon><Download /></el-icon>导出全部
            </el-button>
          </div>
        </div>

        <div v-if="!results.length" class="empty-state">
          <el-icon class="empty-icon"><PictureFilled /></el-icon>
          <p>暂无检测结果</p>
          <span>上传图片后，检测结果将在此展示</span>
        </div>

        <div v-else class="result-grid">
          <div v-for="(item, i) in results" :key="i" class="result-card" @click="openDetail(item)">
            <div class="rc-img-wrap">
              <img :src="item.image" :alt="item.name" />
              <div class="rc-overlay">
                <el-icon><ZoomIn /></el-icon>
                <span>查看详情</span>
              </div>
              <div class="rc-badge">{{ item.total }} 目标</div>
            </div>
            <div class="rc-info">
              <span class="rc-name">{{ item.name }}</span>
              <span class="rc-time">{{ item.time }}</span>
            </div>
            <div class="rc-tags">
              <span
                v-for="(cls, ci) in item.classes.slice(0, 3)"
                :key="ci"
                class="rc-tag"
                :style="{ background: cls.color + '22', color: cls.color }"
              >
                {{ cls.name }}×{{ cls.count }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="showDetail" width="760px" :title="detailItem?.name">
      <div v-if="detailItem" class="detail-body">
        <div class="detail-img">
          <img :src="detailItem.image" alt="检测结果" />
        </div>
        <div class="detail-info">
          <div class="di-title">目标统计</div>
          <div class="di-total">共 <strong>{{ detailItem.total }}</strong> 个目标</div>
          <div class="di-row" v-for="(cls, i) in detailItem.classes" :key="i">
            <span class="di-dot" :style="{ background: cls.color }"></span>
            <span class="di-name">{{ cls.name }}</span>
            <div class="di-bar">
              <div class="di-fill" :style="{ width: cls.pct + '%', background: cls.color }"></div>
            </div>
            <span class="di-cnt">{{ cls.count }}</span>
          </div>
          <div class="di-meta">
            <div><span>模型</span><strong>{{ selectedModel }}</strong></div>
            <div><span>耗时</span><strong>{{ detailItem.time }}</strong></div>
            <div><span>置信度</span><strong>≥ 0.50</strong></div>
            <div><span>图像尺寸</span><strong>640×640</strong></div>
          </div>
          <el-button type="primary" style="width:100%;margin-top:12px" @click="downloadResult(detailItem)">
            <el-icon><Download /></el-icon>下载标注图
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const selectedModel = ref('fogtraffic_v1')
const selectedScene = ref('traffic')
const isDragging = ref(false)
const detecting = ref(false)
const detectedCount = ref(0)
const totalCount = ref(0)
const uploadRef = ref(null)
const showDetail = ref(false)
const detailItem = ref(null)

const modelList = [
  { label: 'fogtraffic_v1 (YOLOv11n)', value: 'fogtraffic_v1' },
  { label: 'fogtraffic_v2 (YOLOv11s)', value: 'fogtraffic_v2' },
  { label: 'remote_v1 (YOLOv11m)', value: 'remote_v1' }
]

const uploadedFiles = reactive([])
const results = reactive([])

const COLORS = ['#667eea', '#f093fb', '#4facfe', '#43e97b', '#f7971e', '#fa709a']
const CLASSES = ['轿车', '卡车', '行人', '摩托车', '公交车', '自行车']

function triggerUpload() {
  if (detecting.value) return
  uploadRef.value?.click()
}

function onFileSelect(e) {
  handleFiles(Array.from(e.target.files))
  e.target.value = ''
}

function onDrop(e) {
  isDragging.value = false
  handleFiles(Array.from(e.dataTransfer.files))
}

function handleFiles(files) {
  const imgs = files.filter(f => f.type.startsWith('image/') || f.name.endsWith('.zip'))
  imgs.forEach(f => {
    const preview = f.type.startsWith('image/') ? URL.createObjectURL(f) : ''
    uploadedFiles.push({ name: f.name, preview, file: f })
  })
  if (imgs.length) ElMessage.success(`已添加 ${imgs.length} 个文件`)
}

function clearFiles() {
  uploadedFiles.splice(0)
}

async function startDetection() {
  if (!uploadedFiles.length) return
  detecting.value = true
  detectedCount.value = 0
  totalCount.value = uploadedFiles.length

  for (let i = 0; i < uploadedFiles.length; i++) {
    await new Promise(r => setTimeout(r, 600))
    detectedCount.value = i + 1
    const f = uploadedFiles[i]
    if (!f.preview) continue

    const clsCount = Math.floor(Math.random() * 3) + 1
    const classes = Array.from({ length: clsCount }, (_, ci) => ({
      name: CLASSES[Math.floor(Math.random() * CLASSES.length)],
      count: Math.floor(Math.random() * 4) + 1,
      color: COLORS[ci % COLORS.length],
      pct: 0
    }))
    const total = classes.reduce((s, c) => s + c.count, 0)
    classes.forEach(c => { c.pct = Math.round(c.count / total * 100) })

    results.unshift({
      image: f.preview,
      name: f.name,
      total,
      classes,
      time: (Math.random() * 0.4 + 0.1).toFixed(2) + 's'
    })
  }

  detecting.value = false
  uploadedFiles.splice(0)
  ElMessage.success('检测完成！')
}

function openDetail(item) {
  detailItem.value = item
  showDetail.value = true
}

function downloadResult(item) {
  ElMessage.success('开始下载标注图：' + item.name)
}

function exportAll() {
  ElMessage.success('正在导出全部检测结果...')
}
</script>

<style lang="scss" scoped>
.detection-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px;
  gap: 16px;
  background: #0f1535;
  overflow: hidden;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
  .sub-title { font-size: 13px; color: #64748b; }
  .header-actions { display: flex; gap: 8px; }
}

.main-area {
  flex: 1;
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 16px;
  overflow: hidden;
  min-height: 0;
}

.left-col {
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow: hidden;
}

.upload-zone {
  flex: 1;
  border: 2px dashed rgba(102, 126, 234, .35);
  border-radius: 14px;
  background: rgba(102, 126, 234, .04);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all .25s;
  position: relative;
  overflow: hidden;
  min-height: 240px;

  &:hover,
  &.dragging {
    border-color: #667eea;
    background: rgba(102, 126, 234, .1);
    .upload-icon .el-icon { transform: scale(1.1); color: #667eea; }
  }

  &.dragging {
    box-shadow: 0 0 0 4px rgba(102, 126, 234, .2);
  }

  animation: breathe 2.5s ease-in-out infinite;
  &:hover { animation: none; }
}

.upload-content,
.detecting-anim {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  text-align: center;
  color: #cbd5e1;
}

.upload-icon {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: rgba(102, 126, 234, .14);
  display: grid;
  place-items: center;
  margin-bottom: 4px;
  .el-icon { font-size: 30px; color: #667eea; transition: all .25s; }
}

.upload-text { font-size: 17px; font-weight: 600; color: #e2e8f0; margin: 0; }
.upload-hint { font-size: 13px; color: #64748b; margin: 0; }
.upload-tags { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin-top: 6px; span { padding: 4px 8px; border-radius: 999px; background: rgba(255,255,255,.06); font-size: 12px; color: #94a3b8; } }
.scan-ring { width: 70px; height: 70px; border-radius: 50%; border: 3px solid rgba(102,126,234,.3); border-top-color: #667eea; animation: spin 1s linear infinite; }
.scan-icon { font-size: 30px; color: #667eea; }
@keyframes breathe { 0%, 100% { border-color: rgba(102,126,234,.35); } 50% { border-color: rgba(102,126,234,.65); } }
@keyframes spin { to { transform: rotate(360deg); } }

.file-list-bar { display: flex; align-items: center; justify-content: space-between; padding: 10px 12px; background: rgba(255,255,255,.05); border: 1px solid rgba(255,255,255,.08); border-radius: 12px; gap: 10px; }
.fl-label { font-size: 12px; color: #94a3b8; }
.fl-thumbs { display: flex; align-items: center; gap: 8px; flex: 1; overflow: hidden; }
.fl-thumb { width: 40px; height: 40px; border-radius: 10px; overflow: hidden; border: 1px solid rgba(255,255,255,.08); flex-shrink: 0; img { width: 100%; height: 100%; object-fit: cover; } }
.fl-more { font-size: 12px; color: #667eea; }
.fl-actions { display: flex; gap: 8px; }

.right-col { display: flex; flex-direction: column; background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.08); border-radius: 16px; padding: 16px; overflow: hidden; min-height: 0; }
.results-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.results-title { font-size: 16px; font-weight: 600; color: #e2e8f0; }
.results-meta { display: flex; align-items: center; gap: 10px; }
.empty-state { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #64748b; gap: 8px; .empty-icon { font-size: 44px; color: #667eea; } p { margin: 0; font-size: 16px; color: #cbd5e1; } span { font-size: 13px; } }
.result-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; overflow: auto; padding-right: 4px; }
.result-card { border: 1px solid rgba(255,255,255,.08); border-radius: 12px; overflow: hidden; background: rgba(255,255,255,.05); cursor: pointer; transition: transform .2s, border-color .2s; &:hover { transform: translateY(-2px); border-color: rgba(102,126,234,.4); } }
.rc-img-wrap { position: relative; aspect-ratio: 4/3; background: #111827; img { width: 100%; height: 100%; object-fit: cover; } }
.rc-overlay { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px; background: rgba(0,0,0,.45); color: #fff; opacity: 0; transition: opacity .2s; .result-card:hover & { opacity: 1; } }
.rc-badge { position: absolute; top: 10px; left: 10px; padding: 4px 8px; border-radius: 999px; background: rgba(0,0,0,.65); color: #fff; font-size: 12px; }
.rc-info { padding: 10px 10px 6px; display: flex; flex-direction: column; gap: 4px; }
.rc-name { font-size: 13px; color: #e2e8f0; font-weight: 600; }
.rc-time { font-size: 12px; color: #64748b; }
.rc-tags { display: flex; flex-wrap: wrap; gap: 6px; padding: 0 10px 10px; }
.rc-tag { font-size: 11px; padding: 3px 7px; border-radius: 999px; }
.detail-body { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.detail-img img { width: 100%; border-radius: 10px; }
.detail-info { display: flex; flex-direction: column; gap: 8px; }
.di-title { font-size: 16px; color: #e2e8f0; font-weight: 600; }
.di-total { font-size: 14px; color: #94a3b8; }
.di-row { display: grid; grid-template-columns: 10px 1fr 90px 34px; align-items: center; gap: 8px; font-size: 13px; color: #cbd5e1; }
.di-dot { width: 8px; height: 8px; border-radius: 50%; }
.di-bar { height: 6px; background: rgba(255,255,255,.08); border-radius: 999px; overflow: hidden; }
.di-fill { height: 100%; border-radius: 999px; }
.di-meta { margin-top: 8px; display: grid; grid-template-columns: 1fr 1fr; gap: 8px; div { padding: 8px 10px; background: rgba(255,255,255,.05); border-radius: 8px; display: flex; flex-direction: column; gap: 4px; span { font-size: 12px; color: #64748b; } strong { font-size: 13px; color: #e2e8f0; } } }
</style>
