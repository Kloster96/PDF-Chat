# 💬 Frontend - RAG PDF Chat UI

Interfaz de usuario moderna para chatear con PDFs. Construida con React, Tailwind CSS y diseño dark mode.

## 🚀 Instalación

```bash
# Navegar al directorio frontend
cd frontend

# Instalar dependencias
npm install
```

## ▶️ Ejecución

```bash
# Servidor de desarrollo
npm run dev

# Build para producción
npm run build
```

La aplicación estará disponible en `http://localhost:3000`

## 🔧 Configuración

### Variables de entorno

Crear archivo `.env` en `frontend/`:

```env
VITE_API_URL=http://localhost:8000
```

## 🎨 Características

- **Dark Mode** elegante con Tailwind CSS
- **Drag & Drop** para subir PDFs con barra de progreso
- **Chat estilo ChatGPT** con bubbles diferenciadas
- **Indicador de conexión** con el backend
- **Historial de conversación** con fuentes consultadas

## 📁 Estructura

```
frontend/
├── src/
│   ├── components/     # Componentes React
│   │   ├── Sidebar.jsx
│   │   └── ChatWindow.jsx
│   ├── services/      # API client
│   │   └── api.js
│   ├── App.jsx        # Componente principal
│   ├── main.jsx       # Entry point
│   └── index.css      # Estilos Tailwind
├── index.html
├── package.json
├── tailwind.config.js
├── vite.config.js
└── README.md
```

## 🛠️ Tecnologías

- React 18, Vite, Tailwind CSS, Axios, Lucide React

## 🔗 Conexión con Backend

El frontend se conecta al backend en `http://localhost:8000` por defecto.

| Endpoint | Descripción |
|----------|-------------|
| `GET /health` | Verificar conexión |
| `POST /upload` | Subir PDF |
| `POST /query` | Consultar documento |
| `POST /reset` | Limpiar conversación |