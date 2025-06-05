import pika

def callback(ch, method, properties, body):
    print(f"[🔔] Alarmi i pranuar: {body.decode()}")

def start_consumer():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='network_alerts', durable=True)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='network_alerts', on_message_callback=callback, auto_ack=True)

        print("[*] Duke pritur alarme... (CTRL+C për ndalje)")
        channel.start_consuming()

    except pika.exceptions.AMQPConnectionError:
        print("❌ Nuk u lidh me RabbitMQ. Sigurohu që është aktiv.")

if __name__ == "__main__":
    start_consumer()
