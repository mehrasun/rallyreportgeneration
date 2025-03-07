from flask import Blueprint, render_template, request
from app.jenkins_service import get_report_links
from datetime import datetime

main = Blueprint("main", __name__)

@main.route("/", methods=["GET"])
def index():
    selected_date = request.args.get("date", datetime.today().strftime("%Y-%m-%d"))

    # Fetch reports for the latest build per job on the selected date
    report_data = get_report_links(selected_date)  # Use 'report_data' instead of 'reports'

    return render_template("index.html", report_data=report_data, selected_date=selected_date)  # Update context variable

@main.route("/aboutUs", methods=["GET"])
def about():
    return render_template("about.html")
