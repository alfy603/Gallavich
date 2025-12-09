import httpRequest from '../request/index'

// 用户管理
export const getUsers = (params) => {
  return httpRequest({
    url: '/admin/users',
    method: 'get',
    params: params
  })
}
// 在 admin.js 文件中添加以下API方法

// 用户管理 - 添加用户
export const createUser = (data) => {
  return httpRequest({
    url: '/admin/users',
    method: 'post',
    data: data
  })
}

// 视频管理 - 添加视频
export const createVideo = (data) => {
  return httpRequest({
    url: '/admin/videos',
    method: 'post',
    data: data
  })
}

// 评论管理 - 添加评论
export const createComment = (data) => {
  return httpRequest({
    url: '/admin/comments',
    method: 'post',
    data: data
  })
}

// 获取视频分类
export const getVideoTypes = () => {
  return httpRequest({
    url: '/admin/video-types',
    method: 'get'
  })
}

// 获取用户列表(简单版,用于评论选择)
export const getSimpleUsers = () => {
  return httpRequest({
    url: '/admin/users/simple',  // 使用新的专用接口
    method: 'get'
  })
}

// 获取视频列表(简单版,用于评论选择)
export const getSimpleVideos = () => {
  return httpRequest({
    url: '/admin/videos/simple',  // 使用新的专用接口
    method: 'get'
  })
}

export const updateUserRole = (userId, data) => {
  return httpRequest({
    url: `/admin/users/${userId}/role`,
    method: 'put',
    data: data
  })
}

export const updateUserStatus = (userId, data) => {
  return httpRequest({
    url: `/admin/users/${userId}/status`,
    method: 'put',
    data: data
  })
}

// 视频管理
export const getVideos = (params) => {
  return httpRequest({
    url: '/admin/videos',
    method: 'get',
    params: params
  })
}

// 视频管理 - 添加删除方法
export const deleteVideo = (videoId) => {
  console.log(`🗑️ 删除视频 - 视频ID: ${videoId}`)
  return httpRequest({
    url: `/admin/videos/${videoId}`,
    method: 'delete'
  })
}

// 评论管理
export const getComments = (params) => {
  return httpRequest({
    url: '/admin/comments',
    method: 'get',
    params: params
  })
}

export const deleteCommentAdmin = (commentId) => {
  return httpRequest({
    url: `/admin/comments/${commentId}`,
    method: 'delete'
  })
}

// 数据统计
export const getStats = () => {
  return httpRequest({
    url: '/admin/stats',
    method: 'get'
  })
}


// 在 admin.js 中添加直播管理API

// 直播流管理
export const getLiveStreams = (params) => {
  return httpRequest({
    url: '/admin/live/streams',
    method: 'get',
    params: params
  })
}

export const deleteLiveStreamAdmin = (streamId) => {
  return httpRequest({
    url: `/admin/live/streams/${streamId}`,
    method: 'delete'
  })
}

export const updateLiveStreamStatus = (streamId, data) => {
  return httpRequest({
    url: `/admin/live/streams/${streamId}/status`,
    method: 'put',
    data: data
  })
}

// 创建直播流
export const createLiveStreamAdmin = (data) => {
  return httpRequest({
    url: '/admin/live/streams',
    method: 'post',
    data: data
  })
}

// 直播评论管理
export const getLiveComments = (params) => {
  return httpRequest({
    url: '/admin/live/comments',
    method: 'get',
    params: params
  })
}

export const deleteLiveCommentAdmin = (commentId) => {
  return httpRequest({
    url: `/admin/live/comments/${commentId}`,
    method: 'delete'
  })
}

// 创建直播评论
export const createLiveCommentAdmin = (data) => {
  return httpRequest({
    url: '/admin/live/comments',
    method: 'post',
    data: data
  })
}

// 新增：管理员获取所有直播流（新API路径）
export function getLiveStreamsNew(params) {
  return httpRequest({
    url: '/live/admin/streams',
    method: 'get',
    params: params
  })
}

// 新增：管理员更新直播状态（新API路径）
export function updateLiveStreamStatusNew(streamId, data) {
  return httpRequest({
    url: `/live/admin/stream/${streamId}/status`,
    method: 'post',
    data: data
  })
}

// 新增：管理员删除直播（新API路径）
export function deleteLiveStreamAdminNew(streamId) {
  return httpRequest({
    url: `/live/admin/stream/${streamId}`,
    method: 'delete'
  })
}