<template>
    <el-row>
        <el-form size="large"
                id="comment-form"
                 :model="commentForm" 
                 class="demo-form-inline"
                 label-position="top"
                 style="width: 100%;"
                 label-width="100px">
            <el-form-item label="评论">
                <el-input v-model="commentForm.body" placeholder="请输入评论" type="textarea" :rows="4"/>
            </el-form-item>
            <el-form-item style="float:left;">
                <el-button type="primary" @click="publishComment">发表</el-button>
            </el-form-item>
        </el-form>
    </el-row>

    <div v-for="(comment, i) in comments" :key="i" class="comment">
        <el-divider />
        <!-- 评论人信息 -->
        <el-row class="comment-username" :id="comment.id">
            {{ comment.user_name }} &nbsp;&nbsp; {{comment.time }}
            <el-button link style="position:absolute; right: 10%" @click="showReplyForm">回复</el-button>
            <!-- 🔥 恢复删除评论按钮 -->
            <el-button 
                v-if="canDelete(comment)"
                link 
                style="position:absolute; right: 20%; color: #f56c6c;" 
                @click="deleteCommentHandler(comment.id)"
            >
                删除
            </el-button>
        </el-row>
        <!-- 评论内容 -->
        <el-row class="comment-p" style="padding: 10px" >
            {{ comment.body }}
        </el-row>
        <!-- 回复框 -->
        <el-row class="comment-reply-form" style="display: none" :id="'reply-' + comment.id">
            <el-form  :model="replyComment" size="small" style="width: 100%;">
                <el-form-item label="">
                    <el-input v-model="replyComment.body" placeholder="回复:" type="textarea" :rows="3" />
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="replyCommentPost">回复</el-button>
                </el-form-item>
            </el-form>
        </el-row>
        <!-- 此评论的回复 -->
        <div v-for="(reply, j) in comment.reply_list" :key="j" class="comment-replay">
            <el-row class="comment-username" :id="reply.id">
                {{ reply.user_name }} &nbsp;回复&nbsp; {{reply.reply_user_name }} &nbsp;&nbsp; {{ reply.time }}
                <el-button link style="position:absolute; right: 10%" @click="showReplyForm">回复</el-button>
                <!-- 🔥 恢复删除回复按钮 -->
                <el-button 
                    v-if="canDelete(reply)"
                    link 
                    style="position:absolute; right: 20%; color: #f56c6c;" 
                    @click="deleteReplyHandler(reply.id)"
                >
                    删除
                </el-button>
            </el-row>
            <el-row class="comment-p" style="padding: 10px" >{{ reply.body }}</el-row>
            <el-row class="comment-reply-form" style="display: none" :id="'reply-' + reply.id">
                <el-form  :model="replyComment" size="small" style="width: 100%;">
                    <el-form-item label="">
                      <el-input v-model="replyComment.body" placeholder="回复:" type="textarea" :rows="3" />
                    </el-form-item>
                    <el-form-item>
                        <el-button type="primary" @click="replyCommentPost">回复</el-button>
                    </el-form-item>
                </el-form>
            </el-row>
        </div>
    </div>
</template>

<script>
import { reactive } from 'vue'
import { useStore } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import { postComments, showComments, replyComment, deleteComment, deleteReply } from '../apis/comments'

export default {
    name: 'Comment',
    setup() {
        const store = useStore()
        
        const commentForm = reactive({
                body: '',
                user_id: '',
            })

        const replyComment = reactive({
                body: '',
                user_id: ''
            })

        return {
            store,
            commentForm,
            replyComment
        }
    },

    props: {
        vod_id: String
    },

    data() {
        return {
            comments:  [],
        }
    },

    methods: {
    // 🔥 检查是否有权限删除
    // 在 Comments.vue 中修改 canDelete 方法
canDelete(item) {
    if (!this.store.state.appStore.isLogining) return false
    
    const currentUser = this.store.state.appStore.user
    if (!currentUser || !currentUser.name) return false
    
    console.log('🔍 权限检查:', {
        评论用户: item.user_name,
        当前用户: currentUser.name,
        匹配: item.user_name === currentUser.name
    })
    
    // 🔥 使用用户名匹配（因为 user_id 是 undefined）
    return item.user_name === currentUser.name
},

    // 🔥 删除评论
    deleteCommentHandler(commentId) {
        console.log('🗑️ 准备删除评论:', commentId)
        ElMessageBox.confirm('确定要删除这条评论吗？', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
        }).then(() => {
            deleteComment(commentId).then(res => {
                console.log('📊 删除评论响应:', res)
                if (res.code === 200) {
                    ElMessage.success('评论删除成功')
                    this.showVodComment() // 重新加载评论列表
                } else {
                    ElMessage.error(res.message || '删除失败')
                }
            }).catch(error => {
                console.error('💥 删除评论失败:', error)
                ElMessage.error('删除失败: ' + error.message)
            })
        }).catch(() => {
            // 用户取消删除
            console.log('❌ 用户取消删除评论')
        })
    },

    // 🔥 删除回复
    deleteReplyHandler(replyId) {
        console.log('🗑️ 准备删除回复:', replyId)
        ElMessageBox.confirm('确定要删除这条回复吗？', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
        }).then(() => {
            deleteReply(replyId).then(res => {
                console.log('📊 删除回复响应:', res)
                if (res.code === 200) {
                    ElMessage.success('回复删除成功')
                    this.showVodComment() // 重新加载评论列表
                } else {
                    ElMessage.error(res.message || '删除失败')
                }
            }).catch(error => {
                console.error('💥 删除回复失败:', error)
                ElMessage.error('删除失败: ' + error.message)
            })
        }).catch(() => {
            // 用户取消删除
            console.log('❌ 用户取消删除回复')
        })
    },

    // 发表评论
    publishComment() {
        if (this.store.state.appStore.isLogining) {
            this.commentForm.user_id = this.store.state.appStore.user.id
            postComments(this.vod_id, this.commentForm).then(
                res => {
                    console.log('📝 发表评论响应:', res)
                    if (res.code == 200) {
                        this.showVodComment()
                        this.commentForm.body = ''
                        ElMessage.success('评论发表成功')
                        
                        // 触发统计更新
                        this.triggerStatsUpdate()
                    } else {
                        ElMessage({
                            message: res.message || '评论发表失败',
                            type: 'warning',
                        })
                    }
                }
            ).catch(error => {
                console.error('💥 发表评论失败:', error)
                ElMessage.error('发表评论失败: ' + error.message)
            })
        } else {
            ElMessage({
                message: "请先登录",
                type: 'warning',
            })
        }
    },

    showVodComment() {
        showComments(this.vod_id).then(
            res => {
                console.log('📝 获取评论响应:', res)
                if (res.code == 200) {
                    this.comments = res.data || []
                    console.log('✅ 评论数据加载成功:', this.comments)
                } else {
                    ElMessage({
                        message: res.message || '获取评论失败',
                        type: 'warning',
                    })
                }
            }
        ).catch(error => {
            console.error('💥 获取评论失败:', error)
            ElMessage.error('获取评论失败: ' + error.message)
        })
    },

    // 触发统计更新
    triggerStatsUpdate() {
        window.dispatchEvent(new CustomEvent('stats-update'))
        console.log('📊 已触发统计更新事件')
    },

    showReplyForm(e) {
        var comment_id = e.currentTarget.parentElement.id
        var replyForm = document.getElementById('reply-' + comment_id)
        if (replyForm.style.display === 'none') {
            replyForm.style.display = 'block'
        } else {
            replyForm.style.display = 'none'
        }
    },

    replyCommentPost(e) {
        if (this.store.state.appStore.isLogining) {
            var comment_id = e.currentTarget.parentElement.parentElement.parentElement.parentElement.id.split('-')[1]
            this.replyComment.user_id = this.store.state.appStore.user.id
            console.log('📝 回复评论数据:', this.replyComment)
            replyComment(comment_id, this.replyComment).then(
                res => {
                    console.log('📝 回复评论响应:', res)
                    if (res.code == 200) {
                        this.replyComment.body = ''
                        this.showVodComment()
                        ElMessage.success('回复成功')
                        
                        // 触发统计更新
                        this.triggerStatsUpdate()
                    } else {
                        ElMessage({
                            message: res.message || '回复失败',
                            type: 'warning',
                        })
                    }
                }
            ).catch(error => {
                console.error('💥 回复评论失败:', error)
                ElMessage.error('回复失败: ' + error.message)
            })
        } else {
            ElMessage({
                message: "请先登录",
                type: 'warning',
            })
        }
    }
},

    created() {
        this.showVodComment()
    }
}
</script>

<style>
#comment-form .el-form-item__label {
  font-size: 18px;
  font-weight: bold;
}

.el-row.comment-username {
    color: #777888;
    position: relative;
}

div.comment-replay {
    padding-left: 3%;
}
</style>