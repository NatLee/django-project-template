from datetime import datetime
import os
from django.conf import settings
import pathlib

RemainDays = settings.LOGS_REMOVE_DAYS
rotation = '10 mb'

file_path = pathlib.Path(__file__).parent.resolve()

class BytesExchange:
    def __init__(self):
        kb = float(1024)
        self.source = {'kb': kb, 'mb':float(kb ** 2), 'gb':float(kb ** 3), 'tb':float(kb ** 4)}
        
    def __input_check(self, _bytes, _type):
        check = False
        if _bytes: 
            check=True
        if _type:
            _type = _type.lower()
        return check, _bytes, _type

    
    def __exchange(self, _bytes, _type):
        if _type:
            return '{0:.2f} {1}'.format(_bytes / self.source[_type], _type.upper())
        else:
            if _bytes < self.source['kb']:
                return '{0} {1}'.format(_bytes,'Bytes' if 0 == _bytes > 1 else 'Byte')
            elif self.source['kb'] <= _bytes < self.source['mb']:
                return '{0:.2f} KB'.format(_bytes / self.source['kb'])
            elif self.source['mb'] <= _bytes < self.source['gb']:
                return '{0:.2f} MB'.format(_bytes / self.source['mb'])
            elif self.source['gb'] <= _bytes < self.source['tb']:
                return '{0:.2f} GB'.format(_bytes / self.source['gb'])
            elif self.source['tb'] <= _bytes:
                return '{0:.2f} TB'.format(_bytes / self.source['tb'])
    
    def main(self, _bytes=None, _type=None):
        msg = None
        ret = None 
        check,_bytes, _type = self.__input_check(_bytes, _type)
        if check:
            _bytes = float(_bytes)
            ret = self.__exchange(_bytes, _type)
        else:
            msg = 'Not Frond bytes data'
        return msg, ret


class logswriter:
    def __init__(
        self,
        SystemName,
        FileName,
        LogPath=str(file_path).replace("/common", "") + "/logs/",
        RemainDays=RemainDays,
        rotation= rotation
    ):
        self.system_name = SystemName
        self.file_name = FileName
        self.log_path = LogPath
        self.system_path = LogPath + self.system_name + "/"
        self.remaindays = RemainDays
        
        rotation = rotation.split(' ')
        self.bytes = float(rotation[0])
        self.type = rotation[1]
        self.BytesExchange_ = BytesExchange()
        
        self.remove_log()
        
    def rotation_check(self, log_path):
        check = False
        b = os.path.getsize(log_path)
        _, ret = self.BytesExchange_ .main(_bytes=b, _type=self.type)
        if ret:
            if float(ret.split(' ')[0]) > self.bytes:
                check = True
        return check

    def write_log(self, massage):
        log_dt = datetime.now().strftime("%Y%m%d")
        log_path = f"{self.system_path}{self.file_name}_{log_dt}.log"
        try:
            try:
                check = self.rotation_check(log_path)
            except:
                check = True
            if check:
                active = 'w+'
            else:
                active = 'a+'
            with open(log_path, active) as f:
                f.write(
                    datetime.now().strftime("%Y-%m-%-d %H:%M:%S")
                    + ": "
                    + str(massage)
                    + "\n"
                )
        except Exception as e:
            print(e)

    def remove_log(self):
        try:
            for i in os.listdir(self.system_path):
                if i.startswith(self.file_name) and i.endswith(".log"):
                    dt_str = i.replace(self.file_name + "_", "").replace(".log", "")
                    dt = datetime.strptime(dt_str, "%Y%m%d")
                    try:
                        if (datetime.now() - dt).days >= self.remaindays:
                            os.remove(self.system_path + i)
                            self.write_log("remove" + str(i))
                    except Exception as e:
                        self.write_log(
                            f"[Error] remove before {self.remaindays} days logs... , error massage: {e}"
                        )
        except Exception as e:
            if "logs" not in list(
                map(lambda x: x, os.listdir(self.log_path.replace("/logs/", "")))
            ):
                os.mkdir(self.log_path)
            os.mkdir(self.system_path)
            self.write_log(f"[Info] Create Folder")


if __name__ == "__main__":
    pass
