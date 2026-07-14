<template>
  <div class="history-page">
    <!-- Filter bar -->
    <div class="filter-bar">
      <el-input
        v-model="search"
        placeholder="搜索文件名..."
        prefix-icon="Search"
        size="small"
        style="width:220px"
        clearable
      />
      <el-select
        v-model="filterScene"
        size="small"
        style="width:120px"
        placeholder="场景"
      >
        <el-option label="全部场景" value="" />
        <el-option label="交通场景" value="交通" />
        <el-option label="遥感场景" value="遥感" />
        <el-option label="工业场景" value="工业" />
      </el-select>
      <el-select
        v-model="filterModel"
        size="small"
        style="width:180px"
        placeholder="模型"
      >
        <el-option label="全部模型" value="" />
        <el-option label="fogtraffic_v1" value="fogtraffic_v1" />
        <el-option label="fogtraffic_v2" value="fogtraffic_v2" />
        <el-option label="remote_v1" value="remote_v1" />
      </el-select>
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        size="small"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        style="width:240px"
      />
      <el-button size="small" @click="resetFilter">
        <el-icon><Refresh /></el-icon>重置
      </el-button>
      <div style="flex:1"></div>
      <el-button size="small" type="primary" @click="exportCSV">
        <el-icon><Download /></el-icon>导出 CSV
      </el-button>
    </div>

    <!-- Stats row -->
    <div class="quick-stats">
      <div class="qs-item" v-for="s in quickStats" :key="s.label">
        <span class="qs-v">{{ s.value }}</span>
        <span class="qs-l">{{ s.label }}</span>
      </div>
    </div>

    <!-- Table -->
    <div class="card table-wrap">
      <el-table
        :data="filteredRecords"
        style="width:100%"
        height="100%"
        @row-click="openDetail"
      >
        <el-table-column type="index" label="#" width="50" />
        <el-table-column prop="filename" label="文件名" min-width="160">
          <template #default="{ row }">
            <div class="filename-cell">
              <div class="file-thumb">
                <el-icon><PictureFilled /></el-icon>
              </div>
              <span>{{ row.filename }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="scene" label="检测场景" width="90" />
        <el-table-column prop="model" label="使用模型" width="160" />
        <el-table-column prop="total" label="目标数量" width="80">
          <template #default="{ row }">
            <el-tag size="small" type="primary">{{ row.total }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="主要类别" min-width="180">
          <template #default="{ row }">
            <div class="cls-tags">
              <span
                v-for="(c,i) in row.classes.slice(0,3)"
                :key="i"
                class="cls-tag"
                :style="{ background: c.color+'22', color: c.color }"
              >
                {{ c.name }}×{{ c.count }}
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="inferTime" label="推理耗时" width="90" />
        <el-table-column prop="time" label="检测时间" width="150" />
        <el-table-column label="操作" width="110" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text type="primary" @click.stop="openDetail(row)">详情</el-button>
            <el-button size="small" text type="danger" @click.stop="deleteRecord(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Pagination -->
    <div class="pagination-bar">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50]"
        :total="allRecords.length"
        layout="total, sizes, prev, pager, next"
        background
      />
    </div>

    <!-- Detail drawer -->
    <el-dialog v-model="showDetail" title="检测详情" width="680px">
      <div v-if="detailRow" class="detail-dialog">
        <div class="dd-img">
          <div class="dd-img-placeholder">
            <el-icon style="font-size:48px;color:rgba(102,126,234,.3)">
              <PictureFilled />
            </el-icon>
            <span>{{ detailRow.filename }}</span>
          </div>
        </div>
        <div class="dd-info">
          <div class="dd-row" v-for="item in detailMeta" :key="item.label">
            <span class="dd-label">{{ item.label }}</span>
            <span class="dd-val">{{ item.value }}</span>
          </div>
          <div class="dd-classes">
            <span class="dd-label">检测类别</span>
            <div class="dd-cls-list">
              <div
                v-for="(c,i) in detailRow.classes"
                :key="i"
                class="dd-cls-item"
              >
                <span class="dd-dot" :style="{ background: c.color }"></span>
                <span>{{ c.name }}</span>
                <span class="dd-cls-cnt">{{ c.count }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const search      = ref('')
const filterScene = ref('')
const filterModel = ref('')
const dateRange   = ref(null)
const currentPage = ref(1)
const pageSize    = ref(20)
const showDetail  = ref(false)
const detailRow   = ref(null)

const COLORS  = ['#667eea','#f093fb','#4facfe','#43e97b','#f7971e']
const CLASSES = ['轿车','卡车','行人','摩托车','公交车']

// Generate mock data
const allRecords = ref(
  Array.from({ length: 60 }, (_, i) => {
    const clsCount = Math.floor(Math.random() * 3) + 1
    const classes  = Array.from({ length: clsCount }, (_, ci) => ({
      name:  CLASSES[Math.floor(Math.random() * CLASSES.length)],
      count: Math.floor(Math.random() * 5) + 1,
      color: COLORS[ci % COLORS.length]
    }))
    const scenes = ['交通','遥感','工业']
    const models = ['fogtraffic_v1','fogtraffic_v2','remote_v1']
    const d = new Date(Date.now() - i * 3600000 * 4)
    return {
      id: i + 1,
      filename: `image_${String(i+1).padStart(3,'0')}.jpg`,
      scene:     scenes[i % 3],
      model:     models[i % 3],
      total:     classes.reduce((s,c) => s + c.count, 0),
      classes,
      inferTime: (Math.random() * 0.4 + 0.1).toFixed(2) + 's',
      time:      d.toLocaleString('zh-CN').slice(0,16)
    }
  })
)

const filteredRecords = computed(() => {
  let data = allRecords.value
  if (search.value)      data = data.filter(r => r.filename.includes(search.value))
  if (filterScene.value) data = data.filter(r => r.scene === filterScene.value)
  if (filterModel.value) data = data.filter(r => r.model === filterModel.value)
  const start = (currentPage.value - 1) * pageSize.value
  return data.slice(start, start + pageSize.value)
})

const quickStats = computed(() => [
  { label:'总记录数',   value: allRecords.value.length },
  { label:'今日检测',   value: 36 },
  { label:'总目标数',   value: allRecords.value.reduce((s,r) => s+r.total, 0) },
  { label:'平均耗时',   value: '0.28s' },
])

const detailMeta = computed(() => detailRow.value ? [
  { label:'文件名',   value: detailRow.value.filename  },
  { label:'检测场景', value: detailRow.value.scene      },
  { label:'使用模型', value: detailRow.value.model      },
  { label:'目标总数', value: detailRow.value.total      },
  { label:'推理耗时', value: detailRow.value.inferTime  },
  { label:'检测时间', value: detailRow.value.time       },
] : [])

function openDetail(row) {
  detailRow.value  = row
  showDetail.value = true
}

function deleteRecord(row) {
  ElMessageBox.confirm(`确认删除记录 ${row.filename}？`, '提示', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const idx = allRecords.value.findIndex(r => r.id === row.id)
    if (idx > -1) allRecords.value.splice(idx, 1)
    ElMessage.success('删除成功')
  }).catch(() => {})
}

function resetFilter() {
  search.value = ''; filterScene.value = ''; filterModel.value = ''; dateRange.value = null
}

function exportCSV() {
  ElMessage.success('CSV 文件导出成功')
}
</script>

<style lang="scss" scoped>
.history-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px;
  gap: 14px;
  background: #0f1535;
  overflow: hidden;
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
  flex-wrap: wrap;
}

.quick-stats {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

.qs-item {
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(102,126,234,.15);
  border-radius: 10px;
  padding: 10px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  .qs-v {
    font-size: 20px;
    font-weight: 700;
    color: #e2e8f0;
  }
  .qs-l {
    font-size: 11px;
    color: #64748b;
  }
}

.card {
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(102,126,234,.15);
  border-radius: 12px;
  overflow: hidden;
}

.table-wrap {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.filename-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  .file-thumb {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    background: rgba(102,126,234,.15);
    display: flex;
    align-items: center;
    justify-content: center;
    .el-icon {
      font-size: 14px;
      color: #667eea;
    }
  }
  span {
    font-size: 13px;
    color: #e2e8f0;
  }
}

.cls-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  .cls-tag {
    font-size: 11px;
    padding: 1px 7px;
    border-radius: 8px;
    font-weight: 500;
  }
}

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  flex-shrink: 0;
  padding: 4px 0;
}

/* Detail dialog */
.detail-dialog {
  display: flex;
  gap: 20px;
}
.dd-img {
  width: 280px;
  flex-shrink: 0;
  border-radius: 10px;
  overflow: hidden;
  background: rgba(0,0,0,.25);
  border: 1px solid rgba(102,126,234,.2);
}
.dd-img-placeholder {
  height: 220px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  span {
    font-size: 12px;
    color: #64748b;
  }
}
.dd-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.dd-row {
  display: flex;
  justify-content: space-between;
  padding: 7px 0;
  border-bottom: 1px solid rgba(102,126,234,.08);
  font-size: 13px;
  .dd-label {
    color: #64748b;
  }
  .dd-val {
    color: #e2e8f0;
    font-weight: 500;
  }
}
.dd-classes {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.dd-cls-list {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.dd-cls-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #cbd5e1;
  .dd-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
  }
  .dd-cls-cnt {
    margin-left: auto;
    font-weight: 600;
    color: #e2e8f0;
  }
}
</style>