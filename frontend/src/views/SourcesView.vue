<template>
  <v-card>
    <v-card-title class="d-flex align-center justify-space-between">
      <div class="d-flex align-center">
        <span>pip 源</span>
        <v-chip class="ml-3" size="small" variant="outlined">{{ sources.length }}</v-chip>
      </div>
      <div class="d-flex ga-2">
        <v-btn color="primary" @click="showSetSourceDialog = true"><v-icon start>mdi-cog</v-icon>设置源</v-btn>
        <v-btn color="error" @click="resetSources" :loading="loading"><v-icon start>mdi-refresh</v-icon>重置</v-btn>
      </div>
    </v-card-title>

    <v-card-text>
      <v-list v-if="sources.length" class="elevation-0">
        <v-list-item v-for="(src, i) in sources" :key="i" class="mb-2 rounded-lg" :style="{ border: '1px solid rgb(var(--v-theme-surface-variant))' }">
          <template v-slot:prepend>
            <v-avatar color="primary" variant="tonal" size="40" class="mr-3">
              <v-icon color="primary">mdi-web</v-icon>
            </v-avatar>
          </template>
          <v-list-item-title class="font-weight-medium">{{ src.name }}</v-list-item-title>
          <v-list-item-subtitle class="text-truncate">{{ src.url }}</v-list-item-subtitle>
          <template v-slot:append>
            <v-btn size="small" color="error" variant="tonal" @click="removeSource(src.url)">删除</v-btn>
          </template>
        </v-list-item>
      </v-list>
      <div v-else class="text-center py-8 text-medium-emphasis">
        <v-icon size="64" class="mb-4">mdi-web-off</v-icon>
        <div>暂无配置的源</div>
      </div>
    </v-card-text>

    <v-dialog v-model="showSetSourceDialog" max-width="500">
      <v-card>
        <v-card-title>设置源</v-card-title>
        <v-card-text>
          <v-select v-model="selectedSource" :items="presetSources" item-title="name" item-value="index_url" label="选择源" variant="outlined" clearable></v-select>
          <v-select v-model="selectedExtraSource" :items="presetSources" item-title="name" item-value="index_url" label="备用源 (可选)" variant="outlined" clearable></v-select>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showSetSourceDialog = false">取消</v-btn>
          <v-btn color="primary" @click="applySource" :loading="loading">应用</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup>
import { ref, inject, onMounted } from 'vue'
import { sourcesApi } from '@/api'

const showToast = inject('showToast')
const sources = ref([])
const loading = ref(false)
const showSetSourceDialog = ref(false)
const selectedSource = ref(null)
const selectedExtraSource = ref(null)

const presetSources = [
  { name: '官方 PyPI', index_url: 'https://pypi.org/simple' },
  { name: '阿里云', index_url: 'https://mirrors.aliyun.com/pypi/simple' },
  { name: '腾讯云', index_url: 'https://mirrors.cloud.tencent.com/pypi/simple' },
  { name: '清华大学', index_url: 'https://pypi.tuna.tsinghua.edu.cn/simple' },
  { name: '豆瓣', index_url: 'https://pypi.doubanio.com/simple' },
  { name: '中科大', index_url: 'https://pypi.mirrors.ustc.edu.cn/simple' },
]

const loadSources = async () => {
  loading.value = true
  const res = await sourcesApi.list()
  if (res) sources.value = res.sources || []
  loading.value = false
}

const applySource = async () => {
  if (!selectedSource.value) return showToast('请选择源', 'error')
  loading.value = true
  showSetSourceDialog.value = false
  const extraSources = selectedExtraSource.value && selectedExtraSource.value !== selectedSource.value ? [selectedExtraSource.value] : null
  const res = await sourcesApi.set(selectedSource.value, extraSources)
  if (res?.message) { showToast('设置成功'); loadSources() }
  else showToast('设置失败', 'error')
  loading.value = false
}

const removeSource = async (url) => {
  loading.value = true
  const res = await sourcesApi.remove(url)
  if (res?.message) { showToast('删除成功'); loadSources() }
  else showToast('删除失败', 'error')
  loading.value = false
}

const resetSources = async () => {
  loading.value = true
  const res = await sourcesApi.reset()
  if (res?.message) { showToast('重置成功'); loadSources() }
  else showToast('重置失败', 'error')
  loading.value = false
}

onMounted(loadSources)
</script>
