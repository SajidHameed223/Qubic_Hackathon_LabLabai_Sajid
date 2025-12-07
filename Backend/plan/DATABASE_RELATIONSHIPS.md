# 🎉 Database Relationships - Complete!

## ✅ **User-Task Relationship Established**

Your database now has a **proper foreign key relationship** between Users and Tasks!

## 📊 **Database Schema**

### **Users Table**
```sql
CREATE TABLE users (
    id VARCHAR PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### **Tasks Table**
```sql
CREATE TABLE tasks (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    data JSON NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Foreign Key Constraint
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
```

## 🔗 **Relationship Details**

### **One-to-Many Relationship**
- **One User** → **Many Tasks**
- **Each Task** → **Belongs to One User**

### **SQLAlchemy Relationships**
```python
class User(Base):
    # One user can have many tasks
    tasks = relationship("TaskRecord", back_populates="user", cascade="all, delete-orphan")

class TaskRecord(Base):
    # Each task belongs to one user
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="tasks")
```

### **Cascade Delete**
When a user is deleted, **all their tasks are automatically deleted** too!

## 🚀 **New API Endpoints**

### **1. List All My Tasks**
```bash
GET /tasks?limit=50&offset=0
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": "task-uuid-1",
    "goal": "Swap 1000 QUBIC to USDT",
    "status": "COMPLETED",
    "created_at": "2025-12-05T16:00:00Z",
    "steps": [...]
  },
  {
    "id": "task-uuid-2",
    "goal": "Create yield farming strategy",
    "status": "PENDING",
    "created_at": "2025-12-05T15:30:00Z",
    "steps": [...]
  }
]
```

### **2. Get Specific Task**
```bash
GET /tasks/{task_id}
Authorization: Bearer <token>
```

**Security:** Only returns the task if it belongs to the authenticated user!

### **3. Delete Task**
```bash
DELETE /tasks/{task_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Task deleted successfully",
  "task_id": "task-uuid-here"
}
```

## 🔒 **Security Features**

### **User Isolation**
- ✅ Users can **only see their own tasks**
- ✅ Users **cannot access other users' tasks**
- ✅ Task IDs are validated against user ownership

### **Example Protection**
```python
# User A tries to access User B's task
GET /tasks/user-b-task-id
Authorization: Bearer user-a-token

# Response: 404 Not Found
# The task exists, but doesn't belong to User A
```

## 💻 **Usage Examples**

### **Python/Requests**
```python
import requests

# Login
login_response = requests.post(
    "http://localhost:8000/auth/login",
    json={"email": "user@example.com", "password": "password123"}
)
token = login_response.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# Create a task
task_response = requests.post(
    "http://localhost:8000/tasks",
    headers=headers,
    json={"goal": "Swap 1000 QUBIC to USDT"}
)
task = task_response.json()

# List all my tasks
tasks_response = requests.get(
    "http://localhost:8000/tasks",
    headers=headers
)
my_tasks = tasks_response.json()

# Get specific task
task_detail = requests.get(
    f"http://localhost:8000/tasks/{task['id']}",
    headers=headers
)

# Delete task
delete_response = requests.delete(
    f"http://localhost:8000/tasks/{task['id']}",
    headers=headers
)
```

### **JavaScript/Fetch**
```javascript
const token = localStorage.getItem('token');
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};

// List all my tasks
async function getMyTasks() {
  const response = await fetch('http://localhost:8000/tasks', { headers });
  return await response.json();
}

// Create task
async function createTask(goal) {
  const response = await fetch('http://localhost:8000/tasks', {
    method: 'POST',
    headers,
    body: JSON.stringify({ goal })
  });
  return await response.json();
}

// Delete task
async function deleteTask(taskId) {
  const response = await fetch(`http://localhost:8000/tasks/${taskId}`, {
    method: 'DELETE',
    headers
  });
  return await response.json();
}
```

## 🎯 **Query User's Tasks via SQLAlchemy**

### **Get all tasks for a user**
```python
# In your code
user = db.query(User).filter(User.email == "user@example.com").first()

# Access all tasks via relationship
user_tasks = user.tasks  # Returns list of TaskRecord objects

# Or query directly
tasks = db.query(TaskRecord).filter(TaskRecord.user_id == user.id).all()
```

### **Get user from task**
```python
task = db.query(TaskRecord).filter(TaskRecord.id == task_id).first()

# Access user via relationship
task_owner = task.user  # Returns User object
print(f"Task belongs to: {task_owner.email}")
```

## 📈 **Pagination Support**

List tasks with pagination:
```bash
# First 50 tasks
GET /tasks?limit=50&offset=0

# Next 50 tasks
GET /tasks?limit=50&offset=50

# Get 10 tasks
GET /tasks?limit=10&offset=0
```

## 🔍 **Database Queries**

### **Count user's tasks**
```python
task_count = db.query(TaskRecord).filter(TaskRecord.user_id == user.id).count()
```

### **Get recent tasks**
```python
recent_tasks = (
    db.query(TaskRecord)
    .filter(TaskRecord.user_id == user.id)
    .order_by(TaskRecord.created_at.desc())
    .limit(10)
    .all()
)
```

### **Filter by status**
```python
# This requires parsing the JSON data field
# For better filtering, consider adding status as a separate column
```

## 🎨 **Frontend Integration**

### **React Component Example**
```jsx
function TaskList() {
  const [tasks, setTasks] = useState([]);
  const token = localStorage.getItem('token');

  useEffect(() => {
    fetchTasks();
  }, []);

  async function fetchTasks() {
    const response = await fetch('http://localhost:8000/tasks', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    setTasks(data);
  }

  async function deleteTask(taskId) {
    await fetch(`http://localhost:8000/tasks/${taskId}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    fetchTasks(); // Refresh list
  }

  return (
    <div>
      <h2>My Tasks</h2>
      {tasks.map(task => (
        <div key={task.id}>
          <h3>{task.goal}</h3>
          <p>Status: {task.status}</p>
          <button onClick={() => deleteTask(task.id)}>Delete</button>
        </div>
      ))}
    </div>
  );
}
```

## ✨ **Benefits**

1. **Data Integrity** - Foreign key ensures tasks always belong to valid users
2. **Automatic Cleanup** - Cascade delete removes orphaned tasks
3. **Easy Queries** - SQLAlchemy relationships make queries simple
4. **Security** - Users can only access their own data
5. **Scalability** - Indexed user_id for fast lookups

## 🎉 **Summary**

Your database now has:
- ✅ **Proper foreign key** relationship
- ✅ **SQLAlchemy relationships** for easy querying
- ✅ **Cascade delete** for data integrity
- ✅ **User isolation** for security
- ✅ **Pagination** support
- ✅ **Full CRUD** operations (Create, Read, Update, Delete)

**Your backend is now production-ready with proper database relationships!** 🚀
