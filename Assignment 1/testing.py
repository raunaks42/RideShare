import pytest
import requests

API_ENDPOINT = "localhost:8000"

#Test API call 1 - Add unique user
#unique
#nonunique
#non sha pass
@pytest.mark.parametrize("username, password, status, resp_body",[("vishwas","2b76bc65a367ae587b4d60d0c8278403f4f61efa",201,{}),("vishwas","2b76bc65a367ae587b4d60d0c8278403f4f61efa",400,{}),("v1","hello",400,{}),("testing","2b76bc65a367ae587b4d60d0c8278403f4f61efa",201,{})])
def test_api_add_user_unique(username,password,status,resp_body):
        payload = {"username":username,"password":password}
        response = requests.put(API_ENDPOINT + "/api/v1/users",headers="Content-Type: application/json",data=payload)
        assert response.status_code == status
        assert response.json()['json'] == resp_body

#Test API call 2 - Remove user
#existing user
#non existing user
@pytest.mark.parametrize("username, status, resp_body",[("vishwas",200,{}),("thanos",400,{})])
def test_api_remove_user(username,status,resp_body):
        response = requests.delete(API_ENDPOINT + "/api/v1/users/"+username)
        assert response.status_code == status
        assert response.json()['json'] == resp_body

#Test API call 3 - Create a new ride
#existing user
#non existing user
@pytest.mark.parametrize("username,timestamp,source,dest,status,resp_body",[("testing","26-01-2020:00-53-09",22,23,201,{}),("nobody","26-01-2020:00-53-09",22,23,400,{})])
def test_api_new_ride(username,timestamp,source,dest,status,resp_body):
        payload = {"created_by":username,"timestamp":timestamp,"source":source,"destination":dest}
        response = requests.post(API_ENDPOINT + "/api/v1/rides/",data=payload,headers="Content-Type:application/json")
        assert response.status_code == status
        assert response.json()['json'] == resp_body


#Test API call 4 - List upcoming rides for source and dest
#existing source and dest
existing_src_existing_dst = [{"rideId":1234,"username":"username","timestamp":"timestamp"}]
#existing source and no dest
existing_src_no_dst = []
#no source and existing dest
no_src_existing_dst = []
#no source and no dest
no_src_no_dst = []
@pytest.mark.parametrize("source,dest,status,resp_body",[(22,23,201,existing_src_existing_dst),(22,1000,400,existing_src_no_dst),(1000,23,400,no_src_existing_dst),(1000,1000,400,no_src_no_dst)])
def test_api_get_rides(source,dest,status,resp_body):
        response = requests.get(API_ENDPOINT + "/api/v1/rides?source="+source+"&destination="+dest)
        assert response.status_code == status
        print(response)
        #assert response.json()['json'] == resp_body

#Test API call 5 - get ride details
#rideid exists
#output = {"rideId":1,"Created_by":"username","users":[{}],"Timestamp":"tstamp","source":"source","destination":"dest"}
#rideid doesn't exist
@pytest.mark.parametrize("rideid,status,resp_body",[(1,200,output),(2048,400,{})])
def test_api_get_rides(rideid,status,resp_body):
        response = requests.get(API_ENDPOINT + "/api/v1/rides/"+rideid)
        assert response.status_code == status
        print(response.json())
        #assert response.json()['json'] == resp_body

#Test API call 6 - join a ride
#existing user existent ride id
e_user_e_id = ("testing",1,200,{})
#existing user non existent ride id
e_user_n_id = ("testing",1000,400,{})
#non existing user and existing ride id
n_user_e_id = ("sfgsf",1,400,{})
#non existing user and non existing ride id
n_user_n_id = ("sfrgr",1000,400,{})
@pytest.mark.parametrize("username,rideid,status,resp_body",[e_user_e_id,e_user_n_id,n_user_e_id,n_user_n_id])
def test_api_new_ride(username,rideid,status,resp_body):
        payload = {"username":username}
        response = requests.post(API_ENDPOINT + "/api/v1/rides/"+rideid,data=payload,headers="Content-Type:application/json")
        assert response.status_code == status
        assert response.json()['json'] == resp_body


#Test API call 7 - Delete ride
#existing ride
#non existing ride
@pytest.mark.parametrize("rideid, status, resp_body",[(1,200,{}),(1254,405,{})])
def test_api_remove_user(rideid,status,resp_body):
        response = requests.delete(API_ENDPOINT + "/api/v1/rides/"+rideid)
        assert response.status_code == status
        assert response.json()['json'] == resp_body

