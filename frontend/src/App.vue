<template>
  <v-app>
    <v-navigation-drawer permanent expand-on-hover width="180">
      <v-list-item class="px-2 py-4" nav>
        <template v-slot:prepend>
          <v-icon size="32" color="primary">mdi-package-variant</v-icon>
        </template>
        <v-list-item-title class="text-h6 font-weight-bold">
          Pip<span class="text-primary">View</span>
        </v-list-item-title>
      </v-list-item>

      <v-divider></v-divider>

      <v-list density="compact" nav>
        <v-list-item
          v-for="item in navItems"
          :key="item.value"
          :prepend-icon="item.icon"
          :title="item.title"
          :value="item.value"
          :active="currentTab === item.value"
          @click="currentTab = item.value"
          color="primary"
        ></v-list-item>
      </v-list>

      <template v-slot:append>
        <v-divider></v-divider>
        <v-list density="compact" nav>
          <v-list-item
            :prepend-icon="activeTasks.length > 0 ? 'mdi-progress-clock' : 'mdi-timer-sand'"
            :title="activeTasks.length > 0 ? `任务 (${activeTasks.length})` : '无任务'"
            :value="'tasks'"
            :active="currentTab === 'tasks'"
            @click="currentTab = 'tasks'"
            color="primary"
          ></v-list-item>
        </v-list>
      </template>
    </v-navigation-drawer>

    <v-main>
      <v-container fluid class="pa-6">
        <PackagesView v-if="currentTab === 'packages'" />
        <SourcesView v-else-if="currentTab === 'sources'" />
        <SettingsView v-else-if="currentTab === 'settings'" />
        <TasksView v-else-if="currentTab === 'tasks'" />
      </v-container>
    </v-main>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000">
      {{ snackbar.message }}
    </v-snackbar>
  </v-app>
</template>

<script setup>
import { ref, provide, reactive, onMounted, onUnmounted } from 'vue'
import PackagesView from './views/PackagesView.vue'
import SourcesView from './views/SourcesView.vue'
import SettingsView from './views/SettingsView.vue'
import TasksView from './views/TasksView.vue'
import { tasksApi } from './api'

const currentTab = ref('packages')

const navItems = [
  { title: '包管理', icon: 'mdi-package-variant', value: 'packages' },
  { title: 'PyPi源', icon: 'mdi-web', value: 'sources' },
  { title: '设置', icon: 'mdi-cog', value: 'settings' }
]

const activeTasks = ref([])
let refreshInterval = null

const loadActiveTasks = async () => {
  const res = await tasksApi.active()
  if (res?.tasks) {
    activeTasks.value = res.tasks
  }
}

onMounted(() => {
  loadActiveTasks()
  refreshInterval = setInterval(loadActiveTasks, 3000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})

const snackbar = reactive({
  show: false,
  message: '',
  color: 'success'
})

const showToast = (message, color = 'success') => {
  snackbar.message = message
  snackbar.color = color
  snackbar.show = true
}

provide('showToast', showToast)
</script>
