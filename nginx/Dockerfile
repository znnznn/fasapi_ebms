FROM node:20.3.0 as build

WORKDIR /app/frontend

COPY ./frontend ./

RUN npm  install

RUN npm run build

# The second stage
# Copy React static files and start nginx
FROM nginx:stable-alpine

COPY ./nginx/development/default.conf /etc/nginx/conf.d/default.conf

COPY --from=build /app/frontend/dist /usr/share/nginx/html
CMD ["nginx", "-g", "daemon off;"]