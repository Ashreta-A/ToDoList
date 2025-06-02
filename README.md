# Smart Todo List Application

A feature-rich todo list application built with Streamlit that helps you manage your tasks efficiently.

## Features

- User Authentication (Login/Register)
- Task Management with Priorities
- Due Date Tracking
- Notes with Editable Titles
- Task Sorting and Filtering
- Comprehensive Statistics Dashboard
- Daily Task Tracking
- Weekly Progress Visualization

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/smart-todo-list.git
cd smart-todo-list
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run Home.py
```

## Project Structure

- `Home.py` - Main application file with login/registration
- `pages/1_Dashboard.py` - Main todo list functionality
- `pages/2_Documentation.py` - Application documentation
- `pages/3_Statistics.py` - Task statistics and analytics
- `data/` - Directory for storing user data

## Usage

1. Register a new account or login with existing credentials
2. Add tasks with priorities and due dates
3. Mark tasks as complete
4. View task statistics and progress
5. Check documentation for detailed features

## Data Storage

User data is stored locally in JSON format in the `data/` directory:
- User credentials: `data/users.json`
- User todos: `data/username_todos.json`

## Deployment

The application can be deployed on Streamlit Cloud:
1. Fork this repository
2. Connect your GitHub account to Streamlit Cloud
3. Deploy the application directly from your repository

## Contributing

Feel free to submit issues and enhancement requests! 