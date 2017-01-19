# ecg-fault-location-backend
A python flask-based backend api for a fault location app for ecg.

## Documentation

* ### Endpoints
 The following endpoint/urls are exposed by the api:
 
  #### POLES

  > __`/poles`__
 
  >> GET all poles
 
  >> POST new pole
 
  > __`/poles/<int:pole_id>`__
 
  >> GET the pole with id 'pole_id'
 
  >> UPDATE the pole with id 'pole_id'
 
  >> DELETE the pole with id 'pole_id'

## How to contribute
* **Clone project**

```
 git clone
```

* **Install project requirements**

```
 pip install -r requirements.txt
```
 
* **Run the app locally**

```
 set FLASK_APP=app.py

 flask run
```

## Tests

 ```
  python test.py
 ```

## TODO
 
 * Add authentication for the api
