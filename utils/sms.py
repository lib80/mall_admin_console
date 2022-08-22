from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkcore.auth.credentials import StsTokenCredential
from aliyunsdkdysmsapi.request.v20170525.SendSmsRequest import SendSmsRequest
from utils.const import ALI_KEY_ID, ALI_KEY_SECRET, SMS_SIGN_NAME, SMS_TEMPLATE_CODE


credentials = AccessKeyCredential(ALI_KEY_ID, ALI_KEY_SECRET)
# use STS Token
# credentials = StsTokenCredential('<your-access-key-id>', '<your-access-key-secret>', '<your-sts-token>')
client = AcsClient(region_id='cn-shenzhen', credential=credentials)
request = SendSmsRequest()
request.set_accept_format('json')
request.set_SignName(SMS_SIGN_NAME)
request.set_TemplateCode(SMS_TEMPLATE_CODE)


def send_sms(mobile: str, captcha: str):
    request.set_PhoneNumbers(mobile)
    request.set_TemplateParam({"code": captcha})
    resp = client.do_action_with_exception(request)
    return resp

