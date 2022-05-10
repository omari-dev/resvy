![Build](https://github.com/omari-dev/resvy/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/omari-dev/resvy/branch/main/graph/badge.svg?token=40D1HAOGWS)](https://codecov.io/gh/omari-dev/resvy)

# Resvy

1. [About](#about)
2. [Features](#features)
3. [Solution](#solution)
4. [Technology Stack](#technology_stack)
5. [Running Resvy locally](#Resvy-locally)
6. [Running Resvy Tests](#Resvy-tests)
7. [Postman Collection](#postman-collection)
8. [System admins](#system-admins)
9. [Development](#development)

---

## About <a name="about"></a>

Reservation System that solve restaurant reservation problem and manging them by finding the available time slots and
which table is available table for the group of customers

---

## Features <a name="features"></a>

* Table management
* Reservation management
* List reservation
* Role based actions

---

## Solution <a name="solution"></a>

Existing reservation:

![Card One](https://user-images.githubusercontent.com/17138533/163597324-0d795e03-f55e-40ee-827c-02832f4d10cb.png)

The provided solutions in this system is to get all the time slot between these reservations as it's shown in below card

![Card Two](https://user-images.githubusercontent.com/17138533/163597501-0d2a7116-5778-4da3-8f16-3a56d26daf68.png)



---

## Technology Stack <a name="technology_stack"></a>

* [Python 3.10.x](https://www.python.org/)
* [Django Web Framework 4.0.x](https://www.djangoproject.com/)
* [Postgresql 13](https://www.postgresql.org/)
* [Redis](https://pypi.org/project/django-redis/)

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

The system has a default demo admin and you can obtain token by using employee number: `0001` with password `A1230838a`

you can create new admin by using django management command: `./manage.py add-admin` use `--help` for more insight

---

## Development <a name="#development"></a>

1. Clone this project using

````
$ git clone https://github.com/omari-dev/resvy.git
````

2. setup postgre: for Postgresql you will need to download and install it.
    - Download Postgresql from [this Link](https://www.postgresql.org/download/)
    - After installation, create Database in postgresql shell using these commands
        1. `CREATE DATABASE resvy_db;`
        2. `CREATE USER resvy WITH PASSWORD 'resvy';`
        3. `GRANT ALL PRIVILEGES ON DATABASE resvy_db TO resvy;`

3. run ``$ make install`` to set up the virtual environment and install the dependencies
4. run `$ ./manage.py migrate`
5. Finally, you need to run development server by ``$ ./manage.py runserver`` 