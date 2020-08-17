FROM node:alpine3.10

WORKDIR /usr/src/app

COPY src /usr/src/app/src
COPY public /usr/src/app/public
COPY package.json /usr/src/app
COPY yarn.lock /usr/src/app

EXPOSE 3000

RUN cp src/Config.prod.js src/Config.js

RUN yarn install
RUN npm install -g serve
RUN npm run-script build

VOLUME [ "/usr/src/app" ]

CMD serve -s build