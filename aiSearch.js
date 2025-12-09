import httpRequest from '../request/index'

// AI智能搜索
export function aiSearch(question) {
  return httpRequest({
    url: '/ai-search/search',
    method: 'post',
    data: { question },
    timeout: 60000  // AI 搜索需要更长时间:60秒
  })
}