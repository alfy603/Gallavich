// 导入axios实例
import service from '../request'

// 发表评论
export function postComments(vod_id, data) {
    var url = '/comments/publish/' + vod_id  // 🔥 修正路径
	return service({
		url: url,
		method: 'post',
		data: data,
	})
}

// 显示评论列表
export function showComments(vod_id) {
    var url = '/comments/show/' + vod_id  // 🔥 修正路径
	return service({
		url: url,
		method: 'get',
	})
}

// 回复评论
export function replyComment(comment_id, data) {
    var url = '/comments/reply/' + comment_id  // 🔥 修正路径
	return service({
		url: url,
		method: 'post',
        data: data
	})
}

// 删除评论
export function deleteComment(comment_id) {
    var url = '/comments/comment/' + comment_id  // 🔥 修正路径
    return service({
        url: url,
        method: 'delete',
    })
}

// 删除回复
export function deleteReply(reply_id) {
    var url = '/comments/reply/' + reply_id  // 🔥 修正路径
    return service({
        url: url,
        method: 'delete',
    })
}