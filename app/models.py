from pydantic import BaseModel

class R(BaseModel):
    '''通用返回格式'''
    data: object
    msg: str
    code: int = 200
    
    @staticmethod
    def success(data=None):
        return R(data=data, msg="success")
    
    @staticmethod
    def success():
        return R(msg="success")
    
    @staticmethod
    def fail(msg):
        return R(msg=msg, code=500)
    
    @staticmethod
    def fail():
        return R(msg="fail", code=500)
    


class QueryRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    references: list


