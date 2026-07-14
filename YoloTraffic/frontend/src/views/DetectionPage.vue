<template>
  <div class="detection-page">
    <div class="page-header">
      <span class="sub-title">拖拽或点击上传图片，支持单张、多张、ZIP 批量检测</span>
      <div class="header-actions">
        <el-select v-model="selectedModel" size="small" style="width:160px">
          <el-option v-for="m in modelList" :key="m.value" :label="m.label" :value="m.value"/>
        </el-select>
        <el-select v-model="selectedScene" size="small" style="width:130px">
          <el-option label="交通场景" value="traffic"/>
          <el-option label="遥感场景" value="remote"/>
          <el-option label="工业场景" value="industry"/>
        </el-select>
      </div>
    </div>

    <div class="main-area">
      <!-- Left: upload + results -->
      <div class="left-col">
        <!-- Upload zone -->
        <div
          class="upload-zone"
          :class="{ dragging: isDragging, has-files: uploadedFiles.length > 0 }"
          @dragover.prevent="isDragging=true"
          @dragleave="isDragging=false"
          @drop.prevent="onDrop"
          @click="triggerUpload"
        >
          <input ref="uploadRef" type="file" multiple accept="image/*,.zip" style="display:none" @change="onFileSelect"/>
          <div class="upload-content" v-if="!detecting">
            <div class="upload-icon">
              <el-icon><UploadFilled/></el-icon>
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
            <el-icon class="scan-icon"><Search/></el-icon>
            <p>正在检测中... {{ detectedCount }}/{{ totalCount }}</p>
          </div>
        </div>

        <!-- File list preview -->
        <div v-if="uploadedFiles.length" class="file-list-bar">
          <span class="fl-label">已选 {{ uploadedFiles.length }} 个文件</span>
          <div class="fl-thumbs">
            <div v-for="(f,i) in uploadedFiles.slice(0,6)" :key="i" class="fl-thumb">
              <img :src="f.preview" :alt="f.name"/>
            </div>
            <div v-if="uploadedFiles.length>6" class="fl-more">+{{ uploadedFiles.length-6 }}</div>
          </div>
          <div class="fl-actions">
            <el-button size="small" type="primary" :loading="detecting" @click="startDetection">
              开始检测
            </el-button>
            <el-button size="small" @click="clearFiles">清空</el-button>
          </div>
        </div>
      </div>

      <!-- Right: result gallery -->
      <div class="right-col">
        <div class="results-header">
          <span class="results-title">检测结果</span>
          <div class="results-meta" v-if="results.length">
            <el-tag size="small" type="success">{{ results.length }} 张已完成</el-tag>
            <el-button size="small" text type="primary" @click="exportAll">
              <el-icon><Download/></el-icon>导出全部
            </el-button>
          </div>
        </div>

        <!-- Empty state -->
        <div v-if="!results.length" class="empty-state">
          <el-icon class="empty-icon"><PictureFilled/></el-icon>
          <p>暂无检测结果</p>
          <span>上传图片后，检测结果将在此展示</span>
        </div>

        <!-- Result grid -->
        <div v-else class="result-grid">
          <div
            v-for="(item, i) in results"
            :key="i"
            class="result-card"
            @click="openDetail(item)"
          >
            <div class="rc-img-wrap">
              <img :src="item.image" :alt="item.name"/>
              <div class="rc-overlay">
                <el-icon><ZoomIn/></el-icon>
                <span>查看详情</span>
              </div>
              <div class="rc-badge">{{ item.total }} 目标</div>
            </div>
            <div class="rc-info">
              <span class="rc-name">{{ item.name }}</span>
              <span class="rc-time">{{ item.time }}</span>
            </div>
            <div class="rc-tags">
              <span v-for="(cls,ci) in item.classes.slice(0,3)" :key="ci"
                class="rc-tag" :style="{ background: cls.color+'22', color: cls.color }">
                {{ cls.name }}×{{ cls.count }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Detail Dialog -->
    <el-dialog v-model="showDetail" width="760px" :title="detailItem?.name">
      <div v-if="detailItem" class="detail-body">
        <div class="detail-img">
          <img :src="detailItem.image" alt="检测结果"/>
        </div>
        <div class="detail-info">
          <div class="di-title">目标统计</div>
          <div class="di-total">共 <strong>{{ detailItem.total }}</strong> 个目标</div>
          <div class="di-row" v-for="(cls,i) in detailItem.classes" :key="i">
            <span class="di-dot" :style="{ background: cls.color }"></span>
            <span class="di-name">{{ cls.name }}</span>
            <div class="di-bar">
              <div class="di-fill" :style="{ width: cls.pct+'%', background: cls.color }"></div>
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
            <el-icon><Download/></el-icon>下载标注图
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
const isDragging    = ref(false)
const detecting     = ref(false)
const detectedCount = ref(0)
const totalCount    = ref(0)
const uploadRef     = ref(null)
const showDetail    = ref(false)
const detailItem    = ref(null)

const modelList = [
  { label: 'fogtraffic_v1 (YOLOv11n)', value: 'fogtraffic_v1' },
  { label: 'fogtraffic_v2 (YOLOv11s)', value: 'fogtraffic_v2' },
  { label: 'remote_v1 (YOLOv11m)',      value: 'remote_v1'     },
]

const uploadedFiles = reactive([])
const results       = reactive([])

const COLORS = ['#667eea','#f093fb','#4facfe','#43e97b','#f7971e','#fa709a']
const CLASSES = ['轿车','卡车','行人','摩托车','公交车','自行车']

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
  detecting.value   = true
  detectedCount.value = 0
  totalCount.value    = uploadedFiles.length

  for (let i = 0; i < uploadedFiles.length; i++) {
    await new Promise(r => setTimeout(r, 600))
    detectedCount.value = i + 1
    const f = uploadedFiles[i]
    if (!f.preview) continue

    const clsCount = Math.floor(Math.random() * 3) + 1
    const classes  = Array.from({ length: clsCount }, (_, ci) => ({
      name: CLASSES[Math.floor(Math.random() * CLASSES.length)],
      count: Math.floor(Math.random() * 4) + 1,
      color: COLORS[ci % COLORS.length],
      pct: 0
    }))
    const total = classes.reduce((s, c) => s + c.count, 0)
    classes.forEach(c => { c.pct = Math.round(c.count / total * 100) })

    results.unshift({
      image: f.preview,
      name:  f.name,
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

/* Upload zone */
.upload-zone {
  flex: 1;
  border: 2px dashed rgba(102,126,234,.35);
  border-radius: 14px;
  background: rgba(102,126,234,.04);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all .25s;
  position: relative;
  overflow: hidden;
  min-height: 240px;

  &:hover, &.dragging {
    border-color: #667eea;
    background: rgba(102,126,234,.1);
    .upload-icon .el-icon { transform: scale(1.1); color: #667eea; }
  }

  &.dragging {
    box-shadow: 0 0 0 4px rgba(102,126,234,.2);
  }

  /* Breathing animation on border */
  @keyframes breathe {
    0%,100% { border-color: rgba(102,126,234,.35); }
    50%      { border-color: rgba(102,126,234,.65); }
  }
  animation: breathe 2.5s ease-in-out infinite;
  &:hover { animation: none; }
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 24px;
  text-align: center;
}

.upload-icon {
  width: 64px; height: 64px;
  border-radius: 16px;
  background: rgba(102,126,234,.12);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 4px;
  .el-icon { font-size: 30px; color: rgba(102,126,234,.7); transition: all .2s; }
}

.upload-text { font-size: 15px; font-weight: 600; color: #e2e8f0; }
.upload-hint { font-size: 12px; color: #64748b; }

.upload-tags {
  display: flex; gap: 8px; margin-top: 4px;
  span {
    padding: 3px 10px;
    background: rgba(102,126,234,.12);
    border: 1px solid rgba(102,126,234,.25);
    border-radius: 12px;
    font-size: 11.5px;
    color: #94a3b8;
  }
}

/* Detecting animation */
.detecting-anim {
  display: flex; flex-direction: column; align-items: center; gap: 14px;
  position: relative;
  p { font-size: 13px; color: #94a3b8; }
}

.scan-ring {
  width: 80px; height: 80px; border-radius: 50%;
  border: 3px solid rgba(102,126,234,.2);
  border-top-color: #667eea;
  animation: spin 1s linear infinite;
  position: absolute;
  top: 50%; left: 50%; transform: translate(-50%,-50%);
}

.scan-icon {
  font-size: 28px; color: #667eea;
  position: relative; z-index: 1;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* File list bar */
.file-list-bar {
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(102,126,234,.15);
  border-radius: 10px;
  padding: 10px 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.fl-label { font-size: 12px; color: #94a3b8; flex-shrink: 0; }

.fl-thumbs {
  display: flex; gap: 4px; flex: 1;
}

.fl-thumb {
  width: 32px; height: 32px; border-radius: 6px; overflow: hidden; flex-shrink: 0;
  img { width: 100%; height: 100%; object-fit: cover; }
}

.fl-more {
  width: 32px; height: 32px; border-radius: 6px; flex-shrink: 0;
  background: rgba(102,126,234,.15);
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; color: #94a3b8;
}

.fl-actions { display: flex; gap: 6px; flex-shrink: 0; }

/* Right col */
.right-col {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.results-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 12px; flex-shrink: 0;
}

.results-title { font-size: 14px; font-weight: 600; color: #e2e8f0; }
.results-meta  { display: flex; align-items: center; gap: 10px; }

.empty-state {
  flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 10px; color: #64748b;
  .empty-icon { font-size: 48px; color: rgba(102,126,234,.25); }
  p { font-size: 14px; font-weight: 500; color: #94a3b8; }
  span { font-size: 12px; }
}

.result-grid {
  flex: 1; overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  gap: 12px;
  align-content: start;
}

.result-card {
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(102,126,234,.15);
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: all .2s;
  &:hover {
    border-color: rgba(102,126,234,.4);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,.2);
    .rc-overlay { opacity: 1; }
  }
}

.rc-img-wrap {
  position: relative; height: 120px;
  img { width: 100%; height: 100%; object-fit: cover; }
}

.rc-overlay {
  position: absolute; inset: 0;
  background: rgba(102,126,234,.75);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 6px; opacity: 0; transition: opacity .2s;
  .el-icon { font-size: 22px; color: #fff; }
  span { font-size: 12px; color: #fff; font-weight: 500; }
}

.rc-badge {
  position: absolute; top: 6px; right: 6px;
  background: rgba(102,126,234,.85);
  color: #fff; font-size: 11px; font-weight: 600;
  padding: 2px 7px; border-radius: 10px;
}

.rc-info {
  display: flex; align-items: center; justify-content: space-between;
  padding: 7px 10px 4px;
  .rc-name { font-size: 12px; color: #e2e8f0; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100px; }
  .rc-time { font-size: 11px; color: #64748b; }
}

.rc-tags {
  display: flex; gap: 4px; padding: 0 8px 8px; flex-wrap: wrap;
  .rc-tag { font-size: 11px; padding: 1px 7px; border-radius: 8px; font-weight: 500; }
}

/* Detail dialog */
.detail-body { display: flex; gap: 16px; }
.detail-img {
  flex: 1; border-radius: 10px; overflow: hidden; background: rgba(0,0,0,.3);
  img { width: 100%; display: block; border-radius: 10px; }
}
.detail-info { width: 200px; flex-shrink: 0; display: flex; flex-direction: column; gap: 10px; }
.di-title { font-size: 12px; color: #64748b; font-weight: 500; text-transform: uppercase; }
.di-total { font-size: 20px; font-weight: 700; color: #e2e8f0; strong { color: #667eea; } }
.di-row {
  display: flex; align-items: center; gap: 6px; font-size: 12.5px;
  .di-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
  .di-name { color: #cbd5e1; min-width: 36px; }
  .di-bar { flex: 1; height: 4px; background: rgba(255,255,255,.07); border-radius: 2px; overflow: hidden; }
  .di-fill { height: 100%; border-radius: 2px; }
  .di-cnt { font-weight: 600; color: #e2e8f0; min-width: 16px; text-align: right; }
}
.di-meta {
  background: rgba(255,255,255,.04); border-radius: 8px; padding: 10px;
  display: flex; flex-direction: column; gap: 6px;
  div { display: flex; justify-content: space-between; font-size: 12px; span { color: #64748b; } strong { color: #e2e8f0; } }
}
