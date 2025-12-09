// 导入axios实例
import httpRequest from '../request/index'

// 注册
export function register(data) {
    const params = new URLSearchParams()
    params.append('username', data.username)
    params.append('password', data.password)
    
    return httpRequest({
        url: '/auth/register',  // baseURL 会自动添加 /api 前缀
        method: 'post',
        data: params,
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    })
}

// 登录
export default function login(data) {
    const params = new URLSearchParams()
    params.append('username', data.username)
    params.append('password', data.password)
    
    return httpRequest({
        url: '/auth/login',  // baseURL 会自动添加 /api 前缀
        method: 'post',
        data: params,
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    })
}

// 获取用户信息
export function getUserInfo() {
    return httpRequest({
        url: '/auth/user',  // baseURL 会自动添加 /api 前缀
        method: 'get',
    })
}