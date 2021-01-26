# Mongy (Monkey) Serializer
Serialize MongoDB documents to native Python datatypes that can then be easily rendered into JSON, XML or other content types.

I am aiming to make this an opensource project and hence looking for collaborators for improvements and feedback. You can raise a PR or add issues after which  we can work together to resolve it.

# Background
I started this for serializing MongoDB documents as part of one of my projects. However, as it progressed I had an impetus to move this as an independent Open Source work that can be leveraged by others. I do not intend to or claim to replace any of the existing serializers. The code here is completely written by me and there is zero plagiarism.

The sole intention is to have a learning experience along with knowledge sharing plus community help.

# TODO
* ListField with nested composite fields returns list with None when max_depth=0.
* Add support for more plausible data types.
* Memory profiling.
* Concurrency.
* Nested field exclusion.

# Testing
Unittests are written within `py-mongo-serializer/tests` directory. You can run tests using docker as given below.

```
cd py-mongo-serializer

# create a .env file and add below environment variables.
MONGO_INITDB_DATABASE=Mongy
MONGO_INITDB_ROOT_USERNAME=<yourmongousername>
MONGO_INITDB_ROOT_PASSWORD=<yourmongopassword>
MONGO_HOST=mongy_mongo
MONGO_DATA_DIR=/data/db
MONGO_LOG_DIR=/dev/null

docker-compose build
docker-compose up
```

# Contributors
* Jayakrishnan Damodaran (jayakrishnandamodaran@gmail.com)
