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
    apiCall(`/packages/list?page=1&page_size=10000&search=${search}`),

  install: (packageName, version = '', upgrade = false) =>
    apiCall('/packages/install', {
      method: 'POST',
      body: JSON.stringify({ package_name: packageName, version, upgrade })
    }),

  uninstall: (packageName) =>
    apiCall('/packages/uninstall', {
      method: 'POST',
      body: JSON.stringify({ package_name: packageName })
    }),

  upgrade: (packageName = null) =>
    apiCall('/packages/upgrade', {
      method: 'POST',
      body: JSON.stringify(packageName ? { package_name: packageName } : { all: true })
    }),

  downgrade: (packageName, version) =>
    apiCall('/packages/downgrade', {
      method: 'POST',
      body: JSON.stringify({ package_name: packageName, version })
    }),

  versions: (packageName) =>
    apiCall(`/packages/versions/${packageName}`),

  latestVersion: (packageName) =>
    apiCall(`/packages/search?q=${packageName}`),

  checkConflicts: () =>
    apiCall('/packages/check-conflicts'),

  checkUpdates: () =>
    apiCall('/packages/check-updates')
}

export const sourcesApi = {
  list: () => apiCall('/sources/list'),

  add: (name, url) =>
    apiCall('/sources/add', {
      method: 'POST',
      body: JSON.stringify({ name, url })
    }),

  remove: (url) =>
    apiCall('/sources/remove', {
      method: 'POST',
      body: JSON.stringify({ url })
    }),

  set: (sourceUrl, extraSources = null) =>
    apiCall('/sources/set', {
      method: 'POST',
      body: JSON.stringify({ source_url: sourceUrl, extra_sources: extraSources })
    }),

  reset: () =>
    apiCall('/sources/reset', { method: 'POST' })
}

export const configApi = {
  pip: () => apiCall('/config/pip'),
  env: () => apiCall('/config/env'),
  pythonVersion: () => apiCall('/config/python-version')
}

export default { packagesApi, sourcesApi, configApi }
