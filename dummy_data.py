import pandas as pd

def get_dummy_seminars():
    """Returns a DataFrame of dummy seminar events."""
    data = {
        'Seminar Title': [
            'Introduction to Machine Learning',
            'Advanced Python for Data Science',
            'The Future of Quantum Computing',
            'Web Development with React',
            'Cybersecurity Best Practices'
        ],
        'Date': [
            '2025-11-10',
            '2025-11-15',
            '2025-11-20',
            '2025-11-25',
            '2025-12-01'
        ],
        'Time': [
            '14:00',
            '16:30',
            '11:00',
            '15:00',
            '10:00'
        ],
        'Presenter Name(s)': [
            'Dr. Anjali Sharma',
            'Rohan Verma',
            'Prof. Ken Thompson',
            'Priya Singh',
            'Amit Kumar'
        ],
        'Seminar Description': [
            'A beginner-friendly session covering the core concepts of machine learning, including supervised and unsupervised learning.',
            'Deep dive into advanced Python libraries like NumPy, Pandas, and Scikit-learn for efficient data manipulation and analysis.',
            'An exciting look into the principles of quantum mechanics and how they are being applied to build the next generation of computers.',
            'Learn how to build modern, interactive user interfaces for web applications using the React JavaScript library.',
            'Essential tips and strategies for protecting your digital assets from common cyber threats in today\'s landscape.'
        ],
        'WhatsApp Link': [
            'https://chat.whatsapp.com/samplelink1',
            'https://chat.whatsapp.com/samplelink2',
            'https://chat.whatsapp.com/samplelink3',
            'https://chat.whatsapp.com/samplelink4',
            'https://chat.whatsapp.com/samplelink5'
        ],
        'Google Meet / Other Link': [
            'https://meet.google.com/aim-ymsn-daw',
            'https://meet.google.com/sample-link-2',
            'https://meet.google.com/sample-link-3',
            'https://meet.google.com/sample-link-4',
            'https://meet.google.com/sample-link-5'
        ],
        'Google Slides Link': [
            'https://docs.google.com/presentation/d/1Pw-yvOblXeGqAKtJ8smB__JuWQNG7N_P/edit?usp=sharing',
            'https://docs.google.com/presentation/d/sample-slides-link-2/edit',
            'https://docs.google.com/presentation/d/sample-slides-link-3/edit',
            'https://docs.google.com/presentation/d/sample-slides-link-4/edit',
            'https://docs.google.com/presentation/d/sample-slides-link-5/edit'
        ],
        'Status': [
            'Approved',
            'Approved',
            'Approved',
            'Pending',
            'Approved'
        ]
    }
    return pd.DataFrame(data)
