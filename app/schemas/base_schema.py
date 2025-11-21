from pydantic import BaseModel

class R(BaseModel):
    '''通用返回格式'''
    data: dict | None = None
    msg: str | None = "success"
    code: int = 200
    
    @staticmethod
    def success():
        return R(data=None, msg="success")
    
    @staticmethod
    def success_data(data=None):
        return R(data=data, msg="success")
    
    @staticmethod
    def fail():
        return R(msg="fail", code=500)
    
    @staticmethod
    def fail_msg(msg):
        return R(msg=msg, code=500)
    
    def fail_msg_code(code:int, msg:str):
        return R(code=code, msg=msg)
    
