import json
import random
import threading
import time

import paho.mqtt.client as mqtt
import requests
from checklib import *

from minijit import get_random_code


def connect_as_new_kube(IP):
    response = requests.get(f"http://{IP}:3000/api/connect_as_new_kube", headers={"User-Agent": rnd_useragent()})
    if response.status_code == 200:
        return response.json()
    else:
        return None


class Device:
    def __init__(self, ip, override_id=None):
        self.ip = ip
        if override_id:
            self.id = override_id
        else:
            conn_details = connect_as_new_kube(ip)
            self.id = conn_details["kube_id"]
        self.mqtt_topic = f"/kube_comms/{self.id}"

        self.mqtt_client = mqtt.Client(client_id=self.id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
        self.mqtt_client.on_message = self.mqtt_on_message
        self.mqtt_client.on_connect = self.mqtt_on_connect
        self.mqtt_client.username_pw_set(username="device", password="device")

        self.mqtt_client.connect(ip, 1883, 60)

        self.mqtt_client.loop_start()

    def mqtt_on_connect(self, client, userdata, flags, reason_code, properties):
        #print(f"Connected with result code {reason_code}")
        client.subscribe(self.mqtt_topic)

    def mqtt_on_message(self, client, userdata, msg):
        pass
        #print('mqtt:', msg.topic + " " + str(msg.payload))

    def check_mqtt_to_ws_connectivity(self):  # send MQTT -> recv WS
        #print('mqtt -> ws check')
        data = rnd_string(random.randint(8, 100))

        response = requests.get(f"http://{self.ip}:3000/api/client/receive?kube={self.id}", stream=True,
                                headers={"User-Agent": rnd_useragent()})
        time.sleep(0.1)
        self.mqtt_client.publish(self.mqtt_topic, data, qos=2, retain=False)

        for line in response.iter_lines():
            if line and line == b"data: " + data.encode():
                return True
        return False

    def check_ws_to_mqtt_connectivity(self):  # send WS -> recv MQTT
        #print('ws -> mqtt check')

        data = rnd_string(random.randint(8, 100))
        event = threading.Event()
        success = False

        def on_message(client, userdata, msg):
            nonlocal success
            if msg.payload == data.encode():
                success = True
                event.set()

        self.mqtt_client.message_callback_add(self.mqtt_topic, on_message)

        time.sleep(0.1)
        self.transmit_message(data)

        event.wait(timeout=5)
        self.mqtt_client.message_callback_remove(self.mqtt_topic)

        return success

    def check_code_exec_capability(self):  # send WS -> recv MQTT
        #print('code exec capability check')
        code, expected_result = get_random_code()

        event = threading.Event()
        success = False

        def on_message(client, userdata, msg):
            nonlocal success
            try:
                #print(json.loads(msg.payload.decode('utf-8'))["cloud_accel_result"])
                if json.loads(msg.payload.decode('utf-8'))["cloud_accel_result"] == expected_result:
                    success = True
                    event.set()
            except:
                pass

        self.mqtt_client.message_callback_add(self.mqtt_topic, on_message)

        self.transmit_message(json.dumps({"e": "execute_on_cloud_accelerator", "code": code}))

        event.wait(timeout=5)
        self.mqtt_client.message_callback_remove(self.mqtt_topic)
        return success

    def put_flag_1(self, flag):  # mqtt flag (in info)
        pubinfo = self.mqtt_client.publish(self.mqtt_topic, json.dumps({
            "e": "add_flag",
            "flag": flag
        }), qos=2, retain=False)
        pubinfo.wait_for_publish()
        return pubinfo.is_published()

    def transmit_message(self, message):
        response = requests.post(f"http://{self.ip}:3000/api/client/transmit", params={"kube": self.id},
                                 data=message, headers={"Content-Type": "application/octet-stream",
                                                        "User-Agent": rnd_useragent()})
        return response.status_code == 200

    def retrieve_flag_1(self):
        return requests.get(f"http://{self.ip}:3000/api/client/info?kube={self.id}",
                            headers={"User-Agent": rnd_useragent()}).text[1:-1]

    def put_flag_2(self, secret):
        response = requests.put(
            f"http://{self.ip}:3000/api/client/secret?kube={self.id}",
            data=secret,
            headers={"Content-Type": "application/octet-stream", "User-Agent": rnd_useragent()}
        )

        return response.status_code == 200

    def retrieve_flag_2(self):
        response = requests.get(f"http://{self.ip}:3000/api/client/secret?kube={self.id}",
                                headers={"User-Agent": rnd_useragent()})
        #print(response.text)
        if response.status_code == 200:
            return response.text
        else:
            return None
