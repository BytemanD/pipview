const API_BASE = '/api/v1'

async function apiCall(url, options = {}) {
  try {
    const response = await fetch(`${API_BASE}${url}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options
    })
    return await response.json()
  } catch (error) {
    console.error('API Error:', error)
    return null
  }
}

export const packagesApi = {
  list: (search = '') =>
    apiCall(`/packages?search=${search}`),

  get: (packageName) =>
    apiCall(`/packages/${packageName}`),

  install: (packageName, version = '', upgrade = false) =>
    apiCall('/packages', {
      method: 'POST',
      body: JSON.stringify({ package_name: packageName, version, upgrade })
    }),

  uninstall: (packageName) =>
    apiCall(`/packages/${packageName}`, {
      method: 'DELETE'
    }),

  upgrade: (packageName) =>
    apiCall(`/packages/${packageName}`, {
      method: 'PUT'
    }),

  upgradeAll: () =>
    apiCall('/packages/upgrade-all', {
      method: 'PUT'
    }),

  downgrade: (packageName, version) =>
    apiCall(`/packages/${packageName}/version?version=${version}`, {
      method: 'PUT'
    }),

  versions: (packageName) =>
    apiCall(`/packages/${packageName}/versions`),

  latestVersion: (packageName) =>
    apiCall(`/packages/search?q=${packageName}`),

  checkConflicts: () =>
    apiCall('/packages/conflicts'),

  checkUpdates: () =>
    apiCall('/packages/updates')
}

export const sourcesApi = {
  list: () => apiCall('/sources'),

  defaults: () => apiCall('/sources/defaults'),

  current: () => apiCall('/sources/current'),

  add: (name, url) =>
    apiCall('/sources', {
      method: 'POST',
      body: JSON.stringify({ name, url })
    }),

  remove: (url) =>
    apiCall(`/sources/${encodeURIComponent(url)}`, {
      method: 'DELETE'
    }),

  set: (sourceUrl, extraSources = null) =>
    apiCall('/sources/current', {
      method: 'PUT',
      body: JSON.stringify({ source_url: sourceUrl, extra_sources: extraSources })
    }),

  reset: () =>
    apiCall('/sources/current', { method: 'DELETE' })
}

export const configApi = {
  get: () => apiCall('/configs'),
  pip: () => apiCall('/configs/pip'),
  env: () => apiCall('/configs/env'),
  pythonVersion: () => apiCall('/configs/python-version'),
  pipVersion: () => apiCall('/configs/pip-version'),
  installPip: () => apiCall('/configs/install-pip', { method: 'POST' })
}

export const tasksApi = {
  list: (status = '', limit = 50) =>
    apiCall(`/tasks?status=${status}&limit=${limit}`),

  active: () => apiCall('/tasks/active'),

  get: (taskId) =>
    apiCall(`/tasks/${taskId}`),

  output: (taskId) =>
    apiCall(`/tasks/${taskId}/output`),

  cancel: (taskId) =>
    apiCall(`/tasks/${taskId}`, { method: 'DELETE' })
}

export default { packagesApi, sourcesApi, configApi, tasksApi }
