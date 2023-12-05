<template>
  <el-dialog
    v-model="dialogVisible"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    :before-close="close"
  >
    <template #header="{ close, titleId, titleClass }">
      <el-breadcrumb separator=">">
        <el-breadcrumb-item>
          <span @click="toSelectProvider" class="select-provider"
            >选择供应商</span
          ></el-breadcrumb-item
        >
        <el-breadcrumb-item
          ><span class="active-breadcrumb">{{
            `添加 ${providerValue?.name} 模型`
          }}</span></el-breadcrumb-item
        >
      </el-breadcrumb>
    </template>

    <DynamicsForm
      v-model="form_data"
      :render_data="model_form_field"
      :model="form_data"
      ref="dynamicsFormRef"
      label-position="top"
      require-asterisk-position="right"
    >
      <template #default>
        <el-form-item label="模型名称" prop="name" :rules="base_form_data_rule.name">
          <el-input
            v-model="base_form_data.name"
            maxlength="20"
            show-word-limit
            placeholder="请给基础模型设置一个名称"
          />
        </el-form-item>
        <el-form-item label="模型类型" prop="model_type" :rules="base_form_data_rule.model_type">
          <el-select
            v-loading="model_type_loading"
            @change="list_base_model($event)"
            style="width: 100%"
            v-model="base_form_data.model_type"
            class="m-2"
            placeholder="请选择模型类型"
          >
            <el-option
              v-for="item in model_type_list"
              :key="item.value"
              :label="item.key"
              :value="item.value"
            ></el-option
          ></el-select>
        </el-form-item>
        <el-form-item label="基础模型" prop="model_name" :rules="base_form_data_rule.model_name">
          <el-select
            @change="getModelForm($event)"
            v-loading="base_model_loading"
            style="width: 100%"
            v-model="base_form_data.model_name"
            class="m-2"
            placeholder="请选择模型类型"
          >
            <el-option
              v-for="item in base_model_list"
              :key="item.name"
              :label="item.name"
              :value="item.name"
            ></el-option
          ></el-select>
        </el-form-item>
      </template>
    </DynamicsForm>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="close">取消</el-button>
        <el-button type="primary" @click="submit" :loading="loading"> 添加 </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Provider, BaseModel } from '@/api/type/model'
import type { Dict, KeyValue } from '@/api/type/common'
import ModelApi from '@/api/model'
import type { FormField } from '@/components/dynamics-form/type'
import DynamicsForm from '@/components/dynamics-form/index.vue'
import type { FormRules } from 'element-plus'
import { MsgSuccess } from '@/utils/message'
const providerValue = ref<Provider>()
const dynamicsFormRef = ref<InstanceType<typeof DynamicsForm>>()
const emit = defineEmits(['change', 'submit'])
const loading = ref<boolean>(false)
const model_type_loading = ref<boolean>(false)
const base_model_loading = ref<boolean>(false)
const model_type_list = ref<Array<KeyValue<string, string>>>([])

const base_model_list = ref<Array<BaseModel>>()
const model_form_field = ref<Array<FormField>>([])
const dialogVisible = ref<boolean>(false)

const base_form_data_rule = ref<FormRules>({
  name: { required: true, trigger: 'blur', message: '模型名不能为空' },
  model_type: { required: true, trigger: 'change', message: '模型类型不能为空' },
  model_name: { required: true, trigger: 'change', message: '基础模型不能为空' }
})

const base_form_data = ref<{
  name: string

  model_type: string

  model_name: string
}>({ name: '', model_type: '', model_name: '' })

const credential_form_data = ref<Dict<any>>({})

const form_data = computed({
  get: () => {
    return {
      ...credential_form_data.value,
      name: base_form_data.value.name,
      model_type: base_form_data.value.model_type,
      model_name: base_form_data.value.model_name
    }
  },
  set: (event: any) => {
    credential_form_data.value = event
  }
})

const getModelForm = (model_name: string) => {
  if (providerValue.value) {
    ModelApi.getModelCreateForm(
      providerValue.value.provider,
      form_data.value.model_type,
      model_name
    ).then((ok) => {
      model_form_field.value = ok.data
      // 渲染动态表单
      dynamicsFormRef.value?.render(model_form_field.value, undefined)
    })
  }
}

const open = (provider: Provider) => {
  ModelApi.listModelType(provider.provider, model_type_loading).then((ok) => {
    model_type_list.value = ok.data
  })
  providerValue.value = provider
  dialogVisible.value = true
}

const list_base_model = (model_type: any) => {
  form_data.value.model_name = ''
  if (providerValue.value) {
    ModelApi.listBaseModel(providerValue.value.provider, model_type, base_model_loading).then(
      (ok) => {
        base_model_list.value = ok.data
      }
    )
  }
}
const close = () => {
  base_form_data.value = { name: '', model_type: '', model_name: '' }
  credential_form_data.value = {}
  dialogVisible.value = false
}
const submit = () => {
  dynamicsFormRef.value?.validate().then(() => {
    if (providerValue.value) {
      ModelApi.createModel(
        {
          ...base_form_data.value,
          credential: credential_form_data.value,
          provider: providerValue.value.provider
        },
        loading
      ).then((ok) => {
        close()
        MsgSuccess('创建模型成功')
        emit('submit')
      })
    }
  })
}
const toSelectProvider = () => {
  close()
  emit('change')
}
defineExpose({ open, close })
</script>
<style lang="scss" scoped>
.select-provider {
  font-size: 16px;
  color: rgba(100, 106, 115, 1);
  font-weight: 400;
  line-height: 24px;
  cursor: pointer;
  &:hover {
    color: var(--el-color-primary);
  }
}
.active-breadcrumb {
  font-size: 16px;
  color: rgba(31, 35, 41, 1);
  font-weight: 500;
  line-height: 24px;
}
</style>