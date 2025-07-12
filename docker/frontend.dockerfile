# docker/frontend.dockerfile

FROM node:18-alpine

WORKDIR /app

COPY smart_quiz_frontend/package*.json ./
RUN npm install

COPY smart_quiz_frontend/ .

# Build React app for production
RUN npm run build

# Serve with a simple web server (like serve or nginx)
RUN npm install -g serve

EXPOSE 5173
CMD ["serve", "-s", "dist", "-l", "5173"]
