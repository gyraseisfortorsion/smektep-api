# Use the official Python base image
FROM python:3.9-slim-buster

# Install dependencies
RUN pip install --upgrade pip
RUN pip install pipenv

# install dependencies for pdfs
# RUN apt-get update \
#     && apt-get install -y \
#         curl \
#         libxrender1 \
#         libjpeg62-turbo \
#         fontconfig \
#         libxtst6 \
#         xfonts-75dpi \
#         xfonts-base \
#         xz-utils \
#         libssl1.1
# RUN curl "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb" -L -o "wkhtmltopdf.deb"

# RUN dpkg -i wkhtmltopdf.deb
RUN apt-get update && apt-get install -y libaio1 wget unzip tzdata && apt-get install -y git && apt-get install -y xz-utils
RUN apt-get install libssl-dev wkhtmltopdf -y

# RUN wget https://poppler.freedesktop.org/poppler-21.09.0.tar.xz

# RUN apt-get install -y libnss3 libnss3-dev
# RUN apt-get install -y libcairo2-dev libjpeg-dev libgif-dev
# RUN apt-get install -y cmake libblkid-dev e2fslibs-dev libboost-all-dev libaudit-dev

# RUN apt-get install -y build-essential
# # Extract and build poppler
# RUN tar -xvf poppler-21.09.0.tar.xz && \
#     cd poppler-21.09.0/ && \
#     mkdir build && \
#     cd build/ && \
#     cmake -DCMAKE_BUILD_TYPE=Release \
#           -DCMAKE_INSTALL_PREFIX=/usr \
#           -DTESTDATADIR=$PWD/testfiles \
#           -DENABLE_UNSTABLE_API_ABI_HEADERS=ON .. && \
#     make && \
#     make install

RUN apt-get install poppler-utils -y


# timezone to +0
ENV TZ=Asia/Almaty
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip install -r requirements.txt

# Copy the application code to the working directory
COPY . .

# Expose the port on which the application will run
# EXPOSE 8080

# Run the FastAPI application using uvicorn server
# CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]