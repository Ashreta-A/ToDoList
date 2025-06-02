try:
    todo.get('completed', False)  # instead of todo['completed']
except Exception as e:
    st.error(f"Error message: {str(e)}")

if total_count > 0:  # prevent division by zero
    progress = completed_count / total_count

if not st.session_state.notification_thread_running:
    # start thread

