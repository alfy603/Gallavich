<template>
  <div class="login-body">
    <div class="login-container">
      <div class="head">
        <div class="name">
          <div class="title">Avalon</div>
          <div class="tips">动漫、视频交流分享网站</div>
        </div>
      </div>
      <el-form label-position="top" :rules="rules" :model="ruleForm" ref="loginForm" class="login-form">
        <el-form-item label="账号" prop="username">
          <el-input type="text" v-model.trim="ruleForm.username" autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input type="password" v-model.trim="ruleForm.password" autocomplete="off"></el-input>
        </el-form-item>

        <el-form-item v-if="haveAccount">
          <el-button type="primary" link style="margin-bottom:10px" @click="switchToRegister">还没有账户?</el-button>
          <el-button style="width: 100%" type="primary" @click="submitForm">立即登录</el-button>
          <el-checkbox v-model="checked" @change="!checked">下次自动登录</el-checkbox>
        </el-form-item>

        <el-form-item v-else>
          <el-button type="primary" link style="margin-bottom:10px" @click="switchToLogin">返回登录</el-button>
          <el-button style="width: 100%" type="primary" @click="submitRegisterForm">注册</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script>
// 登录页
import { reactive, ref, toRefs } from 'vue'
import { useStore } from 'vuex'
import { localSet } from '../utils'
import login, { register } from '../apis/login'
import { ElMessage } from 'element-plus'

export default {
  name: 'Login',
  setup() {
    const loginForm = ref(null)
    const haveAccount = ref(true)
    const store = useStore()
    
    const state = reactive({
      ruleForm: {
        username: '',
        password: ''
      },
      checked: true,
      rules: {
        username: [
          { required: true, message: '账户不能为空', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '密码不能为空', trigger: 'blur' }
        ]
      }
    })

    // 登录提交
    const submitForm = async () => {
      try {
        console.log('🔄 开始登录...')
        console.log('📝 登录表单数据:', state.ruleForm)
        
        if (!loginForm.value) {
          ElMessage.error('表单未初始化')
          return
        }
        
        // 表单验证
        const valid = await loginForm.value.validate()
        if (!valid) {
          ElMessage.error('请填写完整信息')
          return
        }

        const response = await login({
          username: state.ruleForm.username,
          password: state.ruleForm.password
        })
        
        console.log('✅ 登录响应:', response)
        
        if (response && response.code === 200) {
    console.log('🎉 登录成功!')
    
    ElMessage.success({
        message: '登录成功！欢迎回来！',
        duration: 2000,
        showClose: true
    })
    
    // 保存 token
    if (response.data && response.data.token) {
        localSet('token', response.data.token)
    }
    
    // 创建完整的用户信息
    const userInfo = {
        id: response.data.user_id,
        name: response.data.username,
        role: response.data.role || 'user'
    }
    
    // 保存到 localStorage
    localStorage.setItem('user', JSON.stringify(userInfo))
    
    // 🆕 使用新的 mutations 更新 Vuex store
    store.commit('SET_LOGIN_STATE', true)
    store.commit('SET_USER', userInfo)
    
    console.log('✅ Vuex 状态已更新:', store.state.appStore.user)
    
    setTimeout(() => {
        window.location.href = '/'
    }, 1500)
} else {
          console.log('❌ 登录失败:', response?.message || '未知错误')
          ElMessage.error(response?.message || '登录失败')
        }
      } catch (error) {
        console.error('💥 登录异常:', error)
        ElMessage.error('登录失败，请重试')
      }
    }

    // 注册提交
    const submitRegisterForm = async () => {
      try {
        console.log('🔄 开始注册...')
        console.log('📝 注册表单数据:', state.ruleForm)
        
        if (!loginForm.value) {
          ElMessage.error('表单未初始化')
          return
        }
        
        // 表单验证
        const valid = await loginForm.value.validate()
        if (!valid) {
          ElMessage.error('请填写完整信息')
          return
        }

        const response = await register({
          username: state.ruleForm.username,
          password: state.ruleForm.password
        })
        
        console.log('✅ 注册响应:', response)
        
        // 在注册成功后的处理中（大约第 140 行左右）
if (response && response.code === 200) {
  console.log('🎉 注册成功!')
  
  // 🎯 添加注册成功提示
  ElMessage.success({
    message: '注册成功！请登录您的账户',
    duration: 2000,
    showClose: true
  })
  
  // 切换到登录界面
  haveAccount.value = true
  
  // 清空表单
  state.ruleForm.username = ''
  state.ruleForm.password = ''
} else {
          console.log('❌ 注册失败:', response?.message || '未知错误')
          ElMessage.error(response?.message || '注册失败')
        }
      } catch (error) {
        console.error('💥 注册异常:', error)
        ElMessage.error('注册失败，请重试')
      }
    }

    // 切换到注册
    const switchToRegister = () => {
      haveAccount.value = false
      state.ruleForm.username = ''
      state.ruleForm.password = ''
    }

    // 切换到登录
    const switchToLogin = () => {
      haveAccount.value = true
      state.ruleForm.username = ''
      state.ruleForm.password = ''
    }

    const resetForm = () => {
      if (loginForm.value) {
        loginForm.value.resetFields()
      }
    }

    return {
      ...toRefs(state),
      haveAccount,
      loginForm,
      submitForm,
      submitRegisterForm,
      resetForm,
      switchToLogin,
      switchToRegister
    }
  }
}
</script>

<style scoped>
  .login-body {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100vh;
    padding: 5px;
    background-color: #fff;
  }
  .login-container {
    width: 420px;
    height: 500px;
    background-color: #fff;
    border-radius: 4px;
    box-shadow: 0px 21px 41px 0px rgba(0, 0, 0, 0.2);
    padding: 20px;
  }
  .head {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 40px 0 20px 0;
  }
  .head img {
    width: 100px;
    height: 100px;
    margin-right: 20px;
  }
  .head .title {
    font-size: 28px;
    color: #409EFF;
    font-weight: bold;
    text-align: center;
  }
  .head .tips {
    font-size: 12px;
    color: #999;
    text-align: center;
    margin-top: 8px;
  }
  .login-form {
    width: 100%;
    margin: 0 auto;
  }
</style>
<style>
  .el-form--label-top .el-form-item__label {
    padding: 0;
  }
  .login-form .el-form-item {
    margin-bottom: 20px;
  }
</style>