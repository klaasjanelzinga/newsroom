FROM node:alpine3.10

WORKDIR /usr/src/app

COPY frontend/src /usr/src/app/src
COPY frontend/public /usr/src/app/public
COPY frontend/package.json /usr/src/app
COPY frontend/tsconfig.json /usr/src/app
COPY frontend/package-lock.json /usr/src/app

EXPOSE 3000

RUN cp src/Config.prod.js src/Config.js

RUN npm install
RUN npm install -g serve
RUN npm run-script build

VOLUME [ "/usr/src/app" ]

CMD serve -s build
