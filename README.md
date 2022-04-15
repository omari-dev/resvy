# Resvy

Reservation system that solves restaurant reservation problem

1. [Prerequisites](#Prerequisites)
2. [Running Resvy locally](#Resvy-locally)
3. [Running Resvy Tests](#Resvy-tests)
4. [Postman Collection](#postman-collection)
5. [System admins](#system-admins)

---

## Prerequisites <a name="Prerequisites"></a>

* Docker
* Docker-compose

---

## Running Resvy Locally <a name="resvy-locally"></a>

Simply by running this command ``make run-server`` and the web application will be available on http://127.0.0.1:8000

---

## Running Resvy Tests <a name="resvy-tests"></a>

Simply by running this command ``make test``

---

## Postman collection <a name="postman-collection"></a>

You can find Postman collection [here](schema.yaml) import it into your postman app and have fun

---

## System admins <a name="#system-admins"></a>

The system has a default demo admin and you can obtain token by using employee number: `0001` with password `A1230838a`,
also 

you can create new admin by using django management command: `./manage.py add-admin` use `--help` for more insight 

---
