from flask import Blueprint, render_template, request, jsonify, send_file
from .database import save_client_info, get_client_data, add_trip_data, export_trip_data, export_client_data
from .utils import suggest_id, suggest_trip
from .tasks import upload_to_blob, clean_old_files

routes = Blueprint('routes', __name__)

@routes.route("/test.html")
def test():
    return render_template("backstage/test.html")

@routes.route("/trip.html")
def trip():
    return render_template("backstage/trip.html")

@routes.route("/admin.html")
def admin():
    return render_template("backstage/admin.html")

@routes.route("/")
def root():
    return render_template("backstage/admin.html")

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


@routes.route("/upload", methods=["GET"])
def upload_now():
    """手動觸發上傳"""
    upload_to_blob()
    return jsonify({"message": "File uploaded manually."})

@routes.route("/clean", methods=["GET"])
def clean_now():
    """手動觸發清理"""
    clean_old_files()
    return jsonify({"message": "Old files cleaned manually."})