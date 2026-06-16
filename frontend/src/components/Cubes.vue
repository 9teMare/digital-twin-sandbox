<!--
  Cubes — interactive 3D cube grid.
  Component inspired from Can Tastemel's original work for the lambda.ai landing page
  https://cantastemel.com  (via Vue Bits)

  Self-contained version: no Tailwind dependency, styling via scoped CSS.
-->
<template>
  <div class="cubes-root" :style="wrapperStyle">
    <div ref="sceneRef" class="cubes-scene" :style="sceneStyle">
      <template v-for="(_, r) in cells" :key="`row-${r}`">
        <div
          v-for="(__, c) in cells"
          :key="`${r}-${c}`"
          class="cube"
          :data-row="r"
          :data-col="c"
        >
          <span class="cube-hit" />

          <div class="cube-face" :style="faceStyle('translateY(-50%) rotateX(90deg)')" />
          <div class="cube-face" :style="faceStyle('translateY(50%) rotateX(-90deg)')" />
          <div class="cube-face" :style="faceStyle('translateX(-50%) rotateY(-90deg)')" />
          <div class="cube-face" :style="faceStyle('translateX(50%) rotateY(90deg)')" />
          <div class="cube-face" :style="faceStyle('rotateY(-90deg) translateX(50%) rotateY(90deg)')" />
          <div class="cube-face" :style="faceStyle('rotateY(90deg) translateX(-50%) rotateY(-90deg)')" />
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import gsap from 'gsap'

const props = defineProps({
  gridSize: { type: Number, default: 10 },
  cubeSize: { type: Number, default: undefined },
  maxAngle: { type: Number, default: 45 },
  radius: { type: Number, default: 3 },
  easing: { type: String, default: 'power3.out' },
  duration: { type: Object, default: () => ({ enter: 0.3, leave: 0.6 }) },
  cellGap: { type: [Number, Object], default: undefined },
  borderStyle: { type: String, default: '1px solid #fff' },
  faceColor: { type: String, default: '#0b0b0b' },
  shadow: { type: [Boolean, String], default: false },
  autoAnimate: { type: Boolean, default: true },
  rippleOnClick: { type: Boolean, default: true },
  rippleColor: { type: String, default: '#fff' },
  rippleSpeed: { type: Number, default: 2 }
})

const sceneRef = ref(null)
let rafId = null
let idleTimer = null
let userActive = false
let simPos = { x: 0, y: 0 }
let simTarget = { x: 0, y: 0 }
let simRAF = null

const colGap = computed(() => {
  if (typeof props.cellGap === 'number') return `${props.cellGap}px`
  if (props.cellGap && props.cellGap.col !== undefined) return `${props.cellGap.col}px`
  return '5%'
})

const rowGap = computed(() => {
  if (typeof props.cellGap === 'number') return `${props.cellGap}px`
  if (props.cellGap && props.cellGap.row !== undefined) return `${props.cellGap.row}px`
  return '5%'
})

const enterDur = computed(() => props.duration.enter)
const leaveDur = computed(() => props.duration.leave)

const cells = computed(() => Array.from({ length: props.gridSize }))

const sceneStyle = computed(() => ({
  gridTemplateColumns: props.cubeSize
    ? `repeat(${props.gridSize}, ${props.cubeSize}px)`
    : `repeat(${props.gridSize}, 1fr)`,
  gridTemplateRows: props.cubeSize
    ? `repeat(${props.gridSize}, ${props.cubeSize}px)`
    : `repeat(${props.gridSize}, 1fr)`,
  columnGap: colGap.value,
  rowGap: rowGap.value,
  perspective: '99999999px',
  gridAutoRows: '1fr'
}))

const wrapperStyle = computed(() => ({
  '--cube-face-border': props.borderStyle,
  '--cube-face-bg': props.faceColor,
  '--cube-face-shadow': props.shadow === true ? '0 0 6px rgba(0,0,0,.5)' : props.shadow || 'none',
  ...(props.cubeSize
    ? {
        width: `${props.gridSize * props.cubeSize}px`,
        height: `${props.gridSize * props.cubeSize}px`
      }
    : {})
}))

const faceStyle = transform => ({
  background: 'var(--cube-face-bg)',
  border: 'var(--cube-face-border)',
  boxShadow: 'var(--cube-face-shadow)',
  transform
})

const tiltAt = (rowCenter, colCenter) => {
  if (!sceneRef.value) return
  sceneRef.value.querySelectorAll('.cube').forEach(cube => {
    const r = +cube.dataset.row
    const c = +cube.dataset.col
    const dist = Math.hypot(r - rowCenter, c - colCenter)
    if (dist <= props.radius) {
      const pct = 1 - dist / props.radius
      const angle = pct * props.maxAngle
      gsap.to(cube, {
        duration: enterDur.value,
        ease: props.easing,
        overwrite: true,
        rotateX: -angle,
        rotateY: angle
      })
    } else {
      gsap.to(cube, {
        duration: leaveDur.value,
        ease: 'power3.out',
        overwrite: true,
        rotateX: 0,
        rotateY: 0
      })
    }
  })
}

const onPointerMove = e => {
  userActive = true
  if (idleTimer) clearTimeout(idleTimer)

  const rect = sceneRef.value.getBoundingClientRect()
  const cellW = rect.width / props.gridSize
  const cellH = rect.height / props.gridSize
  const colCenter = (e.clientX - rect.left) / cellW
  const rowCenter = (e.clientY - rect.top) / cellH

  if (rafId) cancelAnimationFrame(rafId)
  rafId = requestAnimationFrame(() => tiltAt(rowCenter, colCenter))

  idleTimer = setTimeout(() => {
    userActive = false
  }, 3000)
}

const resetAll = () => {
  if (!sceneRef.value) return
  sceneRef.value.querySelectorAll('.cube').forEach(cube =>
    gsap.to(cube, {
      duration: leaveDur.value,
      rotateX: 0,
      rotateY: 0,
      ease: 'power3.out'
    })
  )
}

const onClick = e => {
  if (!props.rippleOnClick || !sceneRef.value) return

  const rect = sceneRef.value.getBoundingClientRect()
  const cellW = rect.width / props.gridSize
  const cellH = rect.height / props.gridSize
  const colHit = Math.floor((e.clientX - rect.left) / cellW)
  const rowHit = Math.floor((e.clientY - rect.top) / cellH)

  const baseRingDelay = 0.15
  const baseAnimDur = 0.3
  const baseHold = 0.6

  const spreadDelay = baseRingDelay / props.rippleSpeed
  const animDuration = baseAnimDur / props.rippleSpeed
  const holdTime = baseHold / props.rippleSpeed

  const rings = {}
  sceneRef.value.querySelectorAll('.cube').forEach(cube => {
    const r = +cube.dataset.row
    const c = +cube.dataset.col
    const dist = Math.hypot(r - rowHit, c - colHit)
    const ring = Math.round(dist)
    if (!rings[ring]) rings[ring] = []
    rings[ring].push(cube)
  })

  Object.keys(rings)
    .map(Number)
    .sort((a, b) => a - b)
    .forEach(ring => {
      const delay = ring * spreadDelay
      const faces = rings[ring].flatMap(cube => Array.from(cube.querySelectorAll('.cube-face')))
      gsap.to(faces, {
        backgroundColor: props.rippleColor,
        duration: animDuration,
        delay,
        ease: 'power3.out'
      })
      gsap.to(faces, {
        backgroundColor: props.faceColor,
        duration: animDuration,
        delay: delay + animDuration + holdTime,
        ease: 'power3.out'
      })
    })
}

const startAutoAnimation = () => {
  if (!props.autoAnimate || !sceneRef.value) return

  simPos = { x: Math.random() * props.gridSize, y: Math.random() * props.gridSize }
  simTarget = { x: Math.random() * props.gridSize, y: Math.random() * props.gridSize }

  const speed = 0.02
  const loop = () => {
    if (!userActive) {
      simPos.x += (simTarget.x - simPos.x) * speed
      simPos.y += (simTarget.y - simPos.y) * speed
      tiltAt(simPos.y, simPos.x)
      if (Math.hypot(simPos.x - simTarget.x, simPos.y - simTarget.y) < 0.1) {
        simTarget = { x: Math.random() * props.gridSize, y: Math.random() * props.gridSize }
      }
    }
    simRAF = requestAnimationFrame(loop)
  }
  simRAF = requestAnimationFrame(loop)
}

onMounted(() => {
  const el = sceneRef.value
  if (!el) return
  el.addEventListener('pointermove', onPointerMove)
  el.addEventListener('pointerleave', resetAll)
  el.addEventListener('click', onClick)
  startAutoAnimation()
})

onUnmounted(() => {
  const el = sceneRef.value
  if (el) {
    el.removeEventListener('pointermove', onPointerMove)
    el.removeEventListener('pointerleave', resetAll)
    el.removeEventListener('click', onClick)
  }
  if (rafId !== null) cancelAnimationFrame(rafId)
  if (idleTimer !== null) clearTimeout(idleTimer)
  if (simRAF !== null) cancelAnimationFrame(simRAF)
})
</script>

<style scoped>
.cubes-root {
  position: relative;
  width: 100%;
  height: 100%;
  aspect-ratio: 1 / 1;
}

.cubes-scene {
  display: grid;
  width: 100%;
  height: 100%;
}

.cube {
  position: relative;
  width: 100%;
  height: 100%;
  aspect-ratio: 1 / 1;
  transform-style: preserve-3d;
}

.cube-hit {
  position: absolute;
  inset: -2.25rem;
  pointer-events: none;
}

.cube-face {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
