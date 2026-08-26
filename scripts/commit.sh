#!/bin/bash

cd ~/Projects/teapot-lang || exit 1

echo "Running CI tests..."

read -rp "WARNING: Will remove the directory build/. Only continue if the folder is disposable. Continue? (y/n) " warn

if [[ "$warn" =~ ^[Yy]$ ]]; then
    rm -rf ../build/
else
    echo "Aborted."
    exit 1
fi

rm -rf build/

if ! ruff check . ||
   ! ruff format --check . ||
   ! mypy src/teapot ||
   ! python -m pytest ||
   ! python -m build ||
   ! pip-audit .; then

    echo
    echo "WARNING: Some CI tests failed."
    read -rp "Some CI tests failed. Continue? [y/N]: " continue_commit

    if [[ ! "$continue_commit" =~ ^[Yy]$ ]]; then
        echo "Aborting."
        exit 1
    fi
fi

echo "CI tests completed."

git add .

read -rp "Commit name: " commit_name

if [ -z "$commit_name" ]; then
    echo "Commit name cannot be empty."
    exit 1
fi

git commit -m "$commit_name"

read -rp "Push to remote? [y/N]: " push

if [[ "$push" =~ ^[Yy]$ ]]; then
    git push
fi