<template>
  <div>
    <div class="px-8 py-12">
      <div class="text-sm text-yellow-400 font-bold uppercase tracking-widest mb-2">Analytics</div>
      <h2 class="text-6xl font-black mb-4">
        <span class="text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-amber-400">
          ENERGY USAGE
        </span>
      </h2>
    </div>

    <div class="px-8 pb-12">
      <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-2xl p-16 border-2 border-yellow-500/20 shadow-2xl relative overflow-hidden text-center">
        <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-yellow-500 via-amber-500 to-orange-500"></div>
        <div class="text-8xl mb-8">⚡</div>
        <h3 class="text-3xl font-black text-white uppercase mb-4">Energy Metering Not Yet Available</h3>
        <p class="text-gray-400 text-lg max-w-lg mx-auto">
          Detailed energy usage tracking requires a current sensor (INA219). Once installed, this page will show real-time consumption data.
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EnergyTab'
}
</script>
