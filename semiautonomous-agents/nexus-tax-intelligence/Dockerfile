FROM node:22-slim AS frontend-build
WORKDIR /app/frontend
COPY package.json package-lock.json* ./
RUN npm ci
COPY index.html vite.config.js eslint.config.js ./
COPY public/ public/
COPY src/ src/
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY --from=frontend-build /app/frontend/dist /app/dist

COPY backend/pyproject.toml backend/.python-version ./
RUN pip install uv && uv pip install --system -r pyproject.toml

COPY backend/ ./

EXPOSE 8080
ENV PORT=8080

RUN python -c "from fastapi.staticfiles import StaticFiles; print('deps ok')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
