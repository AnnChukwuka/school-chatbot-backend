# scripts/intent_handler.py
import string
import datetime
import firebase_admin
from firebase_admin import firestore
from config import firebase_config

db = firestore.client()


def save_chat_message(session_id: str, text: str, sender: str):
    db.collection("chats").document(session_id).collection("messages").add({
        "text": text,
        "sender": sender,
        "timestamp": datetime.datetime.utcnow()
    })

def preprocess_input(user_input):
    user_input = user_input.lower().strip()
    user_input = user_input.translate(str.maketrans('', '', string.punctuation))
    return user_input.split()

def log_unknown_query(user_input: str):
    db.collection("unknown_queries").add({
        "message": user_input,
        "timestamp": datetime.datetime.utcnow(),
        "handled": False
    })

def detect_intent(user_input):
    tokens = preprocess_input(user_input)
    user_input_text = ' '.join(tokens)

    # Quick keyword detection
    intent_keywords = {
        "greeting": ["hello", "hi", "hey", "whats", "yo", "howdy", "hiya", "greetings", "sup", "popping", "morning", "afternoon", "evening"],
        "thanks": ["thank", "thanks", "thankyou", "appreciate", "ok", "appreciated"],
        "goodbye": ["bye", "goodbye", "see", "later", "farewell"]
    }

    for intent, keywords in intent_keywords.items():
        if any(word in tokens for word in keywords):
            return intent

    # Check for known phrases
    phrase_keywords = {
        "academic_calendar": ["academic calendar", "show me the academic calendar", "when will final exam starting", "when is exam starting", "when is school resuming", "when does semester start", "school break dates", "is tomorrow school", "when is public holiday", "is there holiday tomorrow", "when is next school holiday"],
        "grading_system": ["what is the grading system", "grading system", "tell me about the grading"],
        "registration_office": ["registration office", "where is the registration office"],
        "hostel_application": ["hostel requirement", "apply for hostel", "how to get hostel"],
        "ois_portal": ["check my ois portal", "login to ois", "open ois portal"],
        "school_debts": ["check my school debts", "how do i check school debts", "school fees due"],
        "it_office": ["where is the it office", "it department location"],
        "ID_status": ["how can i get my id", "where can i get student card", "how do i get id card", "where is can i apply for id card"],
        "login_help": ["how to log in to my account", "password reset"],
        "cafeteria_hours": ["bau cafeteria closes", "closing time for the cafeteria", "canteen closing time"],
        "scholarship_info": ["how can i qualify for scholarship", "am i qualified for scholarship", "scholarship info"],
        "financial_info": ["check my financial information", "how much debt do i have", "my finance status"],
        "cyprus_lifestyle": ["general atmosphere of the cyprus", "student life in cyprus", "things to do in cyprus"],
        "bus_schedule": ["bus schedule", "transport timetable", "how do i get to campus"],
        "internship_policy": ["internship policy", "how do internships work", "internship rules"],
        "transfer_exemption": ["transfer exemption", "course exemption rules", "transfer policy"],
        "graduate_regulations": ["graduate rules", "masters program structure", "phd requirements"],
        "bau_info": ["what is bau", "bau", "bau university", "about bau", "what does bau stand for", "what is the full meaning of bau", "bau is abbrevition whats"],
        "undergrad_duration": ["how long is undergraduate", "undergraduate duration", "undergraduate time frame"],
        "tuition_fees": ["tuition fees", "how much is school fees", "cost of studying at bau"],
        "residence_permit": ["how can i start my resident permit", "how i start my resident permit", "how do i get my resident permit", "what is the muharcet process", "how can i sign up for muhaceret"],
        "student_letter": ["how do i get student letter", "where can i get student letter", "do i have to pay for student letter"],
        "lecture_timetable": ["when is my class", "class schedule", "when is my next lecture", "show timetable"],
        "course_registration": ["how do i register courses", "course selection", "course registration guide"],
        "exam_results": ["how do i check my results", "when will results be out", "check exam grades"],
        "contact_student_affairs": ["student affairs contact", "how can i reach the dean of student", "how to contact the student dean office", "student dean email address", "dean of student contact", "contact the dean of students", "dean of student phone number"],
        "contact_registration": ["registration office contact", "contact registrar", "registration office line", "registration office email or phone number"],
        "contact_counseling": ["counseling services", "contact therapist", "how to reach school counselor", "can you give me the contact of the school therapist"]
    }

    for intent, phrases in phrase_keywords.items():
        if any(phrase in user_input_text for phrase in phrases):
            return intent

    log_unknown_query(user_input)
    return "unknown"



intent_responses = {
    "greeting": "Hey there! How can I assist you today? 😊",
    "thanks": "You're welcome! Let me know if you have more questions.",
    "goodbye": "Goodbye! Have a great day! 👋",
    "hostel_application": "To apply for hostel accommodation, visit the student affairs office or apply online via the housing portal. Make sure you’ve completed enrollment.",
    "grading_system": "Grades are based on both absolute and relative evaluation. Letter grades range from A (4.00) to F (0.00). Minimum for pass is typically D or C depending on course type. Final exams must account for at least 40% of the total score.",
    "registration_office": "The registrar’s office is located on the 1st floor of the main admin building, opposite the student affairs office. Open 9AM–5PM weekdays.",
    "academic_calendar": "To get accurate information on this you should view the full academic calendar https://baucyprus.edu.tr/academic-calendar/. It includes semester dates, breaks, and key deadlines.",
    "ois_portal": "You can access your OIS portal at https://ois.baucyprus.edu.tr/auth/login. Use your student ID and password to log in.",
    "school_debts": "To check your school debts or fee balance, go to the Finance tab in your OIS portal or contact the bursary.",
    "it_office": "The IT office is located in on the ground floor at the B-Block of the Admin Block. They handle student emails, portal access, and technical issues.",
    "oin_status": ". You can verify your if your student card is ready at the registration office.",
    "login_help": "You can reset your password via the OIS login page. Click 'Forgot Password' and follow the instructions.",
    "cafeteria_hours": "The BAU Gastro cafeteria usually opens at 8:00 Am and  closes around 7:00 PM. Hours may vary on weekends or holidays.",
    "scholarship_info": "Scholarship eligibility is based on GPA, financial need, and program. Visit the scholarships page on the BAU website.If you Qualify, then visit the Dean at the student affairs office",
    "financial_info": "Log into your OIS portal and click on the third icon and go to 'Financial Information' to view your fee statements and balances.",
    "cyprus_lifestyle": "Cyprus offers a vibrant student life, beautiful beaches, local restaurants, and cultural events near campus.",
    "bus_schedule": "Bus schedules are posted on the Bau Instagram page, you can check for it on the Instagram story too and are also available at the security office.",
    "universal_income": "This is a broader economic question. For now, no policy on universal income is being implemented at BAU.",
    "internship_policy": "Internships are mandatory for many programs. Students must secure their placement, fill insurance and evaluation forms, and submit internship reports. Failure to submit on time may result in failing the internship.",
    "transfer_exemption": "Transfer and exemption procedures require submitting transcripts, course descriptions, and a formal petition. Courses must match at least 70% in content and credits to be eligible.",
    "graduate_regulations": "Graduate programs require a bachelor's degree, sometimes ALES, GPA ≥ 3.0, and may include thesis or non-thesis options. Thesis tracks involve 120–240 ECTS, defense, and committee evaluation.",
    "bau_info": "BAU stands for Bahçeşehir Cyprus University. It's a private higher education institution located in Nicosia, Northern Cyprus. It is part of the global BAU Global network, offering undergraduate and graduate programs in English and Turkish, with a focus on international standards, academic excellence, and innovation. You can follow the link to visit the school website and learn more https://baucyprus.edu.tr/",
    "undergrad_duration": "Undergraduate programs typically last 4 years. However, some programs may be 5 or 6 years. Maximum allowed duration is 7–9 years depending on the program.",
    "tuition_fees": "Tuition is set annually by the Board of Trustees. Fees vary by program and student status. Payments can be made in full or installments. Financial obligations must be met to complete enrollment.",
    "residence_permit": "To apply for your resident permit you have to have finished your course registration for the semester, then you can login to this website https://permissions.gov.ct.tr/login. if you have no previous permit on the Island you click on sign up and fill the information same as  it is on your ois and sign up. ",
    "student_letter": "To acquire you have to pay $5 or (TL equivalent)  through your ois payment portal or cash to to the accounting office, Then go to the registration office with the receipt to  get your Student Letter",
    "lecture_timetable": "To see your timetable you should head to your ois, IMAGE",
    "contact_student_affairs": "You  can contact the Dean of Students via email: Students.dean@baucyprus.edu.tr or Phone: +90 548 847 88 74",
    "contact_registration": "",
    "contact_advisor": "To contact your advisor, scroll down in your OIS portal to the *Courses* section. " "You’ll see your advisor’s name, email, and office number. Tap the image below to locate it easily:",

    "contact_counseling": " +905488692685 You can reach the school psychologist, Ibrahim Ray, at +90 548 869 2685. " "Contact him directly to book a counseling appointment. ",
}



