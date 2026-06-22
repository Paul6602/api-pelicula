import boto3
import uuid
import os
import json

def lambda_handler(event, context):
    try:
        # 1. Extraemos el body del evento. Si no hay body, usamos un diccionario vacío.
        body = event.get('body', {})
        
        # 2. LOG DE ENTRADA (INFO): Registramos solo los datos relevantes que ingresan.
        log_entrada = {
            "tipo": "INFO",
            "log_datos": {
                "mensaje": "Iniciando creación de película",
                "datos_recibidos": body
            }
        }
        print(json.dumps(log_entrada))

        # Extracción de variables de negocio.
        tenant_id = body['tenant_id']
        pelicula_datos = body['pelicula_datos']
        nombre_tabla = os.environ["TABLE_NAME"]
        
        # Proceso de negocio
        uuidv4 = str(uuid.uuid4())
        pelicula = {
            'tenant_id': tenant_id,
            'uuid': uuidv4,
            'pelicula_datos': pelicula_datos
        }
        
        # Conexión e inserción en la base de datos DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(nombre_tabla)
        response = table.put_item(Item=pelicula)
        
        # 3. LOG DE SALIDA (INFO): Éxito total.
        log_salida = {
            "tipo": "INFO",
            "log_datos": {
                "mensaje": "Película insertada exitosamente en DynamoDB",
                "pelicula_creada": pelicula
            }
        }
        print(json.dumps(log_salida))
        
        # RETORNO EXITOSO (HTTP 200 OK)
        return {
            'statusCode': 200,
            'pelicula': pelicula,
            'response': response
        }
        
    except KeyError as e:
        # 4. LOG ERROR CONTROLADO (HTTP 400 Bad Request): Error de tipeo o llave faltante.
        log_error = {
            "tipo": "ERROR",
            "log_datos": {
                "mensaje": "Error de validación: Faltan atributos requeridos en el JSON",
                "atributo_faltante": str(e)
            }
        }
        print(json.dumps(log_error))
        
        # RETORNO ERROR DE CLIENTE
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': f"Falta el atributo requerido: {str(e)}"
            })
        }
        
    except Exception as e:
        # 5. LOG ERROR GENERAL (HTTP 500 Internal Server Error): Caídas de red o de AWS.
        log_error = {
            "tipo": "ERROR",
            "log_datos": {
                "mensaje": "Ocurrió un error interno en el servidor",
                "detalle_error": str(e)
            }
        }
        print(json.dumps(log_error))
        
        # RETORNO ERROR DE SERVIDOR
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': "No se pudo procesar la solicitud debido a un fallo interno."
            })
        }
