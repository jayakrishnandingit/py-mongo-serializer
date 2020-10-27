FROM python:3.8-slim

# Set environment varibles for build.
ENV PYTHONUNBUFFERED 1

RUN apt-get clean \
	&& apt-get update -y

# upgrade pip to the latest version.
RUN pip install --upgrade pip

# Set the working directory.
WORKDIR /mongy/

COPY requirements.txt requirements.txt
# Install required python packages.
RUN pip install -r requirements.txt

COPY mongy_serializer/__init__.py mongy_serializer/__init__.py
COPY mongy_serializer/fields.py mongy_serializer/fields.py
COPY mongy_serializer/serializer.py mongy_serializer/serializer.py

COPY tests tests/

ENV PYTHONPATH $PYTHONPATH:/mongy

CMD ["python", "-m", "unittest"]
