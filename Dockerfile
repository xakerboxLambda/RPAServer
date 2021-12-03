# base image
FROM alpine

RUN apk add --update nodejs npm
RUN apk add --no-cache python3 py3-pip



RUN pip3 install robotframework-browser==9.0.2
RUN pip3 install pycryptodome==3.11.0
RUN pip3 install python-dotenv==0.18.0

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

RUN npm run build
CMD ["npm", "run", "server"]