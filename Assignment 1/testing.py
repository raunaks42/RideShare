import pytest
import requests

API_ENDPOINT = "localhost:8000"

#Test API call 1 - Add new user
param_string_api1 = "payload, status, resp_body"
#new unique user 201
@pytest.mark.parametrize(param_string_api1,({"username":"vishwas","password":"2b76bc65a367ae587b4d60d0c8278403f4f61efa"},201,{}))
#nonunique 405
@pytest.mark.parametrize(param_string_api1,({"username":"vishwas","password":"2b76bc65a367ae587b4d60d0c8278403f4f61efa"},405,{}))
#new unique user 201
@pytest.mark.parametrize(param_string_api1,({"username":"testing","password":"2b76bc65a367ae587b4d60d0c8278403f4f61efa"},201,{}))
#non sha password
@pytest.mark.parametrize(param_string,({"username":"vishwas","password":"hello"},400,{}))
def test_api_add_user_unique(payload,status,resp_body):
        response = requests.put(API_ENDPOINT + "/api/v1/users",headers="Content-Type: application/json",data=payload)
        assert response.status_code == status
        assert response.json()['json'] == resp_body

#Test API call 2 - Remove user
param_string_api2 = "payload, username, status, resp_body"
#existing user 200
@pytest.mark.parametrize(param_string_api2,({},"vishwas",200,{}))
#non existing user 405
@pytest.mark.parametrize(param_string_api2,({},"thanos",405,{}))
#non empty request body 400
@pytest.mark.parametrize(param_string_api2,({"hello":1},"thanos",400,{}))
def test_api_remove_user(payload, username,status,resp_body):
        response = requests.delete(API_ENDPOINT + "/api/v1/users/"+username,data=payload)
        assert response.status_code == status
        assert response.json()['json'] == resp_body

#Test API call 3 - Create a new ride
param_string_api3 = "payload,username,timestamp,source,dest,status,resp_body"
#existing user 201
@pytest.mark.parametrize(param_string_api3,({"created_by":"testing","timestamp":"26-01-2020:00-53-09","source":22,"destination":23},201,{}))
#non existing user 405
@pytest.mark.parametrize(param_string_api3,({"created_by":"nobody","timestamp":"26-01-2020:00-53-09","source":22,"destination":23},405,{}))
#incorrect date format
@pytest.mark.parametrize(param_string_api3,({"created_by":"nobody","timestamp":"2020-01-26:00-53-09","source":22,"destination":23},400,{}))
#out of range src dst
@pytest.mark.parametrize(param_string_api3,({"created_by":"testing","timestamp":"26-01-2020:00-53-09","source":890,"destination":7836},405,{}))
#same src dst
@pytest.mark.parametrize(param_string_api3,({"created_by":"testing","timestamp":"26-01-2020:00-53-09","source":22,"destination":22},405,{}))
#missing fields
@pytest.mark.parametrize(param_string_api3,({"created_by":"testing","source":22,"destination":23},400,{}))
#empty body
@pytest.mark.parametrize(param_string_api3,({},400,{}))
#extra fields
@pytest.mark.parametrize(param_string_api3,({"created_by":"testing","source":22,"destination":23,"random_field":69},400,{}))
def test_api_new_ride(payload,status,resp_body):
        response = requests.post(API_ENDPOINT + "/api/v1/rides/",data=payload,headers="Content-Type:application/json")
        assert response.status_code == status
        assert response.json()['json'] == resp_body


#Test API call 4 - List upcoming rides for source and dest
param_string_api4 = "payload,source,dest,resp_body"
#atleast one ride existing 200
@pytest.mark.parametrize(param_string_api4,({},22,23,200))
#no ride exists 204
@pytest.mark.parametrize(param_string_api4,({},48,59,204))
#existing source and no dest 405
@pytest.mark.parametrize(param_string_api4,({},22,1000,405))
#no source and existing dest 405
@pytest.mark.parametrize(param_string_api4,({},1000,22,405))
#no source and no dest 405
@pytest.mark.parametrize(param_string_api4,({},10000,1000,405))
#non empty request body
@pytest.mark.parametrize(param_string_api4,({"hi":"hello"},10000,1000,400))
def test_api_get_rides(payload,source,dest,status):
        response = requests.get(API_ENDPOINT + "/api/v1/rides?source="+source+"&destination="+dest,payload=payload)
        assert response.status_code == status
        print(response.json())
        #assert response.json()['json'] == resp_body


#Test API call 5 - get ride details
param_string_api5 = "payload,rideid,status,resp_body"
#rideid exists 200
@pytest.mark.parametrize(param_string_api5,({},1,200,{})])
#rideid doesn't exist 204
@pytest.mark.parametrize(param_string_api5,({},1000,204,{}})])
#non empty body 400
@pytest.mark.parametrize(param_string_api5,({"random":"hi"},1,400,{}})])
def test_api_get_rides(payload,rideid,status,resp_body):
        response = requests.get(API_ENDPOINT + "/api/v1/rides/"+rideid,payload=payload)
        assert response.status_code == status
        print(response.json())
        #assert response.json()['json'] == resp_body


#Test API call 6 - join a ride
param_string_api6 = "payload,rideid,status,resp_body"
#existing user existent ride id
@pytest.mark.parametrize(param_string_api6,({"username":"testing"},1,200,{}))
#existing user non existent ride id 204
@pytest.mark.parametrize(param_string_api6,({"username":"testing"},1,204,{}))
#non existing user and existing ride id 405
@pytest.mark.parametrize(param_string_api6,({"username":"blehblehbleh"},1,405,{}))
#non existing user and non existing ride id 405
@pytest.mark.parametrize(param_string_api6,({"username":"blehblehbleh"},1,204,{}))
#empty requestbody 400
@pytest.mark.parametrize(param_string_api6,({},1,400,{}))
#user already in ride 405
@pytest.mark.parametrize(param_string_api6,({"username":"testing"},1,405,{}))
def test_api_new_ride(payload,rideid,status,resp_body):
        response = requests.post(API_ENDPOINT + "/api/v1/rides/"+rideid,data=payload,headers="Content-Type:application/json")
        assert response.status_code == status
        assert response.json()['json'] == resp_body


#Test API call 7 - Delete ride
param_string_api7 = "payload,rideid, status, resp_body"
#existing ride 200
@pytest.mark.parametrize(param_string_api7,({},1,200,{}))
#non existing ride 405
@pytest.mark.parametrize(param_string_api7,({},1254,405,{}))
#request json is not empty 400
@pytest.mark.parametrize(param_string_api7,({"random":"hi"},1,400,{}))
def test_api_remove_user(payload,rideid,status,resp_body):
        response = requests.delete(API_ENDPOINT + "/api/v1/rides/"+rideid,payload=payload)
        assert response.status_code == status
        assert response.json()['json'] == resp_body

