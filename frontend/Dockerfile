FROM node:20

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the entire frontend project to the working directory
COPY . .

COPY .env.docker .env

# Build the SvelteKit app
RUN npm run build

# Expose the port on which the frontend will run (e.g., 3000)
EXPOSE 3000

# Start the SvelteKit app
CMD ["npm", "run", "preview"]