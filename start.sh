#!/bin/bash
while getopts "P:" flag
    do
             case "${flag}" in
                    P) PORT=${OPTARG};;
             esac
    done

if [ -z "$PORT" ]; then
	PORT="8000"
fi


gunicorn app.main:app --workers 3 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --keep-alive=0 --max-requests 1000