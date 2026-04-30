<template>
  <div>
    <!-- Hero Section -->
    <div class="relative px-8 py-16 overflow-hidden">
      <div class="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-yellow-500/10 to-transparent"></div>
      <div class="relative z-10">
        <div class="text-sm text-yellow-400 font-bold uppercase tracking-widest mb-4">Welcome Back</div>
        <h2 class="text-7xl font-black mb-6 leading-tight">
          <span class="text-white">YOUR</span><br/>
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 via-amber-400 to-orange-400">
            POWER STATUS
          </span>
        </h2>
        <p class="text-xl text-gray-400 max-w-2xl">
          Real-time monitoring and intelligent optimization for your home energy system
        </p>
      </div>
    </div>

    <!-- Stats Section - Asymmetric Layout -->
    <div class="px-8 pb-12">
      <div class="grid grid-cols-12 gap-6">
        <!-- Large featured stat -->
        <div class="col-span-12 lg:col-span-7 relative overflow-hidden">
          <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-2xl p-10 border-2 border-yellow-500/30 shadow-2xl h-full relative overflow-hidden">
            <div class="absolute top-0 right-0 w-64 h-64 bg-yellow-500/10 rounded-full blur-3xl"></div>
            <div class="relative z-10">
              <div class="flex items-start justify-between mb-8">
                <div>
                  <div class="text-yellow-400/70 text-sm font-bold uppercase tracking-widest mb-3">Currently Running On</div>
                  <div class="text-6xl font-black text-white mb-2">{{ powerSource ?? 'Unknown' }}</div>
                  <div class="text-gray-500 uppercase text-sm font-bold">Power Source</div>
                </div>
                <div :class="['text-8xl', powerSource === 'Battery' ? 'drop-shadow-[0_0_20px_rgba(34,197,94,0.7)]' : 'drop-shadow-[0_0_20px_rgba(234,179,8,0.7)]']">
                  {{ powerSource === 'Battery' ? '🔋' : '🔌' }}
                </div>
              </div>

              <!-- Mini stats row -->
              <div class="grid grid-cols-3 gap-4 pt-6 border-t border-gray-800">
                <div>
                  <div class="text-gray-500 text-xs uppercase mb-1">Battery</div>
                  <div class="text-2xl font-black text-yellow-400">{{ batteryLevel != null ? batteryLevel + '%' : 'N/A' }}</div>
                </div>
                <div>
                  <div class="text-gray-500 text-xs uppercase mb-1">Price/kWh</div>
                  <div class="text-2xl font-black text-amber-400">{{ currentPrice != null ? '$' + currentPrice : 'N/A' }}</div>
                </div>
                <div>
                  <div class="text-gray-500 text-xs uppercase mb-1">Saved Today</div>
                  <div class="text-2xl font-black text-green-400">${{ todaySavings }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Stacked smaller stats -->
        <div class="col-span-12 lg:col-span-5 flex flex-col gap-6">
          <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-2xl p-8 border-2 border-amber-500/30 shadow-xl relative overflow-hidden">
            <div class="absolute bottom-0 left-0 w-48 h-48 bg-amber-500/10 rounded-full blur-3xl"></div>
            <div class="relative z-10">
              <div class="text-amber-400/70 text-xs font-bold uppercase tracking-widest mb-3">Battery Level</div>
              <div class="flex items-end gap-2 mb-4">
                <div class="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-amber-400">
                  {{ batteryLevel ?? 'N/A' }}
                </div>
                <div v-if="batteryLevel != null" class="text-2xl font-black text-gray-500 mb-1">%</div>
              </div>
              <div class="bg-gray-800 rounded-full h-4 overflow-hidden border border-gray-700">
                <div
                  class="h-4 rounded-full bg-gradient-to-r from-yellow-500 via-amber-500 to-orange-500 shadow-lg transition-all"
                  :style="{ width: (batteryLevel || 0) + '%' }"
                ></div>
              </div>
            </div>
          </div>

          <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-2xl p-8 border-2 border-green-500/30 shadow-xl relative overflow-hidden">
            <div class="absolute top-0 right-0 w-48 h-48 bg-green-500/10 rounded-full blur-3xl"></div>
            <div class="relative z-10">
              <div class="text-green-400/70 text-xs font-bold uppercase tracking-widest mb-3">Today's Savings</div>
              <div class="flex items-end gap-2">
                <div class="text-5xl font-black text-green-400 drop-shadow-[0_0_15px_rgba(34,197,94,0.5)]">
                  ${{ todaySavings }}
                </div>
              </div>
              <div class="text-gray-500 text-sm mt-2">vs. grid-only operation</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Full-width stats bar -->
    <div class="px-8 pb-12">
      <div class="bg-gradient-to-r from-gray-900/90 via-gray-950/90 to-gray-900/90 rounded-2xl p-8 border-y-2 border-yellow-500/20 relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-yellow-500 via-amber-500 to-orange-500"></div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div class="flex items-center gap-6 border-l-4 border-yellow-500 pl-6">
            <div class="text-5xl drop-shadow-[0_0_15px_rgba(234,179,8,0.5)]">$</div>
            <div>
              <div class="text-yellow-400/70 text-xs font-bold uppercase tracking-widest mb-1">Price Zone</div>
              <div class="text-4xl font-black text-yellow-300">{{ priceTier ?? 'N/A' }}</div>
            </div>
          </div>
          <div class="flex items-center gap-6 border-l-4 border-amber-500 pl-6">
            <div class="text-5xl drop-shadow-[0_0_15px_rgba(245,158,11,0.5)]">💰</div>
            <div>
              <div class="text-amber-400/70 text-xs font-bold uppercase tracking-widest mb-1">Monthly Savings</div>
              <div class="text-4xl font-black text-amber-300">${{ monthlySavings }}</div>
            </div>
          </div>
          <div class="flex items-center gap-6 border-l-4 border-green-500 pl-6">
            <div class="text-5xl drop-shadow-[0_0_15px_rgba(34,197,94,0.5)]">✓</div>
            <div>
              <div class="text-green-400/70 text-xs font-bold uppercase tracking-widest mb-1">System Uptime</div>
              <div class="text-4xl font-black text-green-300">{{ uptime != null ? uptime : 'N/A' }}<span v-if="uptime != null" class="text-xl text-gray-500">%</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DashboardTab',
  data() {
    return {
      powerSource: null,
      batteryLevel: null,
      currentPrice: null,
      todaySavings: null,
      priceTier: null,
      monthlySavings: null,
      uptime: null
    }
  },
  async mounted() {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/api/dashboard/`)
      const data = await res.json()
      this.powerSource    = data.power.source
      this.batteryLevel   = data.battery.level
      this.currentPrice   = data.power.currentPrice != null ? data.power.currentPrice.toFixed(4) : null
      this.todaySavings   = data.savings.today != null ? data.savings.today.toFixed(6) : '0.000000'
      this.priceTier      = data.power.priceTier
      this.monthlySavings = data.savings.month != null ? data.savings.month.toFixed(6) : '0.000000'
      this.uptime         = data.system.uptime
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err)
    }
  }
}
</script>
