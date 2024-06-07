FROM node:18-alpine
ENV PORT_REACT_FRONTEND_INSIDE_CONTAINER=$PORT_REACT_FRONTEND_INSIDE_CONTAINER
ENV NODE_OPTIONS=--openssl-legacy-provider

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

EXPOSE $PORT_REACT_FRONTEND_INSIDE_CONTAINER

CMD ["sh", "-c", "npm start"]
