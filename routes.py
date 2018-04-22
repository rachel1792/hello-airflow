from app import app
from flask import render_template, request
from rq import Queue
from rq.job import Job
from worker import conn

from xword.lib.xword_etl import extract

q = Queue(connection=conn)


@app.route('/', methods=['GET'])
def index():
    results = {}
    if request.method == "GET":
        job = q.enqueue_call(
            func=extract, result_ttl=5000
        )
        print(job.get_id())

    return render_template('index.html', results=results)


@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):

    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        return str(job.result), 200
    else:
        return "Nay!", 202