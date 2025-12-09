import service from '../request'

// 检查收藏状态
export const isCollectVideo = (params) => {
  return service({
    url: '/collection/is_collection',
    method: 'get',
    params: params
  })
}

// 添加收藏
export const addCollectVideo = (data) => {
  return service({
    url: '/collection/add',
    method: 'post',
    data: data
  })
}

// 取消收藏
export const removeCollectVideo = (data) => {
  return service({
    url: '/collection/remove',
    method: 'delete',
    data: data
  })
}

// 获取收藏列表 - 添加这个导出
export const showCollectVideo = (params) => {
  return service({
    url: '/collection/show',
    method: 'get',
    params: params
  })
}