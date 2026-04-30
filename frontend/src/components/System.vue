<template>
  <div>
    <!-- Hero section -->
    <div class="px-8 py-12">
      <div class="text-sm text-yellow-400 font-bold uppercase tracking-widest mb-2">Diagnostics</div>
      <h2 class="text-6xl font-black mb-8">
        <span class="text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-amber-400">
          SYSTEM STATUS
        </span>
      </h2>
    </div>

    <!-- Status grid -->
    <div class="px-8 pb-12">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- System Status -->
        <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-2xl p-8 border-2 border-yellow-500/20 shadow-2xl relative overflow-hidden">
          <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-yellow-500 to-green-500"></div>
          <h3 class="text-2xl font-black mb-6 text-white uppercase">System Health</h3>
          <div class="space-y-5">
            <div
              v-for="item in systemStatus"
              :key="item.label"
              class="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg border border-gray-700"
            >
              <span class="text-gray-400 font-bold uppercase text-sm">{{ item.label }}</span>
              <span class="flex items-center gap-3">
                <span :class="`w-3 h-3 bg-${item.color}-500 rounded-full animate-pulse shadow-lg shadow-${item.color}-500/50`"></span>
                <span :class="`text-${item.color}-400 font-black uppercase`">{{ item.status }}</span>
              </span>
            </div>
            <div class="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg border border-gray-700">
              <span class="text-gray-400 font-bold uppercase text-sm">Last Update</span>
              <span class="text-white font-mono">{{ lastUpdate ?? 'Never' }}</span>
            </div>
            <div class="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg border border-gray-700">
              <span class="text-gray-400 font-bold uppercase text-sm">Uptime</span>
              <span class="text-white font-mono font-black">{{ uptime != null ? uptime + '%' : 'N/A' }}</span>
            </div>
          </div>
        </div>

        <!-- Device Info -->
        <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-2xl p-8 border-2 border-amber-500/20 shadow-2xl relative overflow-hidden">
          <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-amber-500 to-orange-500"></div>
          <h3 class="text-2xl font-black mb-6 text-white uppercase">Device Info</h3>
          <div class="space-y-5">
            <div class="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
              <div class="text-gray-500 text-xs uppercase mb-2">Device ID</div>
              <div class="font-mono text-xl text-yellow-400 font-bold">{{ deviceId ?? 'N/A' }}</div>
            </div>
            <div class="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
              <div class="text-gray-500 text-xs uppercase mb-2">Firmware</div>
              <div class="text-white font-mono text-xl font-bold">{{ firmware ?? 'N/A' }}</div>
            </div>
            <div class="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
              <div class="text-gray-500 text-xs uppercase mb-2">IP Address</div>
              <div class="font-mono text-xl text-amber-400 font-bold">{{ ipAddress ?? 'N/A' }}</div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div class="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                <div class="text-gray-500 text-xs uppercase mb-2">CPU</div>
                <div class="text-white font-black text-2xl">{{ cpu != null ? cpu + '%' : 'N/A' }}</div>
              </div>
              <div class="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                <div class="text-gray-500 text-xs uppercase mb-2">Memory</div>
                <div class="text-white font-black text-2xl">{{ memoryUsed != null && memoryTotal != null ? memoryUsed + '/' + memoryTotal + 'GB' : 'N/A' }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Settings - Full width -->
      <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-2xl p-10 border-2 border-orange-500/20 shadow-2xl relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-orange-500 via-amber-500 to-yellow-500"></div>
        <h3 class="text-2xl font-black mb-8 text-white uppercase">Optimization Settings</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div
            v-for="setting in settings"
            :key="setting.name"
            class="p-6 bg-gray-800/50 rounded-xl border border-gray-700 hover:border-yellow-500/50 transition-all"
          >
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <div class="font-black text-white uppercase text-lg mb-1">{{ setting.name }}</div>
                <div class="text-sm text-gray-500 font-mono">{{ setting.desc }}</div>
              </div>
            </div>
            <label class="relative inline-flex items-center cursor-pointer w-full">
              <input type="checkbox" class="sr-only peer" :checked="setting.checked" />
              <div class="w-full h-12 bg-gray-700 peer-focus:outline-none rounded-lg peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[4px] after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-md after:h-10 after:w-10 after:transition-all peer-checked:bg-gradient-to-r peer-checked:from-yellow-500 peer-checked:to-amber-500 shadow-lg peer-checked:shadow-yellow-500/50"></div>
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SystemTab',
  data() {
    return {
      lastUpdate: null,
      uptime: null,
      systemStatus: [],
      deviceId: null,
      firmware: null,
      ipAddress: null,
      cpu: null,
      memoryUsed: null,
      memoryTotal: null,
      settings: [
        { name: 'Cost Optimization', desc: 'Auto-switch based on pricing', checked: true },
        { name: 'Outage Backup',     desc: 'Reserve battery for outages', checked: true },
        { name: 'Smart Scheduling',  desc: 'Learn usage patterns',         checked: false }
      ]
    }
  },
  async mounted() {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/api/system/`)
      const data = await res.json()
      this.lastUpdate   = data.health.lastUpdate ? new Date(data.health.lastUpdate).toLocaleString() : null
      this.uptime       = data.health.uptime
      this.systemStatus = [
        { label: 'System',         status: data.health.system,        color: this.statusColor(data.health.system) },
        { label: 'API Connection', status: data.health.apiConnection, color: this.statusColor(data.health.apiConnection) },
        { label: 'Raspberry Pi',   status: data.health.raspberryPi,   color: this.statusColor(data.health.raspberryPi) }
      ]
      this.deviceId    = data.device.deviceId
      this.firmware    = data.device.firmware
      this.ipAddress   = data.device.ipAddress
      this.cpu         = data.device.cpu
      this.memoryUsed  = data.device.memory.used
      this.memoryTotal = data.device.memory.total
    } catch (err) {
      console.error('Failed to fetch system data:', err)
    }
  },
  methods: {
    statusColor(status) {
      return ['Online', 'Connected', 'Active'].includes(status) ? 'green' : 'red'
    }
  }
}
</script>
