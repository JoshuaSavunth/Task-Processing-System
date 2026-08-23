import argparse
import json
import os
import sys
from typing import Any

import requests

API_URL = "http://localhost:8000"
TOKEN_FILE = os.path.expanduser("~/.dts_token")


# ==========================
# Token management
# ==========================

def save_token(token: str) -> None:
    with open(TOKEN_FILE, "w") as f:
        f.write(token)


def load_token() -> str | None:
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r") as f:
        return f.read().strip()


def auth_headers() -> dict[str, str]:
    token = load_token()
    if not token:
        print("You must login first.")
        sys.exit(1)
    return {"Authorization": f"Bearer {token}"}


# ==========================
# Auth commands
# ==========================

def register(username: str, password: str) -> None:
    resp = requests.post(
        f"{API_URL}/auth/register",
        params={"username": username, "password": password},
    )
    if resp.status_code != 200:
        print("Registration failed:", resp.text)
        return
    token = resp.json()["token"]
    save_token(token)
    print("Registered and logged in.")


def login(username: str, password: str) -> None:
    resp = requests.post(
        f"{API_URL}/auth/login",
        params={"username": username, "password": password},
    )
    if resp.status_code != 200:
        print("Login failed:", resp.text)
        return
    token = resp.json()["token"]
    save_token(token)
    print("Logged in.")


# ==========================
# Job commands
# ==========================

def submit_job(job_type: str, input_value: int) -> None:
    resp = requests.post(
        f"{API_URL}/jobs",
        json={"type": job_type, "input": input_value},
        headers=auth_headers(),
    )
    print(resp.json())


def list_jobs() -> None:
    resp = requests.get(f"{API_URL}/jobs", headers=auth_headers())
    print(json.dumps(resp.json(), indent=2))


def get_job(job_id: int) -> None:
    resp = requests.get(f"{API_URL}/jobs/{job_id}", headers=auth_headers())
    print(json.dumps(resp.json(), indent=2))


def get_result(job_id: int) -> None:
    resp = requests.get(f"{API_URL}/jobs/{job_id}/result", headers=auth_headers())
    print(json.dumps(resp.json(), indent=2))


def delete_job(job_id: int) -> None:
    resp = requests.delete(f"{API_URL}/jobs/{job_id}", headers=auth_headers())
    if resp.status_code == 204:
        print("Job deleted.")
    else:
        print("Delete failed:", resp.text)


def list_tasks() -> None:
    resp = requests.get(f"{API_URL}/tasks")
    print(json.dumps(resp.json(), indent=2))


# ==========================
# CLI parser
# ==========================

def main() -> None:
    parser = argparse.ArgumentParser(description="Distributed Task System CLI")

    sub = parser.add_subparsers(dest="command")

    # Auth
    reg = sub.add_parser("register")
    reg.add_argument("username")
    reg.add_argument("password")

    log = sub.add_parser("login")
    log.add_argument("username")
    log.add_argument("password")

    # Jobs
    submit = sub.add_parser("submit")
    submit.add_argument("type")
    submit.add_argument("input", type=int)

    sub.add_parser("jobs")
    job = sub.add_parser("job")
    job.add_argument("id", type=int)

    result = sub.add_parser("result")
    result.add_argument("id", type=int)

    delete = sub.add_parser("delete")
    delete.add_argument("id", type=int)

    sub.add_parser("tasks")

    args = parser.parse_args()

    if args.command == "register":
        register(args.username, args.password)
    elif args.command == "login":
        login(args.username, args.password)
    elif args.command == "submit":
        submit_job(args.type, args.input)
    elif args.command == "jobs":
        list_jobs()
    elif args.command == "job":
        get_job(args.id)
    elif args.command == "result":
        get_result(args.id)
    elif args.command == "delete":
        delete_job(args.id)
    elif args.command == "tasks":
        list_tasks()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
