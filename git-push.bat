@echo off
set /p commit_message="Enter commit message: "
git add .
git commit -m "%commit_message%"
git push origin main
