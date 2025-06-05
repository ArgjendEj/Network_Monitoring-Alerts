import pika
import json

def send_alarm_to_rabbitmq(message: dict):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='network_alerts')

        channel.basic_publish(
            exchange='',
            routing_key='network_alerts',
            body=json.dumps(message)
        )
        print("📤 Mesazhi u dërgua në RabbitMQ:", message)

        connection.close()
    except Exception as e:
        print("❌ Dështoi dërgimi i mesazhit në RabbitMQ:", e)

# ⚠️ Thirr funksionin me një mesazh testues
if __name__ == "__main__":
    alarm_message = {
        "type": "connection_lost",
        "host": "192.168.1.10",
        "port": 80,
        "status": "down"
    }
    send_alarm_to_rabbitmq(alarm_message)
