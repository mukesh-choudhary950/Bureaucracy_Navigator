import { create } from 'zustand'

interface Task {
  id: number
  title: string
  description: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
  plan?: any
  results?: any
  createdAt: Date
  updatedAt?: Date
}

interface TaskStore {
  tasks: Task[]
  setTasks: (tasks: Task[]) => void
  addTask: (task: Task) => void
  updateTask: (id: number, updates: Partial<Task>) => void
  createTask: (task: Omit<Task, 'id'>) => void
  fetchTasks: () => Promise<void>
  getTaskById: (id: number) => Task | undefined
}

export const useTaskStore = create<TaskStore>((set, get) => ({
  tasks: [],
  setTasks: (tasks) => set({ tasks }),
  addTask: (task) => set((state) => ({ 
    tasks: [...state.tasks, task] 
  })),
  updateTask: (id, updates) => set((state) => ({
    tasks: state.tasks.map(task => 
      task.id === id ? { ...task, ...updates } : task
    )
  })),
  createTask: (task) => {
    const newTask = { ...task, id: Date.now() }
    set((state) => ({ tasks: [...state.tasks, newTask] }))
  },
  fetchTasks: async () => {
    try {
      const response = await fetch('/api/query/user/1/tasks')
      const tasks = await response.json()
      set({ tasks })
    } catch (error) {
      console.error('Failed to fetch tasks:', error)
    }
  },
  getTaskById: (id) => {
    const state = get()
    return state.tasks.find(task => task.id === id)
  }
}))
