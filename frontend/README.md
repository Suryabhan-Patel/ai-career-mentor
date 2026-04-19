# AI Career Mentor - Frontend

A modern, production-ready React frontend for the AI Career Mentor application built with Vite and Tailwind CSS.

## 🚀 Features

- **Modern React Setup** - Using Vite for fast development and optimized builds
- **Beautiful UI** - Clean, responsive design with Tailwind CSS
- **Smooth Animations** - Fade-in and slide-up animations for better UX
- **File Upload** - Drag-and-drop PDF resume upload with validation
- **Real-time Analysis** - Display AI-powered career analysis results
- **Responsive Design** - Works perfectly on mobile, tablet, and desktop
- **Error Handling** - Comprehensive error messaging and validation

## 📋 Prerequisites

- Node.js (v16+)
- npm or yarn
- Backend API running at `http://127.0.0.1:8000`

## 🛠️ Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

## 🚀 Running the Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## 📦 Build for Production

```bash
npm run build
```

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Upload.jsx         # Resume upload component
│   │   ├── Result.jsx          # Results display component
│   │   └── RoleCard.jsx        # Individual role card component
│   ├── App.jsx                 # Main application component
│   ├── main.jsx                # React DOM entry point
│   ├── index.css               # Tailwind CSS + custom styles
│   └── assets/                 # Static assets
├── index.html                  # HTML entry point
├── vite.config.js             # Vite configuration
├── tailwind.config.js         # Tailwind CSS configuration
├── postcss.config.js          # PostCSS configuration
└── package.json               # Dependencies and scripts
```

## 🔧 Configuration

The API endpoint is configured in `src/App.jsx`:

```javascript
const API_BASE_URL = 'http://127.0.0.1:8000';
```

## 📦 Key Dependencies

- **React 19** - UI library
- **Vite 8** - Build tool & dev server
- **Tailwind CSS 4** - Utility-first CSS framework
- **PostCSS** - CSS transformations

## 🎨 Components

### Upload.jsx
- Drag-and-drop PDF upload
- File validation (PDF only, max 10MB)
- Loading states
- Error messages

### Result.jsx
- Display career analysis results
- Show detected skills
- List recommended roles
- Skills to learn section
- Action recommendations

### RoleCard.jsx
- Individual role card component
- Match percentage with progress bar
- Color-coded match levels (green 80%+, blue 60%+, etc.)
- Skill tags display

## ✨ UI Features

- ✅ Responsive grid layouts
- ✅ Tailwind CSS styling
- ✅ Smooth fade-in animations
- ✅ Animated progress bars
- ✅ Spinning loader animation
- ✅ Color-coded match scores
- ✅ Mobile-first design
- ✅ Clean typography

## 🚀 Running Both Frontend & Backend

**Terminal 1 - Backend:**
```bash
cd ..
python -m uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Access the application at `http://localhost:5173`

## 🔌 API Integration

Connects to the backend endpoint:
- `POST /api/upload-resume` - Upload and analyze PDF resume

Expected response structure:
```json
{
  "detected_skills": ["Python", "React"],
  "top_role": {
    "name": "Full Stack Developer",
    "description": "...",
    "match_percentage": 85,
    "required_skills": ["Python", "React"]
  },
  "all_roles": [...],
  "missing_skills": ["TypeScript"]
}
```

## 🐛 Troubleshooting

**Connection Error:**
- Ensure backend is running: `python -m uvicorn app.main:app --reload`
- Check CORS settings in backend
- Verify API URL in `App.jsx`

**Styles Not Loading:**
- Run `npm install` to ensure Tailwind is installed
- Restart dev server: `npm run dev`

**Build Issues:**
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node.js version: `node --version` (v16+ required)

## 📚 Resources

- [React Docs](https://react.dev)
- [Vite Docs](https://vitejs.dev)
- [Tailwind CSS](https://tailwindcss.com)

---

Built with ❤️ for career growth! 🚀
# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is enabled on this template. See [this documentation](https://react.dev/learn/react-compiler) for more information.

Note: This will impact Vite dev & build performances.

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
