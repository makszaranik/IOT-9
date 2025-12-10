from counterfit_connection import CounterFitConnection
import time
from counterfit_shims_grove.adc import ADC
from counterfit_shims_grove.grove_relay import GroveRelay
import json
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse, X509

host_name = "soil-moisture-sensor-max11189.azure-devices.net"
x509 = X509("./soil-moisture-sensor-x509-cert.pem", "./soil-moisture-sensor-x509-key.pem")
device_id = "soil-moisture-sensor-x509"

device_client = IoTHubDeviceClient.create_from_x509_certificate(x509, host_name, device_id)
print('Connecting')
device_client.connect()
print('Connected')


CounterFitConnection.init('127.0.0.1', 5001)
adc = ADC()
relay = GroveRelay(66)


def handle_command(client, userdata, message):
    payload = json.loads(message.payload.decode())
    print("Command received:", payload)

    if payload.get('relay_on'):
        print("Turning relay ON")
        relay.on()
    else:
        print("Turning relay OFF")
        relay.off()

def handle_method_request(request):
    print("Direct method received - ", request.name)
    if request.name == "relay_on":
        print("-> Turning relay ON")
        relay.on()
    elif request.name == "relay_off":
        print("-> Turning relay OFF")
        relay.off()

    method_response = MethodResponse.create_from_method_request(request, 200)
    device_client.send_method_response(method_response)

device_client.on_method_request_received = handle_method_request 

while True:
    soil_moisture = adc.read(65)
    print("Soil moisture:", soil_moisture)
    telemetry = json.dumps({'soil_moisture': soil_moisture})
    print("Sending telemetry:", telemetry)
    message = Message(json.dumps({ 'soil_moisture': soil_moisture }))
    device_client.send_message(message)
    time.sleep(10)