# Stage 1 - Install dependencies and build the app in a build environment
FROM debian:latest AS build-env

# Set build arguments
ARG API_KEY

# Set the environment variable to be used in the flutter build
ENV API_KEY=${_API_KEY}

WORKDIR /app

# Install flutter dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    wget \
    unzip \
    libgconf-2-4 \
    gdb \
    libstdc++6 \
    libglu1-mesa \
    fonts-droid-fallback \
    lib32stdc++6 \
    python3 \
    sed \
    && apt-get clean

# Clone the flutter repo
RUN git clone https://github.com/flutter/flutter.git /app/flutter

# Set flutter path
ENV PATH="${PATH}:/app/flutter/bin:/app/flutter/bin/cache/dart-sdk/bin"

# Run flutter doctor
RUN flutter doctor -v
RUN flutter channel master
RUN flutter upgrade

# Clone the project repository
RUN git clone --depth 1 https://github.com/jchavezar/vertex-ai-samples.git /app/vertex-ai-samples

# Set the working directory
WORKDIR /app/vertex-ai-samples/gen_ai/flutter/home_listings

# Build the flutter web app
RUN flutter build web --dart-define API_KEY=${_API_KEY:-}

# Stage 2 - Use Nginx to serve the built app
FROM nginx:stable-alpine3.19-perl

# Copy the built web app to the nginx html directory
COPY --from=build-env /app/vertex-ai-samples/gen_ai/flutter/home_listings/build/web /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

