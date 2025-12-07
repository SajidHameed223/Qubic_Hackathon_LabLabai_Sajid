# 🔐 Qubic Autopilot Worker - Authentication Guide

## 🎯 Overview

Your Qubic Autopilot Worker now has **full JWT authentication** with user registration, login, and protected routes!

## 🚀 Quick Start

### 1. **Register a New User**

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'
```

Response:
```json
{
  "id": "uuid-here",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2025-12-05T16:00:00Z"
}
```

### 2. **Login to Get JWT Token**

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. **Use Token to Access Protected Routes**

```bash
# Save your token
TOKEN="your-jwt-token-here"

# Access protected endpoint
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "goal": "Swap 1000 QUBIC to USDT and stake in yield farm"
  }'
```

## 📚 API Endpoints

### 🔓 **Public Endpoints** (No Authentication Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login and get JWT token |

### 🔒 **Protected Endpoints** (Require Authentication)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/auth/me` | Get current user info |
| POST | `/auth/logout` | Logout (client-side) |
| POST | `/agent/run` | Run AI agent with goal |
| POST | `/agent/trigger` | Trigger agent via webhook |
| POST | `/tasks` | Create a new task |
| GET | `/tasks/{id}` | Get task by ID |
| POST | `/tasks/{id}/run` | Run existing task |
| GET | `/tools/list` | List all tools |
| POST | `/tools/execute/{name}` | Execute a tool |
| POST | `/debug/send-qu` | Debug QU transaction |

## 🔑 Authentication Flow

```
┌─────────────┐
│   Register  │
│   /auth/    │
│  register   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Login    │
│   /auth/    │
│   login     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Get Token  │
│   (JWT)     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Include   │
│   Token in  │
│   Headers   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Access    │
│  Protected  │
│   Routes    │
└─────────────┘
```

## 💻 Frontend Integration Examples

### **JavaScript/Fetch**

```javascript
// Register
async function register(email, password, fullName) {
  const response = await fetch('http://localhost:8000/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email,
      password,
      full_name: fullName
    })
  });
  return await response.json();
}

// Login
async function login(email, password) {
  const response = await fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();
  
  // Save token to localStorage
  localStorage.setItem('token', data.access_token);
  return data;
}

// Use protected endpoint
async function runAgent(goal) {
  const token = localStorage.getItem('token');
  
  const response = await fetch('http://localhost:8000/agent/run', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ goal })
  });
  
  return await response.json();
}

// Get current user
async function getCurrentUser() {
  const token = localStorage.getItem('token');
  
  const response = await fetch('http://localhost:8000/auth/me', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
}

// Logout
function logout() {
  localStorage.removeItem('token');
}
```

### **React Example**

```jsx
import { useState, useEffect } from 'react';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (token) {
      fetchCurrentUser();
    }
  }, [token]);

  async function fetchCurrentUser() {
    const response = await fetch('http://localhost:8000/auth/me', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    setUser(data);
  }

  async function handleLogin(email, password) {
    const response = await fetch('http://localhost:8000/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    
    localStorage.setItem('token', data.access_token);
    setToken(data.access_token);
  }

  async function runAgent(goal) {
    const response = await fetch('http://localhost:8000/agent/run', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ goal })
    });
    return await response.json();
  }

  function handleLogout() {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  }

  if (!token) {
    return <LoginForm onLogin={handleLogin} />;
  }

  return (
    <div>
      <h1>Welcome, {user?.full_name}!</h1>
      <button onClick={handleLogout}>Logout</button>
      <AgentInterface onRun={runAgent} />
    </div>
  );
}
```

## 🔒 Security Features

✅ **Password Hashing** - Bcrypt with salt  
✅ **JWT Tokens** - Secure, stateless authentication  
✅ **Token Expiration** - 7 days (configurable)  
✅ **Protected Routes** - All sensitive endpoints require auth  
✅ **User Ownership** - Tasks are linked to users  
✅ **CORS Enabled** - Ready for frontend integration  

## 🛡️ Security Best Practices

### **Production Checklist**

1. **Change SECRET_KEY**
   ```bash
   # Generate a secure key
   openssl rand -hex 32
   
   # Add to .env
   SECRET_KEY=your-generated-key-here
   ```

2. **Update CORS Origins**
   ```python
   # In app/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-frontend.com"],  # Specific domain
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **Use HTTPS** in production

4. **Add Rate Limiting** (recommended)

5. **Implement Token Refresh** (optional)

## 📊 Database Schema

### **Users Table**
```sql
CREATE TABLE users (
    id VARCHAR PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### **Tasks Table**
```sql
CREATE TABLE tasks (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR REFERENCES users(id),
    data JSON NOT NULL
);
```

## 🎯 Next Steps

1. **Build Your Frontend**
   - Use React, Vue, or vanilla JS
   - Implement login/register forms
   - Store JWT in localStorage/cookies
   - Add Authorization header to requests

2. **Customize User Model**
   - Add more fields (avatar, bio, etc.)
   - Implement user roles (admin, user)
   - Add email verification

3. **Add More Features**
   - Password reset
   - Email notifications
   - User preferences
   - API key generation

## 🐛 Troubleshooting

### **401 Unauthorized**
- Check if token is included in headers
- Verify token hasn't expired
- Ensure token format: `Bearer <token>`

### **403 Forbidden**
- User account might be inactive
- Check `is_active` field in database

### **404 Task Not Found**
- Tasks are user-specific
- Can only access your own tasks

## 📚 API Documentation

Visit http://localhost:8000/docs for interactive API documentation!

## 🎉 You're All Set!

Your Qubic Autopilot Worker is now:
- ✅ Fully authenticated
- ✅ User-personalized
- ✅ Ready for frontend integration
- ✅ Production-ready (with security updates)

**Start building your frontend and create amazing DeFi experiences!** 🚀
