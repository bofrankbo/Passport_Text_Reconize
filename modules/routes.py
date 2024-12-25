from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from .database import save_client_info, get_client_data, add_trip_data, export_trip_data, export_client_data, import_client_data, import_trip_data
from .utils import suggest_id, suggest_trip
from .tasks import upload_to_blob, clean_old_files, get_next_backup_time, get_blob_list
from .ocr import ocr_passport
from flask_httpauth import HTTPBasicAuth

routes = Blueprint('routes', __name__)
auth = HTTPBasicAuth()

users = {
    "admin": "900824"
}


@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None


@routes.route("/")
def root():
    return render_template("website/passport.html")


@routes.route("/passport.html")
def passport():
    return render_template("website/passport.html")


@routes.route("/backstage/admin.html")
@auth.login_required
def admin():
    return render_template("backstage/admin.html")


@routes.route("/backstage/client.html")
@auth.login_required
def client():
    return render_template("backstage/client.html")


@routes.route("/backstage/trip.html")
@auth.login_required
def trip():
    return render_template("backstage/trip.html")


@routes.route("/backstage/backup.html")
@auth.login_required
def backup():
    next_backup_time = get_next_backup_time()
    blob_list = get_blob_list()
    return render_template("backstage/backup.html", next_backup_time=next_backup_time, blob_list=blob_list)


@routes.route("/test.html")
def test():
    return render_template("backstage/test.html")


@routes.route("/suggest_id", methods=["GET"])
def suggest_id_route():
    return suggest_id(request)


@routes.route("/suggest_trip", methods=["GET"])
def suggest_trip_route():
    return suggest_trip(request)


@routes.route("/submit_passport", methods=["POST"])
def submit_passport():
    return save_client_info(request)


@routes.route("/get_client", methods=["GET"])
def get_client():
    return get_client_data(request)


@routes.route("/add_trip", methods=["POST"])
def add_trip():
    return add_trip_data(request)


@routes.route("/export_trip/<trip_name>", methods=["GET"])
def export_trip(trip_name):
    return export_trip_data(trip_name)


@routes.route("/export_csv", methods=["GET"])
def export_csv():
    return export_client_data()


@routes.route("/import_csv", methods=["GET", "POST"])
def import_csv():
    return import_client_data(request)


@routes.route("/upload", methods=["POST"])
def upload_now():
    """手動觸發上傳"""
    upload_to_blob()
    return jsonify({"message": "File uploaded manually."})


@routes.route("/clean", methods=["POST"])
def clean_now():
    """手動觸發清理"""
    clean_old_files()
    return jsonify({"message": "Old files cleaned manually."})


@routes.route("/process_passport", methods=["POST"])
def process_passport():
    return ocr_passport(request)
