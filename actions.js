export default {
    ADD_ACOUNTVUEX(store, countVuex) {
        store.commit('ADD_ACOUNTVUEX', countVuex)
    },
    
    // 🆕 添加 setUser action
    setUser({ commit }, user) {
        commit('SET_USER', user)
    },
    
    // 🆕 添加 setLoginState action
    setLoginState({ commit }, isLogin) {
        commit('SET_LOGIN_STATE', isLogin)
    }
}