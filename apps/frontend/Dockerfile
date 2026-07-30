# 1. Aşama: Derleme (Build) Aşaması
FROM node:22-alpine AS build

WORKDIR /app

# Monorepo yapısına uygun olarak sadece frontend bağımlılıklarını kopyalıyoruz
COPY apps/frontend/package.json apps/frontend/package-lock.json* ./
RUN npm install

# Tüm frontend kaynak kodunu konteyner içine alıyoruz
COPY apps/frontend/ ./

# Backend'in adresini build zamanında Vite'a gömüyoruz (CP-54)
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Üretim çıktısını (dist klasörünü) oluşturuyoruz
RUN npm run build

# 2. Aşama: Canlı Yayın (Production/Nginx) Aşaması
FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
  CMD wget -q --spider http://localhost:80 || exit 1

# Nginx varsayılan olarak 80 portunda çalışır
EXPOSE 80