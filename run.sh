#!/bin/bash

trap "echo 'Stopping...'; kill 0" EXIT

echo "Starting backend..."
uvicorn app:app --reload &

echo "Starting frontend..."
streamlit run ui.py