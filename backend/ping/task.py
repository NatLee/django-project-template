from django_rq import job

@job
def ping_job(msg:str):
    return msg
