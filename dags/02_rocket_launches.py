import json
import pathlib
import airflow
import requests
import requests.exceptions as requests_exceptions
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


"""
dag_id = The name of the DAG
start_date = The date the DAG should start running
schedule_interval = How often the DAG should run. @daily means it will run once a day

"""

dag = DAG(
    dag_id="download_rocket_launches",
    start_date=airflow.utils.dates.days_ago(14),
    schedule_interval=None,
)

"""
Apply Bash to download the URL response with curl
"""
download_launches = BashOperator(
    task_id="download_launches",
    bash_command="curl -o /tmp/launches.json -L 'https://ll.thespacedevs.com/2.0.0/launch/upcoming'",
    dag=dag,
)

def _get_pictures():
 
 # Ensure directory exists
 pathlib.Path("/tmp/images").mkdir(parents=True, exist_ok=True)

 # Download all pictures in launches.json
 with open("/tmp/launches.json") as f:
    # Load the JSON data
    launches = json.load(f)
    # Get the image URLs for all launches
    image_urls = [launch["image"] for launch in launches["results"]]

    # Download all images
    for image_url in image_urls:

        try:
            # Download the image
            response = requests.get(image_url)
            image_filename = image_url.split("/")[-1]
            # Set the target file path
            target_file = f"/tmp/images/{image_filename}"

            with open(target_file, "wb") as f:
                f.write(response.content)

            print(f"Downloaded {image_url} to {target_file}")

        except requests_exceptions.MissingSchema:
            print(f"{image_url} appears to be an invalid URL.")

        except requests_exceptions.ConnectionError:
            print(f"Could not connect to {image_url}.")


# Python operator
get_pictures = PythonOperator(
    task_id="get_pictures",
    python_callable=_get_pictures,
    dag=dag,
)

# Notify task
notify = BashOperator(
    task_id="notify",
    bash_command='echo "There are now $(ls /tmp/images/ | wc -l) images."',
    dag=dag,
)

# Set the order of tasks in the DAG
download_launches >> get_pictures >> notify