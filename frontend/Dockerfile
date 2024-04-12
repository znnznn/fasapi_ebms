FROM node:20.3.0

WORKDIR /app/frontend

ENV PATH /app/node_modules/.bin:$PATH

COPY . .

RUN npm install

RUN npm run build

ENV NODE_ENV development

EXPOSE 3000
