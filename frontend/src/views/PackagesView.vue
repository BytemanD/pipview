<template>
  <div>
    <v-row class="mb-4">
      <v-col cols="2" v-for="stat in statCards" :key="stat.label">
        <v-card class="pa-3" :class="{ 'cursor-pointer': stat.clickable }" @click="stat.onClick && stat.onClick()">
          <div class="d-flex align-center justify-space-between">
            <div class="d-flex align-center flex-grow-1">
              <v-icon :color="stat.color" size="24" class="mr-3">{{ stat.icon }}</v-icon>
              <div>
                <div class="text-body-2 text-medium-emphasis">{{ stat.label }}</div>
                <div class="text-h6 font-weight-bold">{{ stat.label === 'pip' && !pipInstalled ? '未安装' : stat.value }}</div>
              </div>
            </div>
            <v-btn v-if="stat.label === 'pip' && !pipInstalled" color="warning" variant="text" size="x-small" @click.stop="installPip" :loading="installingPip">
              安装
            </v-btn>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <v-card>
      <v-card-title class="d-flex align-center flex-wrap ga-3">
        <span>已安装的包</span>
        <v-chip size="small" variant="outlined">{{ statsTotal }}</v-chip>
        <v-text-field v-model="search" prepend-inner-icon="mdi-magnify" label="搜索包名" density="compact"
          variant="outlined" hide-details class="flex-grow-1" style="max-width: 500px"
          @update:model-value="debounceSearch"></v-text-field>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="showInstallDialog = true">
          <v-icon start>mdi-plus</v-icon>
          安装包
        </v-btn>
        <v-btn color="success" @click="upgradeAll" :disabled="loading">
          <span class="text-white">
            <v-icon start>mdi-arrow-up-bold</v-icon>
            升级全部
          </span>
        </v-btn>
        <v-btn color="info" @click="checkUpdates" :disabled="checkingUpdates || loading">
          <v-icon start>mdi-refresh</v-icon>
          检查更新
        </v-btn>
        <v-btn color="secondary" @click="exportPackages">
          <v-icon start>mdi-export</v-icon>
          导出
        </v-btn>
      </v-card-title>

      <v-data-table :headers="headers" :items="filteredPackages" :items-per-page="20" density="compact"
        class="elevation-0" :loading="loading" v-model:page="page">
        <template v-slot:item.name="{ item }">
          <span class="text-primary font-weight-medium cursor-pointer" @click.stop="showPackageDetail(item)">{{
            item.name }}</span>
        </template>
        <template v-slot:item.version="{ item }">
          <v-chip size="small" variant="tonal">{{ item.version }}</v-chip>
        </template>
        <template v-slot:item.latest_version="{ item }">
          <v-progress-circular v-if="checkingPackage === item.name" indeterminate size="16" width="2"
            color="primary"></v-progress-circular>
          <v-chip v-else-if="item.latest_version && item.latest_version !== item.version" size="small" color="success"
            variant="flat">
            {{ item.latest_version }}
          </v-chip>
          <span v-else class="text-medium-emphasis">-</span>
        </template>
        <template v-slot:item.summary="{ item }">
          <span class="text-medium-emphasis text-truncate" style="max-width: 300px;">{{ item.summary || '-' }}</span>
        </template>
        <template v-slot:item.actions="{ item }">
          <v-btn size="x-small" color="success" variant="tonal" class="mr-1" @click="upgrade(item)" :disabled="loading">
            升级
          </v-btn>
          <v-btn size="x-small" color="warning" variant="tonal" class="mr-1" @click="showVersionDialog(item)"
            :disabled="loading">
            降级
          </v-btn>
          <v-btn size="x-small" color="error" variant="tonal" @click="confirmUninstall(item)" :disabled="loading">
            卸载
          </v-btn>
        </template>
      </v-data-table>

    </v-card>

    <v-dialog v-model="showInstallDialog" max-width="500" scrollable>
      <v-card>
        <v-card-title>安装包</v-card-title>
        <v-card-text>
          <v-text-field v-model="installForm.name" label="包名" placeholder="如 requests"
            variant="outlined"></v-text-field>
          <v-text-field v-model="installForm.version" label="版本 (可选)" variant="outlined"></v-text-field>
          <v-checkbox v-model="installForm.upgrade" label="升级已存在的包"></v-checkbox>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showInstallDialog = false">取消</v-btn>
          <v-btn color="primary" @click="install" :disabled="loading">安装</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="showVersionDialogFlag" max-width="500">
      <v-card>
        <v-card-title>选择版本</v-card-title>
        <v-card-text>
          <div class="mb-3">当前版本: <strong>{{ currentPackage?.version }}</strong></div>
          <v-select v-model="selectedVersion" :items="availableVersions" label="选择要降级的版本" variant="outlined"></v-select>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showVersionDialogFlag = false">取消</v-btn>
          <v-btn color="warning" @click="confirmDowngrade" :disabled="loading">降级</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="showDetailDialog" max-width="900" scrollable>
      <v-card :title="packageDetail?.name" :subtitle="packageDetail?.summary">
        <v-divider></v-divider>
        <v-card-text v-if="detailLoading" class="pa-0">
          <v-skeleton-loader type="article"></v-skeleton-loader>
        </v-card-text>
        <v-card-text v-else-if="packageDetail">
          <v-list density="compact">
            <v-list-item>
              <v-row no-gutters>
                <v-col cols="4">
                  <div class="text-primary">版本</div>
                  <div class="text-body-2">{{ packageDetail.version || '-' }}</div>
                </v-col>
                <v-col cols="4" v-if="packageDetail.author">
                  <div class="text-primary">作者</div>
                  <div class="text-body-2">{{ packageDetail.author }}</div>
                </v-col>
                <v-col cols="4" v-else>
                  <div class="text-primary">作者</div>
                  <div class="text-body-2">-</div>
                </v-col>
                <v-col cols="4" v-if="packageDetail.license">
                  <div class="text-primary">许可证</div>
                  <div class="text-body-2">{{ packageDetail.license }}</div>
                </v-col>
                <v-col cols="4" v-else>
                  <div class="text-primary">许可证</div>
                  <div class="text-body-2">-</div>
                </v-col>
              </v-row>
            </v-list-item>
            <v-list-item v-if="packageDetail.home - page">
              <v-list-item-title class="text-primary">主页</v-list-item-title>
              <v-list-item-subtitle>
                <a :href="packageDetail.home - page" target="_blank" class="text-primary">{{ packageDetail.home - page
                  }}</a>
              </v-list-item-subtitle>
            </v-list-item>
            <v-list-item v-if="packageDetail.requires - python">
              <v-list-item-title class="text-primary">Python 版本要求</v-list-item-title>
              <v-list-item-subtitle>{{ packageDetail.requires_python }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item v-if="packageDetail.keywords">
              <v-list-item-title class="text-primary">关键词</v-list-item-title>
              <v-list-item-subtitle>{{ packageDetail.keywords }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item v-if="packageDetail.classifiers && packageDetail.classifiers.length">
              <v-list-item-title class="text-primary">分类</v-list-item-title>
              <div class="mt-2">
                <v-chip v-for="c in packageDetail.classifiers" :key="c" size="x-small" class="mr-1 mb-1">{{ c
                  }}</v-chip>
              </div>
            </v-list-item>
            <v-list-item v-if="packageDetail.description">
              <v-list-item-title class="text-primary">描述</v-list-item-title>
              <v-card-text class="pa-2 text-caption" style="white-space: pre-wrap;">{{ packageDetail.description
                }}</v-card-text>
            </v-list-item>
          </v-list>
        </v-card-text>
      </v-card>
    </v-dialog>

    <v-dialog v-model="showUninstallDialog" max-width="400">
      <v-card>
        <v-card-title>卸载包</v-card-title>
        <v-card-text>确定要卸载 <strong>{{ uninstallTarget?.name }}</strong> 吗？</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showUninstallDialog = false">取消</v-btn>
          <v-btn color="error" @click="uninstall" :loading="loading">卸载</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="showConflictDialog" max-width="700">
      <v-card>
        <v-card-title class="text-error">
          <v-icon color="error" class="mr-2">mdi-alert</v-icon>
          依赖冲突
        </v-card-title>
        <v-card-text>
          <pre class="bg-red-lighten-5 pa-4 rounded" style="white-space: pre-wrap; max-height: 400px; overflow: auto;">{{
        conflictOutput }}</pre>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, inject, onMounted, computed } from 'vue'
import { packagesApi, configApi } from '@/api'

const showToast = inject('showToast')

const headers = [
  { title: '包名', key: 'name' },
  { title: '版本', key: 'version' },
  { title: '最新版本', key: 'latest_version' },
  { title: '简介', key: 'summary' },
  { title: '操作', key: 'actions', sortable: false }
]

const packages = ref([])
const allPackages = ref([])
const loading = ref(false)
const page = ref(1)
const search = ref('')
const statsTotal = ref(0)
const statsUpgradable = ref(0)
const statsOutdated = ref(0)
const hasConflict = ref(false)
const conflictOutput = ref('')

const filteredPackages = computed(() => {
  if (!search.value) return allPackages.value
  return allPackages.value.filter(pkg => pkg.name.toLowerCase().includes(search.value.toLowerCase()))
})

const showInstallDialog = ref(false)
const installForm = reactive({ name: '', version: '', upgrade: false })

const showVersionDialogFlag = ref(false)
const currentPackage = ref(null)
const availableVersions = ref([])
const selectedVersion = ref('')

const showUninstallDialog = ref(false)
const uninstallTarget = ref(null)

const showDetailDialog = ref(false)
const detailLoading = ref(false)
const packageDetail = ref(null)

const showConflictDialog = ref(false)
const checkingUpdates = ref(false)
const checkingPackage = ref('')

const pythonVersion = ref('')
const pipVersion = ref('')
const pipInstalled = ref(true)
const installingPip = ref(false)

const statCards = computed(() => [
  { label: 'pip', value: pipInstalled.value ? (pipVersion.value || '-') : '未安装', icon: 'mdi-toolbox', color: pipInstalled.value ? 'primary' : 'error' },
  { label: '已安装包', value: statsTotal.value, icon: 'mdi-package-variant', color: 'primary' },
  { label: '可升级', value: statsUpgradable.value, icon: 'mdi-check-circle', color: 'success' },
  { label: 'Python 版本', value: pythonVersion.value || '-', icon: 'mdi-language-python', color: 'info' },
  { label: '依赖状态', value: hasConflict.value ? '冲突' : '正常', icon: hasConflict.value ? 'mdi-alert' : 'mdi-shield-check', color: hasConflict.value ? 'error' : 'success', clickable: hasConflict.value, onClick: () => showConflictDialog.value = true }
])

let searchTimeout
const debounceSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    page.value = 1
    loadPackages()
  }, 300)
}

const loadPackages = async () => {
  loading.value = true
  const [pyRes, pipRes, listRes] = await Promise.all([
    configApi.pythonVersion(),
    configApi.pipVersion(),
    packagesApi.list()
  ])
  if (pyRes?.version) {
    pythonVersion.value = pyRes.version.split(' ')[0]
  }
  if (pipRes) {
    pipVersion.value = pipRes.version || ''
    pipInstalled.value = pipRes.installed !== false
  }
  if (listRes) {
    allPackages.value = listRes.packages || []
    statsTotal.value = listRes.total || 0
    statsUpgradable.value = 0
  }
  loading.value = false
  checkConflicts()
}

const checkConflicts = async () => {
  const res = await packagesApi.checkConflicts()
  if (res && !res.ok) {
    hasConflict.value = true
    conflictOutput.value = res.output
  } else {
    hasConflict.value = false
  }
}

const install = async () => {
  if (!installForm.name) return showToast('请输入包名', 'error')
  loading.value = true
  showInstallDialog.value = false
  const res = await packagesApi.install(installForm.name, installForm.version, installForm.upgrade)
  if (res?.task_id) {
    showToast(`安装任务已创建: ${installForm.name}`)
  } else {
    showToast(res?.message || '安装失败', 'error')
  }
  loading.value = false
  installForm.name = ''
  installForm.version = ''
  installForm.upgrade = false
}

const upgrade = async (pkg) => {
  loading.value = true
  const res = await packagesApi.upgrade(pkg.name)
  if (res?.task_id) {
    showToast(`升级任务已创建: ${pkg.name}`)
  } else {
    showToast(res?.message || '升级失败', 'error')
  }
  loading.value = false
}

const upgradeAll = async () => {
  loading.value = true
  const res = await packagesApi.upgradeAll()
  if (res?.task_id) {
    showToast('升级任务已创建')
  } else {
    showToast(res?.message || '升级失败', 'error')
  }
  loading.value = false
}

const checkUpdates = async () => {
  checkingUpdates.value = true
  showToast('正在逐个检查更新...')
  statsUpgradable.value = 0
  for (const pkg of allPackages.value) {
    checkingPackage.value = pkg.name
    try {
      const res = await packagesApi.latestVersion(pkg.name)
      if (res?.results && res.results.length > 0) {
        const latestVersion = res.results[0].version
        if (latestVersion !== pkg.version) {
          const idx = allPackages.value.findIndex(p => p.name === pkg.name)
          if (idx !== -1) {
            allPackages.value[idx] = { ...allPackages.value[idx], latest_version: latestVersion }
            statsUpgradable.value++
          }
        }
      }
    } catch (e) {
      console.error(`检查 ${pkg.name} 失败`, e)
    }
  }
  checkingPackage.value = ''
  showToast(`检查完成，${statsUpgradable.value} 个包有更新`)
  checkingUpdates.value = false
}

const showVersionDialog = async (pkg) => {
  currentPackage.value = pkg
  const res = await packagesApi.versions(pkg.name)
  if (res?.versions) {
    availableVersions.value = res.versions.slice(0, 20)
    showVersionDialogFlag.value = true
  } else {
    showToast('获取版本失败', 'error')
  }
}

const confirmDowngrade = async () => {
  if (!selectedVersion.value) return showToast('请选择版本', 'error')
  loading.value = true
  showVersionDialogFlag.value = false
  const res = await packagesApi.downgrade(currentPackage.value.name, selectedVersion.value)
  if (res?.task_id) {
    showToast(`降级任务已创建: ${currentPackage.value.name}`)
  } else {
    showToast(res?.message || '降级失败', 'error')
  }
  loading.value = false
}

const showPackageDetail = async (pkg) => {
  packageDetail.value = null
  showDetailDialog.value = true
  detailLoading.value = true
  const res = await packagesApi.get(pkg.name)
  if (res) {
    packageDetail.value = res
  } else {
    showToast('获取包详情失败', 'error')
    showDetailDialog.value = false
  }
  detailLoading.value = false
}

const confirmUninstall = (pkg) => {
  uninstallTarget.value = pkg
  showUninstallDialog.value = true
}

const uninstall = async () => {
  loading.value = true
  showUninstallDialog.value = false
  const res = await packagesApi.uninstall(uninstallTarget.value.name)
  if (res?.task_id) {
    showToast(`卸载任务已创建: ${uninstallTarget.value.name}`)
  } else {
    showToast(res?.message || '卸载失败', 'error')
  }
  loading.value = false
}

const exportPackages = () => {
  const lines = allPackages.value.map(pkg => {
    if (pkg.version) {
      return `${pkg.name}==${pkg.version}`
    }
    return pkg.name
  })
  const content = lines.join('\n')
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'requirements.txt'
  a.click()
  URL.revokeObjectURL(url)
  showToast('已导出包列表')
}

const installPip = async () => {
  installingPip.value = true
  const res = await configApi.installPip()
  if (res?.success) {
    pipVersion.value = res.version
    pipInstalled.value = true
    showToast(`pip ${res.version} 安装成功`)
  } else {
    showToast(res?.output || '安装失败', 'error')
  }
  installingPip.value = false
}

onMounted(loadPackages)
</script>
