import httpRequest from '../request/index'

// 获取直播列表
export function getLiveStreams(params) {
    return httpRequest({
        url: '/live/streams',  // 添加 /api 前缀
        method: 'get',
        params: params
    })
}

// 创建直播
export function createLiveStream(data) {
    return httpRequest({
        url: '/live/stream/create',  
        method: 'post',
        data: data
    })
}

// 结束直播
export function endLiveStream(streamId) {
    return httpRequest({
        url: `/live/stream/${streamId}/end`,  
        method: 'post'
    })
}

// 删除直播
export function deleteLiveStream(streamId) {
    return httpRequest({
        url: `/live/stream/${streamId}/delete`,
        method: 'delete'
    })
}

// 获取直播详情
export function getLiveStreamDetail(streamId) {
    return httpRequest({
        url: `/live/stream/${streamId}`,  
        method: 'get'
    })
}

// 点赞直播
export function likeLiveStream(streamId) {
    return httpRequest({
        url: `/live/stream/${streamId}/like`,  
        method: 'post'
    })
}

// 发送评论
export function addLiveComment(data) {
    return httpRequest({
        url: '/live/comment',  
        method: 'post',
        data: data
    })
}

// 获取评论
export function getLiveComments(streamId) {
    return httpRequest({
        url: `/live/comments/${streamId}`,  
        method: 'get'
    })
}