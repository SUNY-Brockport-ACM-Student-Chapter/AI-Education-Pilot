import streamlit as st
from database.database import (get_ai_feedback, get_student_answers,
                               insert_ai_feedback, insert_student_answer, 
                               get_current_attempt, get_or_create_student, 
                               update_student_attempt)
from utils import (get_feedback, get_or_create_chroma_collection,
                   get_relevant_content, load_questions_and_answers)

def first_attempt_flow(collection, questions, answers, ai_client):
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {q_id: "" for q_id in questions}
    if "feedbacks" not in st.session_state:
        st.session_state.feedbacks = {q_id: "" for q_id in questions}
    if "current_question" not in st.session_state:
        st.session_state.current_question = list(questions.keys())[0]
    if "submitted" not in st.session_state:
        st.session_state.submitted = False

     # Sidebar for question navigation
    with st.sidebar:
        st.title("Question Navigation")
        for q_id in questions:
            if st.button(f"Question {q_id}", key=f"nav_{q_id}"):
                st.session_state.current_question = q_id

    if not st.session_state.submitted:
        # Display current question
        current_q_id = st.session_state.current_question
        st.markdown(f"<p class='big-font'>Question {current_q_id}</p>", unsafe_allow_html=True)
        st.write(questions[current_q_id])

        # Text area for user answer
        user_answer = st.text_area(
            "Your answer:",
            value=st.session_state.user_answers[current_q_id],
            key=f"answer_{current_q_id}",
        )

        # Save answer button
        if st.button("Save Answer"):
            st.session_state.user_answers[current_q_id] = user_answer
            insert_student_answer(st.session_state.student_id, current_q_id, user_answer, attempt=1)
            st.success("Answer saved!")

        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Previous Question"):
                current_index = list(questions.keys()).index(current_q_id)
                if current_index > 0:
                    st.session_state.current_question = list(questions.keys())[current_index - 1]
                    st.rerun()
        with col2:
            if st.button("Next Question"):
                current_index = list(questions.keys()).index(current_q_id)
                if current_index < len(questions) - 1:
                    st.session_state.current_question = list(questions.keys())[current_index + 1]
                    st.rerun()

        # Submit all button
        if st.button("Submit All Answers"):
            st.session_state.submitted = True
            st.session_state.current_attempt = 2
            update_student_attempt(st.session_state.student_id, 2)
            st.success("All answers submitted. Generating AI feedback...")
            st.rerun()

    else:
        # Display all questions, answers, and generate feedback
        st.markdown("<h2 style='color: #215732;'>Submission Summary</h2>", unsafe_allow_html=True)

        for q_id, question in questions.items():
            st.markdown(f"<p class='big-font'>Question {q_id}</p>", unsafe_allow_html=True)
            st.write(question)
            st.write("Your Answer:")
            st.write(st.session_state.user_answers[q_id])

            if not st.session_state.feedbacks[q_id]:
                with st.spinner("Generating AI feedback..."):
                    relevant_content = get_relevant_content(
                        collection,
                        st.session_state.user_answers[q_id],
                        answers[q_id],
                        question,
                    )
                    feedback = get_feedback(
                        ai_client,
                        st.session_state.user_answers[q_id],
                        question,
                        relevant_content,
                        answers[q_id],
                    )
                    st.session_state.feedbacks[q_id] = feedback
                    insert_ai_feedback(st.session_state.student_id, feedback)

            st.markdown("**AI Feedback:**")
            st.write(st.session_state.feedbacks[q_id])
            st.markdown("---")

        st.write("You have completed the first attempt. You can now close the window and return later for your second attempt, or start your second attempt now.")
        if st.button("Start Second Attempt"):
            for key in ["user_answers", "feedbacks", "current_question", "submitted"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

def second_attempt_flow(questions):
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {q_id: "" for q_id in questions}
    if "current_question" not in st.session_state:
        st.session_state.current_question = list(questions.keys())[0]
    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    st.write("This is your second assessment attempt, your submitted answers will be final.")

     # Sidebar for question navigation
    with st.sidebar:
        st.title("Question Navigation")
        for q_id in questions:
            if st.button(f"Question {q_id}", key=f"nav_{q_id}"):
                st.session_state.current_question = q_id

    if not st.session_state.submitted:
        current_q_id = st.session_state.current_question
        st.markdown(f"<p class='big-font'>Question {current_q_id}</p>", unsafe_allow_html=True)
        st.write(questions[current_q_id])

        user_answer = st.text_area("Your answer:", value=st.session_state.user_answers[current_q_id], key=f"second_attempt_{current_q_id}")

        if st.button("Save Answer"):
            st.session_state.user_answers[current_q_id] = user_answer
            insert_student_answer(st.session_state.student_id, current_q_id, user_answer, attempt=2)
            st.success("Answer saved!")

        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Previous Question"):
                current_index = list(questions.keys()).index(current_q_id)
                if current_index > 0:
                    st.session_state.current_question = list(questions.keys())[current_index - 1]
                    st.rerun()
        with col2:
            if st.button("Next Question"):
                current_index = list(questions.keys()).index(current_q_id)
                if current_index < len(questions) - 1:
                    st.session_state.current_question = list(questions.keys())[current_index + 1]
                    st.rerun()

        if st.button("Submit All Answers"):
            st.session_state.submitted = True
            st.session_state.current_attempt = 3
            update_student_attempt(st.session_state.student_id, 3)
            st.success("All answers for the second attempt have been submitted. You have completed the assessment.")
            st.rerun()
    else:
        st.write("You have completed both attempts of the assessment.")

def main(collection, questions_fp, ai_client):
    # Brockport green color scheme
    st.markdown(
        """
    <style>
    .big-font {
        font-size: 20px !important;
        font-weight: bold;
        color: #00533E;
    }
    .stButton>button {
        background-color: #00533E;
        color: white;
    }
    .stTextInput>div>div>input {
        border-color: #00533E;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.title("SUNY Brockport Student Assessment Feedback System")

    if "student_id" not in st.session_state:
        st.session_state.student_id = None
    if "current_attempt" not in st.session_state:
        st.session_state.current_attempt = None

    questions, answers = load_questions_and_answers(questions_fp)

    # Input for Banner ID
    if st.session_state.student_id is None:
        banner_id = st.text_input("Enter the last four of your Banner ID:")
        if st.button("Submit Banner ID"):
            if banner_id:
                student_id, current_attempt, is_new_student = get_or_create_student(banner_id)
                st.session_state.student_id = student_id
                st.session_state.current_attempt = current_attempt
                if is_new_student:
                    st.success(f"New student record created. You are starting attempt 1.")
                    st.button("Start Test")
                    return
                    
                else:
                    st.success(f"Returning student found. You are on attempt {current_attempt}.")
                    st.button("Start Test")
                    return
                    
            else:
                st.error("Please enter a valid Banner ID.")
        return
    
    # Display current attempt
    st.write(f"Current attempt: {st.session_state.current_attempt}")
    # Handle different attempts
    if st.session_state.current_attempt == 1:
        first_attempt_flow(collection, questions, answers, ai_client)
    elif st.session_state.current_attempt == 2:
        if "submitted" in st.session_state and st.session_state.submitted:
            # If the first attempt was just submitted, show the feedback
            first_attempt_flow(collection, questions, answers, ai_client)
        else:
            # Otherwise, start the second attempt
            second_attempt_flow(questions)
    else:
        st.write("You have completed both attempts of the assessment.")