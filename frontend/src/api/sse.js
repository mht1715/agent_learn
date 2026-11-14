import axios from 'axios'

const http = axios.create({
    baseURL: '/api',
    timeout: 0, // SSE 长连接不能设超时
})

/**
 * payload: { message: string | null, session_id: string, action: 'chat' | 'resume' }
 */
export function chatStream(payload, onEvent) {
    let consumed = 0
    let buffer = ''

    return http
        // 把 message 换成 payload
        .post('/chat/stream', payload, {
            headers: {
                Accept: 'text/event-stream',
                'Content-Type': 'application/json',
            },
            responseType: 'text',
            onDownloadProgress: (progressEvent) => {
                const xhr = progressEvent.event.target
                const full = xhr.responseText || ''
                const chunk = full.slice(consumed)
                consumed = full.length
                buffer += chunk
                const frames = buffer.split('\n\n')
                buffer = frames.pop() ?? ''

                for (const frame of frames) {
                    if (!frame.startsWith('data: ')) continue
                    try {
                        onEvent(JSON.parse(frame.slice(6)))
                    } catch (e) {
                        console.warn('SSE 帧解析失败:', frame)
                    }
                }
            },
        })
        .then(() => {
            if (buffer.startsWith('data: ')) {
                try {
                    onEvent(JSON.parse(buffer.slice(6)))
                } catch { /* ignore */
                }
            }
        })
}

export function getChatState(sessionId) {
    return http.get('/chat/state', {
        params: { session_id: sessionId }
    })
}