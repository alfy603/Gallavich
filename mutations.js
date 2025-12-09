export default {
    ADD_ACOUNTVUEX(state, countVuex) {
        state.countVuex = countVuex
    },
    
    // 🆕 添加 setUser mutation
    SET_USER(state, user) {
        state.user = user
        // 同时保存到 localStorage
        window.localStorage.setItem('user', JSON.stringify(user))
    },
    
    // 🆕 添加 setLoginState mutation  
    SET_LOGIN_STATE(state, isLogin) {
        state.isLogining = isLogin
        if (!isLogin) {
            window.localStorage.removeItem('token')
            window.localStorage.removeItem('user')
            state.user = {}  // 清空用户信息
        }
    }
}