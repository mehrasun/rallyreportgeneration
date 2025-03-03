from flask import Blueprint, render_template, request
from app.jenkins_service import get_report_links
from datetime import datetime

main = Blueprint("main", __name__)

@main.route("/", methods=["GET"])
def index():
    selected_date = request.args.get("date", datetime.today().strftime("%Y-%m-%d"))

    # Fetch reports for the latest build per job on the selected date
    reports = get_report_links(selected_date)

    return render_template("index.html", reports=reports, selected_date=selected_date)

@main.route("/aboutUs", methods=["GET"])
def about():
    return render_template("about.html")


