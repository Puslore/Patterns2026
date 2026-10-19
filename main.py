from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Logics.report_factory import report_factory
import connexion
from Src.Logics.settings_manager import settings_manager
from flask import request

# Необходимо установить pip install flask connexion
# pip install "connexion[flask]"
# pip install "connexion[uvicorn]"

api = connexion.FlaskApp(__name__, specification_dir="./")
settings_manager = settings_manager()
settings_manager.load()

storage_manager = storage_manager(settings_manager.settings)
storage_manager.build()

"""
Получить отчет в формате по умолчанию
"""
@api.route("/api/get_default_report", methods=["GET"])
def get_default_report():
    try:
        key = request.args.get('entity') 
        unique_code = request.args.get('unique_code')

        items = storage_manager.data[ key ]
        item = next((obj for obj in items if hasattr(obj, 'unique_code') and obj.unique_code == unique_code), None)

        factory = report_factory(settings_manager.settings)
        report_type = factory.create_default()
        result = report_type().build( item )
        
        return result.text, 200, {'Content-Type': result.format}
    except Exception as ex:
        return  f"Ошибка: {ex}!", 500

"""
Получить список доменных сущностей
"""
@api.route("/api/get_entities", methods=["GET"])
def get_entities():
    keys = storage_manager.domains().keys() 
    result = ",".join(keys) 
    return result, 200, {'Content-Type': 'text/plain'}
    

if __name__ == "__main__":
    api.run(host = "0.0.0.0", port = 8080)
