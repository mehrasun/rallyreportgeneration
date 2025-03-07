import jenkins
import re
from datetime import datetime

# Connect to Jenkins
server = jenkins.Jenkins('http://10.22.226.66:32000')

# List of Jenkins jobs to track
jobs_name = [
    'DFW_3-Compute/DFW_3-Compute-BFV',
    'DFW_3-Compute/DFW_3-Compute-BFI',
    'SJC3-Compute/SJC3-Compute-BFV',
    'SJC3-Compute/SJC3-Compute-BFI'
]

def get_latest_build_on_date(job_name, selected_date):
    """Fetch the latest completed build for a job on a given date, skipping in-progress builds if needed."""
    try:
        job_info = server.get_job_info(job_name)
        completed_build_number = None

        builds_found = 0  # Counter to track the number of builds on the given date

        for build in job_info.get('builds', []):
            build_number = build['number']
            build_info = server.get_build_info(job_name, build_number)

            build_date = datetime.fromtimestamp(build_info['timestamp'] / 1000).strftime('%Y-%m-%d')

            if build_date == selected_date:
                builds_found += 1  # Increase the count of builds on this date

                # Skip if the build is still running
                if build_info['building']:
                    continue  # Check the next build

                # Store the latest completed build
                completed_build_number = build_number
                break  # Stop after finding the latest completed build

        # If only one build exists for the date and it's still running, return None (Not Found)
        if builds_found == 1 and completed_build_number is None:
            return None

        return completed_build_number

    except jenkins.NotFoundException:
        return None
    except Exception as e:
        print(f"Error fetching build for {job_name}: {e}")
        return None


def get_report_links(date):
    """Fetch report links, job status, and build number for the latest build of each job on a given date."""
    report_data = {}

    for job_name in jobs_name:
        latest_build_number = get_latest_build_on_date(job_name, date)

        if not latest_build_number:
            report_data[job_name] = {
                "status": "Not Found",
                "url": "Not Found",
                "build_number": "N/A",
                "build_url": "N/A"
            }
            continue

        try:
            build_info = server.get_build_info(job_name, latest_build_number)
            job_status = build_info["result"] if build_info["result"] else "IN PROGRESS"

            console_output = server.get_build_console_output(job_name, latest_build_number)
            pattern = r"(Flex-[A-Za-z0-9_]+-Generate-HTML-Report) #(\d+) started\."

            match = re.search(pattern, console_output)
            if match:
                HTML_job_name = match.group(1)
                HTML_build_number = match.group(2)

                # Fetch console output of the HTML report generation job
                html_console_output = server.get_build_console_output(HTML_job_name, int(HTML_build_number))
                html_pattern = r"Generated HTML Report - (http[^\s]+)"

                report_match = re.search(html_pattern, html_console_output)
                if report_match:
                    report_url = report_match.group(1)
                else:
                    report_url = "Not Found"
            else:
                report_url = "Not Found"

            job_view = "Flex-SJC3" if "SJC3-Compute" in job_name else "Flex-DFW_3"
            parent_job, actual_job = job_name.split("/")
            build_console_url = f"http://10.22.226.66:32000/view/{job_view}/job/{parent_job}/job/{actual_job}/{latest_build_number}/console"

            report_data[job_name] = {
                "status": job_status,
                "url": report_url,
                "build_number": latest_build_number,
                "build_console_url": build_console_url
            }

        except jenkins.NotFoundException:
            report_data[job_name] = {"status": "Not Found", "url": "Not Found", "build_number": "N/A"}
        except Exception as e:
            print(f"Error fetching report for {job_name}: {e}")
            report_data[job_name] = {"status": "Error", "url": "Not Found", "build_number": "N/A"}

    return report_data
