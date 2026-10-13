from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Logics.report_factory import report_factory
import flask
import connexion


api = connexion.FlaskApp(__name__, specification_dir="./")

@api.route("/api/get_report", methods=["GET"])
def get_report():
    return "success"

if __name__ == "__main__":
    api.run(host = "0.0.0.0", port = 8080)
