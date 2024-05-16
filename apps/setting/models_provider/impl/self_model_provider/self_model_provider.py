# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： openai_model_provider.py
    @date：2024/3/28 16:26
    @desc:
"""
import os
from typing import Dict

from langchain.schema import HumanMessage

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import IModelProvider, ModelProvideInfo, BaseModelCredential, \
    ModelInfo, \
    ModelTypeConst, ValidCode
from setting.models_provider.impl.self_model_provider.model.self_chat_model import VLLMChatModel
from smartdoc.conf import PROJECT_DIR


class SelfLLMModelCredential(BaseForm, BaseModelCredential):

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], raise_exception=False):
        model_type_list = SelfModelProvider().get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')

        for key in ['api_base', 'api_key']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, f'{key} 字段为必填字段')
                else:
                    return False
        try:
            model = SelfModelProvider().get_model(model_type, model_name, model_credential)
            model.invoke([HumanMessage(content='你好')])
        except Exception as e:
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, f'校验失败,请检查参数是否正确: {str(e)}')
            else:
                return False
        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, 'api_key': super().encryption(model.get('api_key', ''))}

    api_base = forms.TextInputField('API 域名', required=True)
    api_key = forms.PasswordInputField('API Key', required=True)


self_llm_model_credential = SelfLLMModelCredential()

model_dict = {
    'phi-3': ModelInfo('phi-3', 'phi-3测试专用', ModelTypeConst.LLM, self_llm_model_credential),
    'Qwen-14B-Chat': ModelInfo('Qwen-14B-Chat', 'Qwen-14B-Chat测试专用', ModelTypeConst.LLM, self_llm_model_credential),
}


class SelfModelProvider(IModelProvider):

    def get_dialogue_number(self):
        return 3

    def get_model(self, model_type, model_name, model_credential: Dict[str, object], **model_kwargs) -> VLLMChatModel:
        # azure_chat_open_ai = OpenAIChatModel(
        #     model=model_name,
        #     openai_api_base=model_credential.get('api_base'),
        #     openai_api_key=model_credential.get('api_key')
        # )

        llm = VLLMChatModel(
            openai_api_key=model_credential.get('api_key'),
            openai_api_base=model_credential.get('api_base'),
            model_name=model_name,
            model_kwargs={},
        )
        return llm

    def get_model_credential(self, model_type, model_name):
        if model_name in model_dict:
            return model_dict.get(model_name).model_credential
        return self_llm_model_credential

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_self_provider', name='Self_VLLM', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'self_model_provider', 'icon',
                         'self_icon_svg')))

    def get_model_list(self, model_type: str):
        if model_type is None:
            raise AppApiException(500, '模型类型不能为空')
        return [model_dict.get(key).to_dict() for key in
                list(filter(lambda key: model_dict.get(key).model_type == model_type, model_dict.keys()))]

    def get_model_type_list(self):
        return [{'key': "大语言模型", 'value': "LLM"}]
