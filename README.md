# Task-Processing-System

A Python project that implements a simple distributed job processing system. Jobs are submitted through a FastAPI server, stored in a SQL database, and processed by one or more worker processes.

The project was built to explore how multiple workers can safely share a job queue and how a system can handle failed or interrupted jobs.

## Features

* REST API to submit jobs and check status
* SQL database as the job queue
* Multiple workers run in parallel
* Atomic job claiming - no duplicate processing
* Job status and result tracking
* Worker heartbeats for failure detection
* Retry logic for failed or stalled jobs
* Command-line client included
* Unit and integration tests

## How It Works

```text
Client
   |
   | Submit job
   v
FastAPI Server
   |
   | Store job
   v
SQL Database
   |
   +--------+--------+
   |                 |
   v                 v
Worker 1          Worker 2
   |                 |
   +--------+--------+
            |
            v
       Execute Task
            |
            v
      Update Job
```

A typical job starts as "pending". A worker claims the job and changes it to "running" before executing it. Once finished, the worker stores the result and marks the job as "completed" or "failed".

If a worker stops responding, its heartbeat can become stale and the job can be made available for another attempt.

## Project Structure

```text
distributed-task-system/
├── api/
├── client/
├── tasks/
├── tests/
├── worker/
├── requirements.txt
└── README.md
```

## How to Run

### Setup

Install the required packages:

```bash
pip install -r requirements.txt
```

Apply the database schema:

```bash
psql -U postgres -d distributed_tasks -f sql/schema.sql
```

> **Note:** When prompted for the PostgreSQL password, enter: postgres.

### Terminal 1 — Start the API

Start the FastAPI server and keep this terminal running:

```bash
uvicorn app.main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

### Terminal 2 — Start a Worker

Open a second terminal, start the worker, and keep this terminal running:

```bash
python worker.py
```

### Terminal 3 — Run Client Commands

Open a third terminal to interact with the system.

#### Register a User

```bash
python client.py register <username> <password>
```

#### Submit a Job

Submit a Fibonacci job:

```bash
python client.py submit fibonacci 10
```

Example response:

```text
Job submitted successfully.
Job ID: 1
```

#### Check Results

```bash
python client.py result 1
```

Example response:

```text
Job ID: 1
Status: completed
Result: 55
```

#### List All Jobs

```bash
python client.py jobs
```

#### Delete a Job

```bash
python client.py delete <job_id>
```

**Optional:** Run additional workers in separate terminals for parallel processing.

**Tip:** The API and worker terminals need to stay running while you use the client, so use an additional terminal tab for client commands.


## Job Queue

Each job contains information such as:

* Job ID
* Task name
* Task input
* Current status
* Result
* Number of attempts
* Assigned worker
* Last heartbeat
* Creation/update timestamps

The main job states are:

```text
pending → running → completed
              |
              └────→ failed → retry → pending
```

Jobs are claimed atomically so that two workers do not normally pick up the same job.

## Fault Handling

Workers send periodic heartbeats while processing jobs. This gives the system a way to detect workers that have stopped responding.

For example:

```text
Worker claims job
       |
       v
  Running task
       |
    heartbeat
       |
       X  Worker stops
       |
       v
 Stale heartbeat
       |
       v
   Job retried
```

Failed jobs can also be retried depending on the configured retry limit.

## Tasks

The project currently includes different example tasks such as:

* **Prime factorization** - finds the prime factors of a number
* **Fibonacci** - calculates a Fibonacci value
* **Sleep/delay** - waits for a specified amount of time

The delay task is useful when testing multiple workers and the heartbeat/retry system.

New tasks can be added as Python functions and registered with the task system.

## Testing

Unit tests are used to check individual task functions:

```bash
pytest tests/test_tasks.py
```

The integration tests can be used to run jobs through the full system and test multiple workers, job claiming, and retry behavior.

Run all tests with:

```bash
pytest
```

## Limitations

Limitations include:
- SQL is used as the job queue
- Retry handling is basic
- Logging/monitoring is minimal
- No authentication or web dashboard
- Not tested at large scale

## Possible Improvements

Some areas I would like to explore further include:

* Adding task priorities and cancellation
* Adding better logging and monitoring
* Adding a simple web dashboard

## Technologies

* Python
* FastAPI
* SQL
* Pytest
* REST APIs
