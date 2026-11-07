import axios from 'axios'

const http = axios.create({
    baseURL: '/api',
    timeout: 0, // SSE 长连接不能设超时
})

/**
 * 用 Axios 的 onDownloadProgress 逐块消费 SSE。
 * onEvent: (event: object) => void，每解析出一个完整 SSE 帧就回调一次。
 * 返回一个 Promise，流结束时 resolve。
 */
export function chatStream(message, onEvent) {
    let consumed = 0   // 已经解析到的 responseText 位置
    let buffer = ''    // 半帧缓存

    return http
        .post('/chat/stream', {message}, {
            headers: {
                Accept: 'text/event-stream',
                'Content-Type': 'application/json',
            },
            responseType: 'text',
            onDownloadProgress: (progressEvent) => {
                const xhr = progressEvent.event.target
                const full = xhr.responseText || ''

                // 只取新增部分，避免重复解析
                const chunk = full.slice(consumed)
                consumed = full.length

                buffer += chunk
                const frames = buffer.split('\n\n')
                buffer = frames.pop() ?? ''   // 最后一段可能不完整，留到下次

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
            // 流结束后，buffer 里理论上不应再有完整帧；如有残留尝试兜底解析
            if (buffer.startsWith('data: ')) {
                try {
                    onEvent(JSON.parse(buffer.slice(6)))
                } catch { /* ignore */
                }
            }
        })
}