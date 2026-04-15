<template>
  <v-card>
    <v-card-title>设置</v-card-title>
    <v-card-text>
      <v-tabs v-model="tab" color="primary">
        <v-tab value="pip">pip.ini 配置</v-tab>
        <v-tab value="env">环境变量</v-tab>
      </v-tabs>
      <v-divider></v-divider>
      <v-window v-model="tab" class="mt-4">
        <v-window-item value="pip">
          <v-textarea v-model="pipConfig" variant="outlined" rows="15" readonly auto-grow></v-textarea>
        </v-window-item>
        <v-window-item value="env">
          <v-textarea v-model="envConfig" variant="outlined" rows="10" readonly auto-grow></v-textarea>
        </v-window-item>
      </v-window>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, inject, onMounted } from 'vue'
import { configApi } from '@/api'

const showToast = inject('showToast')
const tab = ref('pip')
const pipConfig = ref('')
const envConfig = ref('')

const loadConfig = async () => {
  const [pipRes, envRes] = await Promise.all([configApi.pip(), configApi.env()])
  pipConfig.value = pipRes?.content || '未找到配置文件'
  envConfig.value = envRes?.content || '无环境变量'
}

onMounted(loadConfig)
</script>
