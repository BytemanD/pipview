<template>
  <div>
    <v-card>
      <v-card-title class="d-flex align-center flex-wrap ga-3">
        <span>安装任务</span>
        <v-chip size="small" variant="outlined" color="primary">{{ activeTasks.length }}</v-chip>
        <v-spacer></v-spacer>
        <v-btn color="primary" variant="text" size="small" @click="refreshTasks">
          <v-icon start>mdi-refresh</v-icon>
          刷新
        </v-btn>
      </v-card-title>

      <v-list v-if="activeTasks.length > 0" class="pa-0">
        <v-list-item v-for="task in activeTasks" :key="task.task_id" class="border-b">
          <template v-slot:prepend>
            <v-progress-circular v-if="task.status === 'running'" indeterminate size="24" width="2"
              color="primary"></v-progress-circular>
            <v-icon v-else-if="task.status === 'success'" color="success">mdi-check-circle</v-icon>
            <v-icon v-else-if="task.status === 'failed'" color="error">mdi-close-circle</v-icon>
            <v-icon v-else color="warning">mdi-clock</v-icon>
          </template>
          <v-list-item-title>{{ task.name }}</v-list-item-title>
          <v-list-item-subtitle>
            <span v-if="task.status === 'running'">
              <v-progress-linear :model-value="task.progress" color="primary" height="4"
                class="rounded"></v-progress-linear>
            </span>
            <span v-else>{{ task.message || task.status }}</span>
          </v-list-item-subtitle>
          <template v-slot:append>
            <v-chip size="x-small" :color="getStatusColor(task.status)" variant="tonal">
              {{ getStatusText(task.status) }}
            </v-chip>
          </template>
        </v-list-item>
      </v-list>

      <v-card-text v-else class="text-center py-8 text-medium-emphasis">
        <v-icon size="48" color="grey-lighten-1">mdi-timer-sand</v-icon>
        <div class="mt-2">暂无进行中的任务</div>
      </v-card-text>
    </v-card>

    <v-card class="mt-4">
      <v-card-title>任务历史</v-card-title>
      <v-data-table :headers="historyHeaders" :items="historyTasks" :items-per-page="10" density="compact">
        <template v-slot:item.status="{ item }">
          <v-chip size="small" :color="getStatusColor(item.status)" variant="tonal">
            {{ getStatusText(item.status) }}
          </v-chip>
        </template>
        <template v-slot:item.created_at="{ item }">
          {{ formatTime(item.created_at) }}
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { tasksApi } from '@/api'

const activeTasks = ref([])
const historyTasks = ref([])
let refreshInterval = null

const historyHeaders = [
  { title: '任务', key: 'name' },
  { title: '状态', key: 'status' },
  { title: '时间', key: 'created_at' },
  { title: '包', key: 'package_name' }
]

const getStatusColor = (status) => {
  const colors = {
    pending: 'warning',
    running: 'primary',
    success: 'success',
    failed: 'error',
    cancelled: 'grey'
  }
  return colors[status] || 'grey'
}

const getStatusText = (status) => {
  const texts = {
    pending: '等待中',
    running: '运行中',
    success: '成功',
    failed: '失败',
    cancelled: '已取消'
  }
  return texts[status] || status
}

const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN')
}

const loadTasks = async () => {
  const activeRes = await tasksApi.active()
  if (activeRes?.tasks) {
    activeTasks.value = activeRes.tasks
  }

  const historyRes = await tasksApi.list('', 20)
  if (historyRes?.tasks) {
    historyTasks.value = historyRes.tasks.filter(t => t.status !== 'running' && t.status !== 'pending')
  }
}

const refreshTasks = () => {
  loadTasks()
}

onMounted(() => {
  loadTasks()
  refreshInterval = setInterval(loadTasks, 2000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>