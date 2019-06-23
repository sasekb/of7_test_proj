Prerequisites:
Please install Docker (https://docs.docker.com/install/)
and Docker compose (https://docs.docker.com/compose/install/) if needed.

How to run:
From root folder run:
"docker-compose up --build"
This might take a few minutes. After everything is up and running you can access the server at localhost:8000.

Important endpoints:
Admin: localhost:8000/admin (username: admin, password: admin)
Token auth: localhost:8000/api-token-auth/ (method: POST, payload: {"username": "admin", "password": "admin")
List active backends: http://localhost:8000/mediation/backends/ (can be used to create a new backend too; or use admin)
Backend RUD view: http://localhost:8000/mediation/backends/<id>
List all backends: http://localhost:8000/mediation/backends/show_all/

BULK ACTIVATE BACKENDS:
POST: localhost:8000/mediation/backends/bulk_activate/
Payload: list of IDs to activate (i.e. [3, 2]). Other backends will be deactivated. Backends will be ordered base on
the input parameter (here 3 will be before 2)

Assumptions:
- Batch processor needs to know IDs of backends in this system. But the lookup field can be quickly changed.
- I didn't make any assumptions about the date for backends. The only field I added is therefore "name" but other
    attributes can easily be added.
- System comes preloaded with 3 backends (of which 2 are activated) and 1 user. This is for testing only.
- The only read heavy endpoint is http://localhost:8000/mediation/backends/, this is the only one cached. Other views
    could be cached but given the criteria there is no need. In reality a cache mixin would be used on models or views
    to cache across the board.

What could be improved:
CODE:
- This simple token authentication will probably have to be replaced with something else (depends on your security guidelines)
- A simple permission model is used (write enabled for authenticated users, others can only read) for testing
    purposes, but in reality this would need a more fine grained control
- For security reasons admin interface should be either disabled or moved (a sinkhole should be put in its usual spot)
- For ease of use of the reviewer I left the server in debug mode (will help you with available endpoints if you get lost)

DEV OPS:
- Redis and Postgres are not protected with a password, but this is often not in a developer's domain so I left it as is
- In order to run a load balancer in front of this, cache & database would have to be configured separately.

