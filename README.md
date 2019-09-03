# canvas-downloader
Python script to download modules from your canvas course while preserving module organization

## Requirements
- lxml
- requests

## To run
First clone the github repository. Then, install required packages using:
`pip3 install -r requirements.txt`

Then run using:
`python3 canvas-downloader.py -u USERNAME -c COURSE_URL`

For additional help, run:
`python3 canvas-downloader.py --help`

## If using for multiple courses...
Remember to delete the modules folder if downloading different course
