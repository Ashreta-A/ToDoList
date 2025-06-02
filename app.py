import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os
import yaml
import streamlit_authenticator as stauth
import bcrypt

# Set page configuration
st.set_page_config(
    page_title="Smart Todo List",
    page_icon="✅",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .task-container {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .completed-task {
        text-decoration: line-through;
        color: #666;
    }
    .note-title {
        font-weight: bold;
        font-size: 1.2em;
        margin-bottom: 10px;
    }
    .documentation-links {
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 5px;
        margin: 10px 0;
    }
    .stTextArea textarea {
        height: 150px;
    }
    .priority-high {
        color: red;
        font-weight: bold;
    }
    .priority-medium {
        color: orange;
        font-weight: bold;
    }
    .priority-low {
        color: green;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authentication_status' not in st.session_state:
    st.session_state.authentication_status = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'todos' not in st.session_state:
    st.session_state.todos = {}
if 'notes' not in st.session_state:
    st.session_state.notes = {}
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1

# Load or create config file
if not os.path.exists('config.yaml'):
    config = {
        'credentials': {
            'usernames': {}
        }
    }
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
else:
    with open('config.yaml') as file:
        config = yaml.safe_load(file)

# Authentication
authenticator = stauth.Authenticate(
    config['credentials'],
    'todo_app_cookie',
    'todo_app_key',
    cookie_expiry_days=30
)

# Login/Register interface
if st.session_state.authentication_status is None or st.session_state.authentication_status == False:
    st.title("✨ Smart Todo List")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        name, authentication_status, username = authenticator.login('Login', 'main')
        if st.session_state.authentication_status == False:
            st.error('Username/password is incorrect')
    
    with tab2:
        st.subheader("Register New User")
        new_username = st.text_input("Username", key="reg_username")
        new_password = st.text_input("Password", type="password", key="reg_password")
        if st.button("Create Account"):
            if new_username and new_password:
                if new_username not in config['credentials']['usernames']:
                    config['credentials']['usernames'][new_username] = {
                        'password': bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode(),
                        'name': new_username
                    }
                    with open('config.yaml', 'w') as file:
                        yaml.dump(config, file, default_flow_style=False)
                    st.success("Account created successfully! Please login.")
                else:
                    st.error("Username already exists!")
            else:
                st.error("Please enter both username and password!")

# Main application
if st.session_state.authentication_status:
    # Save and load functions
    def save_data():
        try:
            data = {
                'todos': st.session_state.todos,
                'notes': st.session_state.notes
            }
            with open(f'data_{st.session_state.username}.json', 'w') as f:
                json.dump(data, f)
        except Exception as e:
            st.error(f"Error saving data: {str(e)}")

    def load_data():
        try:
            if os.path.exists(f'data_{st.session_state.username}.json'):
                with open(f'data_{st.session_state.username}.json', 'r') as f:
                    data = json.load(f)
                    st.session_state.todos[st.session_state.username] = data['todos'].get(st.session_state.username, [])
                    st.session_state.notes[st.session_state.username] = data['notes'].get(st.session_state.username, [])
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")

    # Initialize user data if not exists
    if st.session_state.username not in st.session_state.todos:
        st.session_state.todos[st.session_state.username] = []
    if st.session_state.username not in st.session_state.notes:
        st.session_state.notes[st.session_state.username] = [
            {'title': 'Meeting Notes', 'content': 'Meeting notes go here...'},
            {'title': 'Important Deadlines', 'content': 'Important deadlines...'},
            {'title': 'Project Ideas', 'content': 'Project ideas...'},
            {'title': 'Shopping List', 'content': 'Shopping list...'},
            {'title': 'Reminders', 'content': 'Reminders...'}
        ]

    # Load existing data
    load_data()

    # Main app header
    st.title(f"✨ Welcome {st.session_state.username}!")
    authenticator.logout('Logout', 'main')
    st.markdown("---")

    # Layout with columns
    col1, col2 = st.columns([2, 1])

    with col1:
        # Add new todo
        with st.form(key='add_todo_form'):
            new_todo = st.text_input("Add a new task")
            col_a, col_b = st.columns(2)
            with col_a:
                priority = st.select_slider("Priority", options=['Low', 'Medium', 'High'])
                priority_value = {'High': 0, 'Medium': 1, 'Low': 2}[priority]
            with col_b:
                due_date = st.date_input("Due date")
            
            details = st.text_area("Task Details", height=100)
            submit_button = st.form_submit_button(label='Add Task')
            
            if submit_button and new_todo:
                try:
                    new_task = {
                        'task': new_todo,
                        'completed': False,
                        'priority': priority,
                        'priority_value': priority_value,
                        'due_date': due_date.strftime("%Y-%m-%d"),
                        'details': details,
                        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.todos[st.session_state.username].append(new_task)
                    save_data()
                    st.success("Task added successfully!")
                except Exception as e:
                    st.error(f"Error adding task: {str(e)}")

        # Display todos with pagination
        st.subheader("📝 Tasks")
        
        # Filter and sort todos
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            show_completed = st.checkbox("Show completed tasks", True)
        with filter_col2:
            sort_by = st.selectbox("Sort by", ["Priority", "Due date", "Created date"])

        try:
            user_todos = st.session_state.todos[st.session_state.username]
            filtered_todos = [todo for todo in user_todos if show_completed or not todo.get('completed', False)]
            
            if sort_by == "Priority":
                filtered_todos.sort(key=lambda x: (x.get('priority_value', 2), x.get('due_date', '')))
            elif sort_by == "Due date":
                filtered_todos.sort(key=lambda x: x.get('due_date', ''))
            else:
                filtered_todos.sort(key=lambda x: x.get('created_at', ''), reverse=True)

            if filtered_todos:
                for idx, todo in enumerate(filtered_todos):
                    with st.container():
                        col1, col2, col3 = st.columns([0.1, 2.8, 0.1])
                        
                        with col1:
                            completed = st.checkbox(
                                "Complete task",
                                todo.get('completed', False),
                                key=f"todo_{idx}",
                                label_visibility="collapsed"
                            )
                            if completed != todo.get('completed', False):
                                todo_idx = user_todos.index(todo)
                                st.session_state.todos[st.session_state.username][todo_idx]['completed'] = completed
                                save_data()
                        
                        with col2:
                            task_style = "completed-task" if todo.get('completed', False) else ""
                            priority_class = f"priority-{todo.get('priority', 'low').lower()}"
                            with st.expander(f"📌 {todo.get('task', 'Untitled Task')}", expanded=False):
                                st.markdown(f"""
                                    <div class="task-container {task_style}">
                                        <h4>{todo.get('task', 'Untitled Task')}</h4>
                                        <p>Priority: <span class="{priority_class}">{todo.get('priority', 'Low')}</span></p>
                                        <p>Due: {todo.get('due_date', 'No date')}</p>
                                        <p>Details: {todo.get('details', 'No details')}</p>
                                    </div>
                                """, unsafe_allow_html=True)
                        
                        with col3:
                            if st.button("🗑️", key=f"delete_{idx}"):
                                st.session_state.todos[st.session_state.username].remove(todo)
                                save_data()
                                st.rerun()
            else:
                st.info("No tasks to display. Add some tasks to get started!")

        except Exception as e:
            st.error(f"Error processing tasks: {str(e)}")
            st.error("Please try refreshing the page or adding new tasks.")

    with col2:
        # Notes section
        st.subheader("📌 Quick Notes")
        
        # Add new note button
        if st.button("➕ Add New Note"):
            try:
                st.session_state.notes[st.session_state.username].append({
                    'title': 'New Note',
                    'content': 'Write your note here...'
                })
                save_data()
                st.rerun()
            except Exception as e:
                st.error(f"Error adding note: {str(e)}")
        
        for i, note in enumerate(st.session_state.notes[st.session_state.username]):
            try:
                with st.expander(f"📝 {note.get('title', 'Untitled Note')}", expanded=False):
                    new_title = st.text_input("Title", note.get('title', ''), key=f"title_{i}")
                    new_content = st.text_area("Content", note.get('content', ''), key=f"note_{i}")
                    
                    if new_title != note.get('title', '') or new_content != note.get('content', ''):
                        st.session_state.notes[st.session_state.username][i]['title'] = new_title
                        st.session_state.notes[st.session_state.username][i]['content'] = new_content
                        save_data()
                    
                    if st.button("🗑️ Delete Note", key=f"delete_note_{i}"):
                        st.session_state.notes[st.session_state.username].pop(i)
                        save_data()
                        st.rerun()
            except Exception as e:
                st.error(f"Error displaying note {i+1}: {str(e)}")

    # Footer
    st.markdown("---")
    st.markdown("### 📊 Task Statistics")
    try:
        user_todos = st.session_state.todos[st.session_state.username]
        completed_count = len([todo for todo in user_todos if todo.get('completed', False)])
        total_count = len(user_todos)
        if total_count > 0:
            progress = completed_count / total_count
            st.progress(progress)
            st.write(f"Completed: {completed_count}/{total_count} tasks ({int(progress*100)}%)")
            
            # Priority distribution
            priority_counts = {'High': 0, 'Medium': 0, 'Low': 0}
            for todo in user_todos:
                if not todo.get('completed', False):
                    priority_counts[todo.get('priority', 'Low')] += 1
            
            st.write("### Priority Distribution (Pending Tasks)")
            for priority, count in priority_counts.items():
                st.write(f"{priority}: {count} tasks")
                
    except Exception as e:
        st.error(f"Error calculating statistics: {str(e)}")

    # Page References Section
    st.markdown("---")
    st.markdown("""
    <h2 style='text-align: center; color: #1E88E5;'>📚 Helpful Resources & References</h2>
    """, unsafe_allow_html=True)

    with st.expander("🔍 Quick Navigation", expanded=False):
        st.markdown("""
        - [Task Management](#task-management)
        - [Notes Section](#notes-section)
        - [Statistics](#statistics)
        - [Documentation](#documentation)
        """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 🎓 Learning Resources
        
        #### Python Fundamentals
        - [Python Official Tutorial](https://docs.python.org/3/tutorial/)
        - [Python for Beginners](https://www.python.org/about/gettingstarted/)
        - [Real Python Tutorials](https://realpython.com/)
        
        #### Data Science & Analytics
        - [Pandas User Guide](https://pandas.pydata.org/docs/user_guide/index.html)
        - [NumPy Tutorials](https://numpy.org/learn/)
        - [Data Science Handbook](https://jakevdp.github.io/PythonDataScienceHandbook/)
        
        #### Web Development
        - [Streamlit Gallery](https://streamlit.io/gallery)
        - [Streamlit Components](https://streamlit.io/components)
        - [Web Dev with Python](https://www.fullstackpython.com/)
        """)

    with col2:
        st.markdown("""
        ### 🛠️ Development Tools
        
        #### Code Editors & IDEs
        - [Visual Studio Code](https://code.visualstudio.com/)
        - [PyCharm](https://www.jetbrains.com/pycharm/)
        - [Jupyter Notebooks](https://jupyter.org/)
        
        #### Version Control
        - [Git Basics](https://git-scm.com/book/en/v2/Getting-Started-Git-Basics)
        - [GitHub Guides](https://guides.github.com/)
        
        #### Testing & Debugging
        - [Python Testing](https://docs.python.org/3/library/test.html)
        - [Debugging with pdb](https://docs.python.org/3/library/pdb.html)
        """)

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center;'>
        <h3 style='color: #666;'>📱 Connect & Contribute</h3>
        <p>Found a bug? Have a feature request? Want to contribute?</p>
        <p>Visit our <a href="https://github.com/yourusername/todo-app">GitHub repository</a> or reach out to the community!</p>
    </div>
    """, unsafe_allow_html=True)

    # Copyright footer
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <small>© 2024 Smart Todo List App. Made with ❤️ using Streamlit.</small>
    </div>
    """, unsafe_allow_html=True) 