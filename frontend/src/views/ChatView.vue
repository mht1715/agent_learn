<script setup>
import {ref, onMounted} from 'vue'
import {chatStream, getChatState} from '../api/sse'

const input = ref('帮我取消订单 A1001') // 默认填审批测试用例
const events = ref([])
const answer = ref('')
const loading = ref(false)

// 新增：会话 ID 和审批状态
const sessionId = ref('')
const needApproval = ref(false)

onMounted(async () => {
  // 1. 获取 sessionId
  let sid = localStorage.getItem('agent_session_id')
  if (!sid) {
    sid = crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).substring(2)
    localStorage.setItem('agent_session_id', sid)
  }
  sessionId.value = sid

  // 2. 关键：检查后端是否有未完成的挂起任务（应对刷新）
  try {
    const resp = await getChatState(sessionId.value)
    if (resp.data && resp.data.interrupted) {
      // 恢复事件流 UI 显示
      events.value = resp.data.tool_calls.map(tc => ({
        type: 'tool_call',
        name: tc.name,
        args: tc.args
      }))
      answer.value = resp.data.message
      // 重新唤起审批框
      needApproval.value = true
    }
  } catch (e) {
    console.warn("获取初始状态失败", e)
  }
})

// 修改：接收 action 参数
async function send(action = 'chat') {
  if (loading.value) return
  if (action === 'chat' && !input.value.trim()) return

  if (action === 'chat') {
    events.value = []
    answer.value = ''
  }

  loading.value = true
  needApproval.value = false // 重置审批状态

  const payload = {
    message: action === 'chat' ? input.value : null,
    session_id: sessionId.value,
    action: action
  }

  try {
    // 修改：传入 payload 对象
    await chatStream(payload, (ev) => {
      events.value.push(ev)
      if (ev.type === 'final') answer.value = ev.answer
      if (ev.type === 'error') answer.value = ev.message
      // 新增：拦截中断事件
      if (ev.type === 'interrupt') {
        answer.value = ev.answer
        needApproval.value = true
      }
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
          @keyup.enter="send('chat')"
      />
      <button :disabled="loading" @click="send('chat')">
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
        <!-- 新增：中断提示 -->
        <span v-else-if="ev.type === 'interrupt'" class="interrupt">
          ⚠️ {{ ev.answer }}
        </span>
        <span v-else-if="ev.type === 'final'" class="final">
          完成（共 {{ ev.steps }} 步，状态：{{ ev.status }}）
        </span>
      </li>
    </ol>

    <p v-if="answer" class="answer">{{ answer }}</p>

    <!-- 新增：审批操作区 -->
    <div v-if="needApproval" class="approval-box">
      <p>该操作需要人工审批，是否同意继续执行？</p>
      <button class="btn-approve" @click="send('resume')" :disabled="loading">同意并执行</button>
      <button class="btn-reject" @click="needApproval = false" :disabled="loading">拒绝</button>
    </div>
  </div>
</template>

<style scoped>
/* 保留你原有的样式 */
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

/* 新增的样式 */
.interrupt {
  color: #dc2626;
  font-weight: bold;
}

.approval-box {
  margin-top: 16px;
  padding: 16px;
  border: 1px solid #fca5a5;
  background: #fef2f2;
  border-radius: 8px;
}

.btn-approve {
  background: #dc2626;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 8px;
}

.btn-reject {
  background: #e5e7eb;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>