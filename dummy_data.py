import pandas as pd

def get_dummy_seminars():
    """Returns a DataFrame of dummy seminar events."""
    data = [
        {
            "Seminar Title": "Introduction to Machine Learning",
            "Date": "2025-11-10",
            "Time": "10:00 AM",
            "Presenter Name(s)": "Dr. Alex Greyson",
            "Seminar Description": "A foundational course on the core concepts of machine learning, including supervised and unsupervised learning.",
            "Google Meet Link": "https://meet.google.com/fake-link-one",
            "Google Slides Link": "https://docs.google.com/presentation/d/1Pw-yvOblXeGqAKtJ8smB__JuWQNG7N_P/edit?usp=sharing"
        },
        {
            "Seminar Title": "Advanced Python for Data Science",
            "Date": "2025-11-12",
            "Time": "2:00 PM",
            "Presenter Name(s)": "Ms. Brenda Smith",
            "Seminar Description": "Explore advanced Python libraries like Pandas, NumPy, and Scikit-learn for efficient data manipulation and analysis.",
            "Google Meet Link": "https://meet.google.com/fake-link-two",
            "Google Slides Link": "https://docs.google.com/presentation/d/1Pw-yvOblXeGqAKtJ8smB__JuWQNG7N_P/edit?usp=sharing"
        },
        {
            "Seminar Title": "The Future of Artificial Intelligence",
            "Date": "2025-11-15",
            "Time": "11:00 AM",
            "Presenter Name(s)": "Prof. Charles Xavier",
            "Seminar Description": "A guest lecture discussing the future trends, ethical considerations, and potential impact of AI on society.",
            "Google Meet Link": "https://meet.google.com/fake-link-three",
            "Google Slides Link": "https://docs.google.com/presentation/d/1Pw-yvOblXeGqAKtJ8smB__JuWQNG7N_P/edit?usp=sharing"
        },
        {
            "Seminar Title": "Web Development with React",
            "Date": "2025-11-18",
            "Time": "3:00 PM",
            "Presenter Name(s)": "Mr. David Wu",
            "Seminar Description": "Learn the fundamentals of building modern, interactive web applications using the React library.",
            "Google Meet Link": "https://meet.google.com/fake-link-four",
            "Google Slides Link": "https://docs.google.com/presentation/d/1Pw-yvOblXeGqAKtJ8smB__JuWQNG7N_P/edit?usp=sharing"
        }
    ]
    return pd.DataFrame(data)

def get_dummy_users():
    """Returns a DataFrame of dummy users."""
    data = [
        {
            "Phone(login)": "1234567890",
            "FullName": "John Doe",
            "Role": "Student",
            "EnrolledSeminars": "Introduction to Machine Learning,The Future of Artificial Intelligence"
        },
        {
            "Phone(login)": "0987654321",
            "FullName": "Jane Smith",
            "Role": "Lead",
            "EnrolledSeminars": "Advanced Python for Data Science"
        }
    ]
    return pd.DataFrame(data)
