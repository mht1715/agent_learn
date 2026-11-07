<script setup>
import {ref} from 'vue'
import {chatStream} from '../api/sse'

const input = ref('北京天气怎么样')
const events = ref([])
const answer = ref('')
const loading = ref(false)

async function send() {
  if (loading.value || !input.value.trim()) return
  events.value = []
  answer.value = ''
  loading.value = true

  try {
    await chatStream(input.value, (ev) => {
      events.value.push(ev)
      if (ev.type === 'final') answer.value = ev.answer
      if (ev.type === 'error') answer.value = ev.message
    })
  } catch (e) {
    answer.value = `请求失败：${e.message}`
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="chat">
    <div class="input-row">
      <input
          v-model="input"
          :disabled="loading"
          placeholder="输入问题，例如：订单 A1001 到哪了"
          @keyup.enter="send"
      />
      <button :disabled="loading" @click="send">
        {{ loading ? '处理中…' : '发送' }}
      </button>
    </div>

    <ol class="steps">
      <li v-for="(ev, i) in events" :key="i">
        <span v-if="ev.type === 'step_start'" class="step-start">
          第 {{ ev.step }} 步
        </span>
        <span v-else-if="ev.type === 'tool_call'" class="tool-call">
          调用 {{ ev.name }} <code>{{ JSON.stringify(ev.args) }}</code>
        </span>
        <span v-else-if="ev.type === 'tool_result'" class="tool-result">
          {{ ev.name }} → {{ ev.result }}
        </span>
        <span v-else-if="ev.type === 'final'" class="final">
          完成（共 {{ ev.steps }} 步，状态：{{ ev.status }}）
        </span>
      </li>
    </ol>

    <p v-if="answer" class="answer">{{ answer }}</p>
  </div>
</template>

<style scoped>
.chat {
  max-width: 720px;
  margin: 40px auto;
  font-family: system-ui, sans-serif;
}

.input-row {
  display: flex;
  gap: 8px;
}

.input-row input {
  flex: 1;
  padding: 8px 12px;
}

.steps {
  margin: 16px 0;
  padding-left: 20px;
  line-height: 1.9;
}

.step-start {
  color: #888;
}

.tool-call {
  color: #b45309;
}

.tool-result {
  color: #047857;
}

.final {
  color: #1d4ed8;
  font-weight: 600;
}

.answer {
  padding: 12px 16px;
  background: #f3f4f6;
  border-radius: 8px;
  white-space: pre-wrap;
}
</style>