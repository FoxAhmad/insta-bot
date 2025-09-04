# Instagram Bot Frontend

This is the frontend for the Instagram Messaging Bot, designed to be deployed on Vercel.

## 🚀 Quick Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/instagram-bot&root-directory=frontend)

## 📁 Files

- `index.html` - Main HTML file
- `style.css` - CSS styles
- `script.js` - JavaScript functionality
- `vercel.json` - Vercel configuration
- `package.json` - Node.js configuration

## ⚙️ Configuration

Before deploying, update the `API_BASE_URL` in `script.js`:

```javascript
const API_BASE_URL = 'https://your-backend-url.onrender.com';
```

Replace `your-backend-url` with your actual Render backend URL.

## 🌐 Deployment

### Option 1: Vercel CLI

```bash
npm install -g vercel
vercel login
vercel
```

### Option 2: Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Set root directory to `frontend`
4. Deploy

## 🔧 Development

To run locally:

```bash
cd frontend
python -m http.server 3000
```

Then open `http://localhost:3000` in your browser.

## 📱 Features

- Responsive design
- Real-time status updates
- Progress tracking
- Toast notifications
- Mobile-friendly interface
