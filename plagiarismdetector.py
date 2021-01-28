import sys, requests, time, re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

originalID = ""
originalCode = ""
csv = [];

# Check if a project ID is provided
if len(sys.argv) == 2 and sys.argv[1].isdigit():
    originalID = sys.argv[1]
else:
    print("Please provide a correct project ID (e.g 1234567890123456)")
    sys.exit(1)

# Fetch the main project
response = requests.get("https://www.khanacademy.org/api/labs/scratchpads/" + originalID)

# Check if it is JSON
try:
    originalCode = response.json()["revision"]["code"]
except:
    print("Project does not exist")
    sys.exit(1)

# Fetch the list
projectListLink = requests.get("https://www.khanacademy.org/api/internal/scratchpads/Project:x13566a1395f56078/top-forks?subject=all&sort=2&page=0&limit=100")
projectList = projectListLink.json()

outputHTML = ""

# Loop through the projects
for projectIndex in range(len(projectList["scratchpads"])):
    url = projectList["scratchpads"][projectIndex]["url"]
    id = url.split("/")[-1]

    print("Checking against project " + id)

    # Get the projects data
    project = requests.get("https://www.khanacademy.org/api/labs/scratchpads/" + id)
    projectCode = project.json()["revision"]["code"]

    # Compare the code
    a = fuzz.ratio(originalCode, projectCode)
    b = fuzz.partial_ratio(originalCode, projectCode)
    c = fuzz.token_sort_ratio(originalCode, projectCode)
    d = fuzz.partial_token_sort_ratio(originalCode, projectCode)
    e = fuzz.QRatio(originalCode, projectCode)

    data = [a, b, c, d, e]

    # Process the data and output it
    outputHTML = outputHTML + "<tr><td><a href=\"" + url + "\" target=\"_blank\"><p>" + id + "</p></a></td>"
    for value in data:
        color = ""
        if value < 58:
            color = "#7ffe00"
        elif value >= 58 and value < 75:
            color = "#ffff00"
        elif value >= 75 and value < 87:
            color = "#fe7f00"
        elif value >= 87:
            color = "#fe007f"
        outputHTML = outputHTML + "<td style='background-color:" + color + "'>" + str(value) + "</td>"
    outputHTML = outputHTML + "</tr>"

    if projectIndex % 10 == 0:
        with open("output.js", 'w') as output:
            print("Exported data")
            output.write("data = `" + outputHTML + "`; document.getElementById(\"table\").innerHTML = data")

    time.sleep(0.5)
