import json
import datetime
from Classes.PARAMs import customer_num, dockhub_num, depot_num
import time


class JasonLog:
    def __init__(self, log_url: str, result_url: str):
        self.log_loc: str = log_url
        self.log: str = log_url+"\dep"+ str(depot_num) + "_doc" + str(
        dockhub_num) + "_cus" + str(customer_num)+"_log.json"
        self.sa_result: str = result_url

    def save_to_json(self, data_dict: dict):
        dateArray = datetime.datetime.utcfromtimestamp(time.time())
        otherStyleTime = dateArray.strftime("%m%d")
        fileObject = open(self.sa_result+"_"+ str(otherStyleTime)+".json", 'w')
        for obj in data_dict.items():
            fileObject.write(str(obj))
            fileObject.write('\n')
        fileObject.close()

    def initiate_json(self):
        dateArray = datetime.datetime.utcfromtimestamp(time.time())
        parameters = {
            "initial time": dateArray.strftime("%Y-%m-%d %H:%M"),
            "customer nodes": customer_num,
            "docking hubs nodes":dockhub_num,
            "depot nodes": depot_num,
        }
        json.dumps(parameters)
        with open(self.log, 'w', encoding='utf-8') as file:
            json.dump(parameters, file)

    def append_to_json(self, parameters: dict):
        with open(self.log, "r", encoding="utf-8") as file:
            data = json.load(file)

        with open(self.log, "w", encoding="utf-8") as file:
            data.update(parameters)
            json.dump(data, file)