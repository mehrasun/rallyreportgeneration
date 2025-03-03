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
    """Fetch the latest build for a specific job on a given date."""
    try:
        job_info = server.get_job_info(job_name)

        # Find the latest build on the given date
        latest_build_number = None

        for build in job_info.get('builds', []):
            build_number = build['number']
            build_info = server.get_build_info(job_name, build_number)

            build_date = datetime.fromtimestamp(build_info['timestamp'] / 1000).strftime('%Y-%m-%d')

            if build_date == selected_date:
                latest_build_number = build_number
                break  # Stop after finding the latest build on the date

        if not latest_build_number:
            return None  # No build found for the date

        return latest_build_number

    except jenkins.NotFoundException:
        return None
    except Exception as e:
        print(f"Error fetching build for {job_name}: {e}")
        return None


def get_report_links(date):
    """Fetch report links for the latest build of each job on a given date."""
    report_links = {}

    for job_name in jobs_name:
        latest_build_number = get_latest_build_on_date(job_name, date)

        if not latest_build_number:
            report_links[job_name] = "Not Found"
            continue

        try:
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
                    report_links[job_name] = report_match.group(1)
                else:
                    report_links[job_name] = "Not Found"
            else:
                report_links[job_name] = "Not Found"

        except jenkins.NotFoundException:
            report_links[job_name] = "Not Found"
        except Exception as e:
            print(f"Error fetching report for {job_name}: {e}")
            report_links[job_name] = "Not Found"

    return report_links
