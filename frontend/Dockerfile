# use node images
FROM node:20-alpine

#working directory
WORKDIR /app

#install all dependencies
COPY package*.json ./
RUN npm install

#Copy frontend code
COPY . .

#Build frontend
RUN npm run build

#Expose Vite preview port
EXPOSE 4173

#Run Vite preview server
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0"]