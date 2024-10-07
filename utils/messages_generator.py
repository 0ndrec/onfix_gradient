
import base64
import json
import time

class MQTTMessageGenerator:

    def __init__(self, client_id, username, password):
        self.client_id = client_id
        self.username = username
        self.password = password

    @staticmethod
    def _replace_in_bytes(message, old_value, new_value):
        return message.replace(old_value.encode(), new_value.encode())

    @staticmethod
    def decode_message(encoded_message):
        return base64.b64decode(encoded_message)

    def generate_task_message(self) -> bytes:
        original_data = 'giKXVgAAHGNsaWVudC90YXNrL1laNUdYMDY2VFZPVjQzUUIAoiGXVwAAHGNsaWVudC90YXNrL1laNUdYMDY2VFZPVjQzUUKCIpdYAAAcY2xpZW50L3Rhc2svWVo1R1gwNjZUVk9WNDNRQgA='
        message = bytearray(base64.b64decode(original_data))
        message = self._replace_in_bytes(message, 'YZ5GX066TVOV43QB', self.client_id)
        return message

    def generate_login_message(self) -> bytes:
        message_template = b"\x10\x82\x01\x00\x04MQTT\x05\xc2\x00<\x05'\x00\x10\x00\x00\x00\x10" + self.client_id.encode('utf-8') + b'\x00\x1c' + self.username.encode('utf-8') + b'\x00@' + self.password.encode('utf-8')
        return message_template

    def generate_ping_message(self) -> bytes:
        original_data = 'MpUBAB5jbGllbnQvb25saW5lL1laNUdYMDY2VFZPVjQzUUKXWQB7InR5cGUiOiJvbmxpbmUiLCJjbGllbnRpZCI6IllaNUdYMDY2VFZPVjQzUUIiLCJhY2NvdW50IjoiS2ROQzNPVzdOdWFvNG1LSVliQWpkNGFRNFprMSIsInRpbWVzdGFtcCI6MTcyNjc0NzQ2MTA5M30='
        message = bytearray(base64.b64decode(original_data))
        message = self._replace_in_bytes(message, 'YZ5GX066TVOV43QB', self.client_id)
        message = self._replace_in_bytes(message, 'KdNC3OW7Nuao4mKIYbAjd4aQ4Zk1', self.username)
        message = self._replace_in_bytes(message, '172674746s1093', str(int(time.time()) * 1000))
        return message

    @staticmethod
    def generate_clear_message() -> bytes:
        return base64.b64decode('wAA=')

    def analyze_differences(self, generated, original):
        gen = self.decode_message(generated)
        orig = self.decode_message(original)
        differences = []
        for i, (g, o) in enumerate(zip(gen, orig)):
            if g != o:
                differences.append(f'Position {i}: Generated {g:02x}, Original {o:02x}')
        return differences