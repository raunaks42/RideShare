import pytest
import requests

API_ENDPOINT = "http://localhost:4000"

#Test API call 1 - Add new user
param_string_api1 = "payload, status, resp_body"
#new unique user 201
a = ({"username":"vishwas","password":"2b76bc65a367ae587b4d60d0c8278403f4f61efa"},201,{})
#nonunique 405
b = ({"username":"vishwas","password":"2b76bc65a367ae587b4d60d0c8278403f4f61efa"},405,{})
#new unique user 201
c = ({"username":"testing","password":"2b76bc65a367ae587b4d60d0c8278403f4f61efa"},201,{})
#non sha password
d = ({"username":"vishwas","password":"hello"},400,{})
@pytest.mark.parametrize(param_string_api1,[a,b,c,d])
def test_api_add_user_unique(payload,status,resp_body):
        response = requests.put(API_ENDPOINT + "/api/v1/users",data=payload)
        assert response.status_code == status
        print(str(response.status_code) + " " +str(response.json()))
        assert response.json() == resp_body

#Test API call 2 - Remove user
param_string_api2 = "payload, username, status, resp_body"
#existing user 200
a = ({},"vishwas",200,{})
#non existing user 405
b = ({},"thanos",405,{})
#non empty request body 400
c = ({"hello":1},"thanos",400,{})
@pytest.mark.parametrize(param_string_api2,[a,b,c])
def test_api_remove_user(payload, username,status,resp_body):
        response = requests.delete(API_ENDPOINT + "/api/v1/users/"+username,data=payload)
        assert response.status_code == status
        print(str(response.status_code) + " " +str(response.json()))
        assert response.json() == resp_body

#Test API call 3 - Create a new ride
param_string_api3 = "payload,status,resp_body"
#existing user 201
a = ({"created_by":"testing","timestamp":"26-01-2020:00-53-09","source":22,"destination":23},201,{})
#non existing user 405
b = ({"created_by":"nobody","timestamp":"26-01-2020:00-53-09","source":22,"destination":23},405,{})
#incorrect date format
c = ({"created_by":"nobody","timestamp":"2020-01-26:00-53-09","source":22,"destination":23},400,{})
#out of range src dst
d = ({"created_by":"testing","timestamp":"26-01-2020:00-53-09","source":890,"destination":7836},405,{})
#same src dst
e = ({"created_by":"testing","timestamp":"26-01-2020:00-53-09","source":22,"destination":22},405,{})
#missing fields
f = ({"created_by":"testing","source":22,"destination":23},400,{})
#empty body
g = ({},400,{})
#extra fields
h = ({"created_by":"testing","source":22,"destination":23,"random_field":69},400,{})
@pytest.mark.parametrize(param_string_api3,[a,b,c,d,e,f,g,h])
def test_api_new_ride(payload,status,resp_body):
        response = requests.post(API_ENDPOINT + "/api/v1/rides",data=payload)
        assert response.status_code == status
        assert response.json() == resp_body
        print(str(response.status_code) + " " +str(response.json()))


#Test API call 4 - List upcoming rides for source and dest
param_string_api4 = "payload,source,dest,status"
#atleast one ride existing 200
a = ({},22,23,200)
#no ride exists 204
b = ({},48,59,204)
#existing source and no dest 405
c = ({},22,1000,405)
#no source and existing dest 405
d = ({},1000,22,405)
#no source and no dest 405
e = ({},10000,1000,405)
#non empty request body ##invalid..get request
#f = ({"hi":"hello"},10000,1000,400)
@pytest.mark.parametrize(param_string_api4,[a,b,c,d,e])
def test_api_get_upcoming_rides(payload,source,dest,status):
        response = requests.get(API_ENDPOINT + "/api/v1/rides?source="+str(source)+"&destination="+str(dest))
        assert response.status_code == status
        print(str(response.status_code))
        

#Test API call 5 - get ride details
param_string_api5 = "payload,rideid,status,resp_body"
#rideid exists 200
a = ({},1,200,{})
#rideid doesn't exist 204
b = ({},1000,204,{})
#non empty body 400 invalid case get request
#c = ({"random":"hi"},1,400,{})
@pytest.mark.parametrize(param_string_api5,[a,b])
def test_api_get_ride_details(payload,rideid,status,resp_body):
        response = requests.get(API_ENDPOINT + "/api/v1/rides/"+str(rideid))
        assert response.status_code == status
        print(str(response.status_code))
        


#Test API call 6 - join a ride
param_string_api6 = "payload,rideid,status,resp_body"
#existing user existent ride id
a = ({"username":"testing"},1,200,{})
#existing user non existent ride id 204
b = ({"username":"testing"},5,204,{})
#non existing user and existing ride id 405
c = ({"username":"blehblehbleh"},1,405,{})
#non existing user and non existing ride id 405
d = ({"username":"blehblehbleh"},5,204,{})
#empty requestbody 400
e = ({},1,400,{})
#user already in ride 405
f = ({"username":"testing"},1,405,{})
@pytest.mark.parametrize(param_string_api6,[a,b,c,d,e,f])
def test_api_join_ride(payload,rideid,status,resp_body):
        response = requests.post(API_ENDPOINT + "/api/v1/rides/"+str(rideid),data=payload)
        assert response.status_code == status
        print(str(response.status_code) + " " +str(response.json()))
        assert response.json() == resp_body


#Test API call 7 - Delete ride
param_string_api7 = "payload,rideid, status, resp_body"
#existing ride 200
a = ({},1,200,{})
#non existing ride 405
b = ({},1254,405,{})
#request json is not empty 400
c = ({"random":"hi"},1,400,{})
@pytest.mark.parametrize(param_string_api7,[a,b,c])
def test_api_delete_ride(payload,rideid,status,resp_body):
        response = requests.delete(API_ENDPOINT + "/api/v1/rides/"+str(rideid))
        assert response.status_code == status
        assert response.json() == resp_body
        print(str(response.status_code) + " " +str(response.json()))
