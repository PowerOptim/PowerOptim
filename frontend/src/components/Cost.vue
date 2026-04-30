<template>
  <div>
    <!-- Split hero section -->
    <div class="px-8 py-12">
      <div class="grid grid-cols-1 lg:grid-cols-5 gap-8 items-end">
        <div class="lg:col-span-3">
          <div class="text-sm text-green-400 font-bold uppercase tracking-widest mb-2">Financial Impact</div>
          <h2 class="text-7xl font-black mb-6 leading-tight">
            <span class="text-white">YOU'RE</span><br/>
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-yellow-400">
              SAVING MONEY
            </span>
          </h2>
        </div>
        <div class="lg:col-span-2">
          <div class="bg-gradient-to-br from-green-900/30 to-green-950/30 rounded-2xl p-8 border-2 border-green-500/50">
            <div class="text-green-400/70 text-xs font-bold uppercase tracking-widest mb-2">This Month</div>
            <div class="text-6xl font-black text-green-400 drop-shadow-[0_0_20px_rgba(34,197,94,0.5)]">
              ${{ monthlyCost?.savings?.toFixed(6) ?? '0.000000' }}
            </div>
            <div class="text-gray-500 text-sm mt-2 uppercase">{{ monthlyCost?.savingsPercentage ?? 0 }}% Reduction</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Comparison cards -->
    <div class="px-8 pb-8">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div class="bg-gradient-to-br from-green-900/20 to-green-950/20 rounded-2xl p-10 border-l-4 border-green-500 relative overflow-hidden">
          <div class="absolute top-4 right-4 text-6xl opacity-20">✓</div>
          <div class="text-green-400/70 text-sm font-bold uppercase tracking-widest mb-3">With PowerOptim</div>
          <div class="text-6xl font-black text-green-400 mb-2">${{ monthlyCost?.actual?.toFixed(6) ?? '0.000000' }}</div>
          <div class="text-gray-500 uppercase text-sm">Actual cost paid (30 days)</div>
        </div>
        <div class="bg-gradient-to-br from-red-900/20 to-red-950/20 rounded-2xl p-10 border-l-4 border-red-500 relative overflow-hidden">
          <div class="absolute top-4 right-4 text-6xl opacity-20">✗</div>
          <div class="text-red-400/70 text-sm font-bold uppercase tracking-widest mb-3">Without System</div>
          <div class="text-6xl font-black text-red-400 mb-2">${{ monthlyCost?.withoutSystem?.toFixed(6) ?? '0.000000' }}</div>
          <div class="text-gray-500 uppercase text-sm">Grid-only estimate</div>
        </div>
      </div>
    </div>

    <!-- Pricing Chart - Full width -->
    <div class="px-8 pb-8">
      <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-2xl p-10 border-2 border-yellow-500/20 shadow-2xl relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-red-500 via-yellow-500 to-green-500"></div>
        <div class="flex items-center justify-between mb-8">
          <h3 class="text-2xl font-black text-white uppercase">Today's Pricing Zones</h3>
          <div class="flex items-center gap-6 text-xs font-bold uppercase text-gray-500">
            <span class="flex items-center gap-2"><span class="w-3 h-3 rounded-sm bg-red-500 inline-block"></span>Peak</span>
            <span class="flex items-center gap-2"><span class="w-3 h-3 rounded-sm bg-yellow-500 inline-block"></span>Standard</span>
            <span class="flex items-center gap-2"><span class="w-3 h-3 rounded-sm bg-green-500 inline-block"></span>Off-Peak</span>
            <span class="flex items-center gap-2"><span class="w-3 h-3 rounded-sm bg-gray-600 inline-block opacity-60 border border-dashed border-gray-400"></span>Forecast</span>
          </div>
        </div>
        <div class="h-80 flex items-end gap-1">
          <div
            v-for="(item, i) in pricingData"
            :key="i"
            class="flex-1 flex flex-col items-center"
          >
            <div
              :class="[
                'w-full rounded-t transition-all shadow-lg',
                item.is_forecast ? 'opacity-50' : 'opacity-100',
                barColor(i)
              ]"
              :style="{ height: pricingMax > 0 ? (item.price / pricingMax) * 100 + '%' : '4px' }"
              :title="`${formatHour(item.hour)}: ${item.price != null ? '$' + item.price.toFixed(4) + '/kWh' : 'N/A'}${item.is_forecast ? ' (forecast)' : ''}`"
            ></div>
          </div>
        </div>
        <div class="flex justify-between text-sm text-gray-600 mt-6 font-mono">
          <span>MIDNIGHT</span>
          <span>NOON</span>
          <span>MIDNIGHT</span>
        </div>
      </div>
    </div>

    <!-- Breakdown -->
    <div class="px-8 pb-12">
      <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-2xl p-10 border-2 border-amber-500/20 shadow-2xl relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-red-500 via-yellow-500 to-green-500"></div>
        <h3 class="text-2xl font-black mb-2 text-white uppercase">Savings Breakdown</h3>
        <p class="text-gray-500 text-sm mb-8 uppercase">Cost avoided by switching to battery during each pricing zone</p>
        <div class="space-y-8">
          <div v-for="(zone, i) in breakdown" :key="zone.category">
            <div class="flex justify-between items-center mb-4">
              <div>
                <div class="text-gray-400 font-bold uppercase text-sm mb-1">{{ zone.category }}</div>
                <div class="text-gray-600 text-xs font-mono">{{ zone.description }}</div>
              </div>
              <span :class="['font-black text-3xl', zoneColor(i)]">${{ zone.savings?.toFixed(6) ?? '0.000000' }}</span>
            </div>
            <div class="bg-gray-800 rounded-full h-4 overflow-hidden border border-gray-700">
              <div
                :class="['h-4 rounded-full shadow-lg', zoneBarClass(i)]"
                :style="{ width: (zone.percentage || 0) + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CostTab',
  data() {
    return {
      monthlyCost: null,
      pricingData: [],
      pricingMax: 0.01,
      breakdown: []
    }
  },
  async mounted() {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/api/cost/`)
      const data = await res.json()
      this.monthlyCost = data.monthlyCost
      this.pricingData = data.pricingZones

      const prices = data.pricingZones.map(z => z.price).filter(p => p != null)
      this.pricingMax = prices.length > 0 ? Math.max(...prices) : 0.01

      const totalSavings = data.monthlyCost.savings || 0
      this.breakdown = data.breakdown.map(b => ({
        ...b,
        percentage: totalSavings > 0 ? Math.round((b.savings / totalSavings) * 100) : 0
      }))
    } catch (err) {
      console.error('Failed to fetch cost data:', err)
    }
  },
  methods: {
    barColor(hourIndex) {
      if (hourIndex >= 17 && hourIndex <= 20) return 'bg-gradient-to-t from-red-600 to-red-500 shadow-red-500/50'
      if (hourIndex >= 0 && hourIndex <= 5)  return 'bg-gradient-to-t from-green-600 to-green-500 shadow-green-500/50'
      return 'bg-gradient-to-t from-yellow-600 to-yellow-500 shadow-yellow-500/50'
    },
    zoneColor(i) {
      return ['text-red-400', 'text-green-400', 'text-yellow-400'][i] ?? 'text-gray-400'
    },
    zoneBarClass(i) {
      return [
        'bg-gradient-to-r from-red-600 to-red-500 shadow-red-500/50',
        'bg-gradient-to-r from-green-600 to-green-500 shadow-green-500/50',
        'bg-gradient-to-r from-yellow-600 to-yellow-500 shadow-yellow-500/50'
      ][i] ?? 'bg-gradient-to-r from-gray-600 to-gray-500'
    },
    formatHour(isoString) {
      if (!isoString) return ''
      const d = new Date(isoString)
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  }
}
</script>
