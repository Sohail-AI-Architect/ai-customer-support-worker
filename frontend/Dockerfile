# Frontend image: Next.js App Router UI (T059).
FROM node:22-alpine

WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 3000

# Local-dev default; a production image would `next build && next start`.
CMD ["npm", "run", "dev"]