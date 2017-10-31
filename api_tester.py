import httplib2
import json
import sys

print("Running Endpoint Tester....\n")
address = 'http://localhost:5000'


# # Making a POST Request
print("Making a Meal POST request to /activities...")
try:
    url = address + "/activities?type=meal&user_id=1&description=Snickers&duration=0:30&healthy=False&unhealthy=True&starch_rich=False&sucrose_rich=True"
    activity_type = 'meal'
    user_id = 1
    h = httplib2.Http()
    resp, result = h.request(url, 'POST')
    obj = json.loads(result)
    activityID = obj['Meal']['id']
    if resp['status'] != '200':
        raise Exception(
            'Received an unsuccessful status code of %s' % resp['status'])
except Exception as err:
    print("Test 1 FAILED: Could not make POST Request to web server")
    print(err.args)
    sys.exit()
else:
    print("Test 1 PASS: Succesfully Made POST Request to /activities")


# # Making a GET Request
print("Making a GET Request for /activities...")
try:
    url = address + "/activities?user_id=1"
    h = httplib2.Http()
    resp, result = h.request(url, 'GET')
    if resp['status'] != '200':
        raise Exception(
            'Received an unsuccessful status code of %s' % resp['status'])
except Exception as err:
    print("Test 2 FAILED: Could not make GET Request to web server")
    print(err.args)
    sys.exit()
else:
    print("Test 2 PASS: Succesfully Made GET Request to /activities")


# # Making GET Requests to  /activities/user_id/activity_type/activity_id/
print("Making GET requests to /activities/user_id/activity_type/activity_id/ ")

try:
    userID = user_id
    activityTYPE = activity_type
    activityID = activityID
    url = address + \
        "/activities/%s/%s/%s" % (userID, activityTYPE, activityID)
    h = httplib2.Http()
    resp, result = h.request(url, 'GET')
    if resp['status'] != '200':
        raise Exception(
            'Received an unsuccessful status code of %s' % resp['status'])
except Exception as err:
    print("Test 3 FAILED: Could not make GET Requests to web server")
    print(err.args)
    sys.exit()
else:
    print("Test 3 PASS: Succesfully Made GET Request to \
        /activities/user_id/activity_type/activity_id")


# # Making a PUT Request
print("Making a Meal description PUT request to \
    /activities/user_id/activity_type/activity_id/ ")

try:
    userID = user_id
    activityTYPE = activity_type
    activityID = activityID
    url = address + \
        "/activities/%s/%s/%s?healthy=True&description=Slimy+soup" % (
            userID, activityTYPE, activityID)
    h = httplib2.Http()
    resp, result = h.request(url, 'PUT')
    if resp['status'] != '200':
        raise Exception(
            'Received an unsuccessful status code of %s' % resp['status'])

except Exception as err:
    print("Test 4 FAILED: Could not make PUT Request to web server")
    print(err.args)
    sys.exit()
else:
    print("Test 4 PASS: Succesfully Made PUT Request to \
        /activities/user_id/activity_type/activity_id/")


# # Making a DELETE Request
print("Making DELETE requests to \
    /activities/user_id/activity_type/activity_id ... ")

try:
    userID = userID
    activityTYPE = activityTYPE
    activityID = activityID
    url = address + "/activities/%s/%s/%s" % (userID, activityTYPE, activityID)
    h = httplib2.Http()
    resp, result = h.request(url, 'DELETE')
    if resp['status'] != '200':
        raise Exception(
            'Received an unsuccessful status code of %s' % resp['status'])


except Exception as err:
    print("Test 5 FAILED: Could not make DELETE Requests to web server")
    print(err.args)
    sys.exit()
else:
    print("Test 5 PASS: Succesfully Made DELETE Request to \
        /activities/user_id/activity_type/activity_id")
    print("ALL TESTS PASSED!!")
