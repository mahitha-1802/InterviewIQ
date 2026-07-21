import os
import json
import warnings

try:
    from google import genai as _genai_new
    _USE_NEW_SDK = True
except ImportError:
    _USE_NEW_SDK = False
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        import google.generativeai as genai

class GeminiService:
    _DEFAULT_API_KEY = None

    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or self._DEFAULT_API_KEY
        self.client = None
        if self.api_key:
            try:
                if _USE_NEW_SDK:
                    self.client = _genai_new.Client(api_key=self.api_key)
                    self._sdk = "new"
                else:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", FutureWarning)
                        genai.configure(api_key=self.api_key)
                        self.client = genai.GenerativeModel("gemini-1.5-flash")
                    self._sdk = "old"
            except Exception:
                self.client = None

    def has_active_client(self):
        return self.client is not None

    def _call_gemini(self, prompt):
        """Call Gemini and return the JSON-parsed response dict. Raises on failure."""
        if _USE_NEW_SDK:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text.strip())
        else:
            response = self.client.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text.strip())

    def generate_question(self, category, experience, difficulty, history):
        if not self.has_active_client():
            return self._mock_question(category, experience, difficulty, len(history))

        prompt = f"""
        Role: Senior Technical Interviewer

        You are conducting a technical interview on the topic: "{category}".
        Experience Level of Candidate: {experience}
        Target Difficulty: {difficulty}
        Previous Questions Already Asked: {json.dumps(history)}

        Generate the NEXT single interview question for the candidate.
        Rules:
        - The question MUST be specifically about "{category}" — do not drift to unrelated topics.
        - If previous questions list is empty, start with a foundational/introductory question.
        - Do NOT repeat any of the previous questions or topics already covered.
        - Adjust depth and complexity to match a {experience} level candidate at {difficulty} difficulty.
        - The question should be open-ended and encourage a detailed technical answer.

        Return the result STRICTLY as a JSON object with exactly two keys:
        - "question": string — the full interview question text
        - "difficulty": string — one of: Easy, Medium, Hard, Expert (your own assessment of this specific question)

        JSON only. No markdown, no code fences, no extra text.
        """
        try:
            data = self._call_gemini(prompt)
            return data.get("question"), data.get("difficulty", difficulty)
        except Exception:
            return self._mock_question(category, experience, difficulty, len(history))

    def evaluate_answer(self, question, answer):
        if not self.has_active_client() or not answer.strip():
            return self._mock_evaluation(question, answer)

        prompt = f"""
        Role: Expert Interview Evaluator
        Question Asked: {question}
        Candidate Answer: {answer}

        Evaluate this answer on the following metrics:
        - Technical Accuracy (out of 100)
        - Communication (out of 100)
        - Completeness (out of 100)
        - Confidence (out of 100, based on phrasing and vocabulary)
        - Grammar (out of 100)
        - Professionalism (out of 100)
        - Overall Score (out of 100)

        Also provide a short written feedback and specific suggestions for improvement.
        Return the response strictly as a JSON object with these keys:
        - "technical_score": int
        - "communication_score": int
        - "completeness_score": int
        - "confidence_score": int
        - "grammar_score": int
        - "professionalism_score": int
        - "overall_score": int
        
        - "feedback_text": string
        - "suggestion_text": string

        JSON format only. Do not include markdown code block syntax.
        """
        try:
            data = self._call_gemini(prompt)
            return data
        except Exception:
            return self._mock_evaluation(question, answer)

    def compile_final_report(self, category, experience, difficulty, QA_history):
        if not self.has_active_client():
            return self._mock_report(category, experience, difficulty, QA_history)

        prompt = f"""
        Role: Hiring Committee Lead
        Category: {category}
        Experience: {experience}
        Starting Difficulty: {difficulty}
        QA History: {json.dumps(QA_history)}

        Review the candidate's answers and evaluations to generate a final hiring report.
        Compute the aggregate score metrics out of 100:
        - Technical
        - Communication
        - Problem Solving
        - Confidence
        - Grammar
        - Professionalism
        - Overall Score

        Generate:
        - Strengths: list of strings (3 items)
        - Weaknesses: list of strings (3 items)
        - Topics to Improve: list of strings (3 items)
        - Recommended Learning Path: list of strings (3 steps)
        - Hiring Recommendation: string (Strong Hire, Hire, Borderline, No Hire)
        - Summary: detailed summary text

        Return the response strictly as a JSON object with these keys:
        - "overall_score": int
        - "technical_score": int
        - "communication_score": int
        - "problem_solving_score": int
        - "confidence_score": int
        - "grammar_score": int
        - "professionalism_score": int
        - "strengths": list of strings
        - "weaknesses": list of strings
        - "topics_to_improve": list of strings
        - "learning_path": list of strings
        - "hiring_recommendation": string
        - "summary": string

        JSON format only. Do not include markdown code block syntax.
        """
        try:
            data = self._call_gemini(prompt)
            return data
        except Exception:
            return self._mock_report(category, experience, difficulty, QA_history)

    def _mock_question(self, category, experience, difficulty, index):
        questions = {
            "Python": [
                "Can you explain the difference between a list and a tuple in Python, and when you would use one over the other?",
                "What are decorators in Python, and how would you implement a simple timing decorator?",
                "How does Python's memory management and garbage collection system work?",
                "Can you explain the global interpreter lock (GIL) and its implications on multi-threaded applications?",
                "How do you implement custom context managers using the generator-based syntax?",
                "What is the difference between deepcopy and shallow copy in the copy module?",
                "How do generators work in Python, and what is the difference between yield and return?",
                "Can you explain method resolution order (MRO) and the use of super() in multiple inheritance?",
                "What are *args and **kwargs, and how are they used in function definitions?",
                "What is the difference between multiprocessing and multithreading in Python, and when should you use each?"
            ],
            "Java": [
                "What is the difference between JVM, JRE, and JDK?",
                "Explain the differences between String, StringBuilder, and StringBuffer in Java.",
                "What is the difference between method overloading and method overriding?",
                "How does the Java garbage collection mechanism work, and what are the different memory areas (Heap, Stack, Metaspace)?",
                "Can you explain the difference between checked and unchecked exceptions in Java?",
                "How does Java handle multithreading, and what is the difference between extending Thread and implementing Runnable?",
                "What is the Java Collections Framework? Explain the difference between HashMap, HashSet, and ArrayList.",
                "What are Java 8 functional interfaces and Lambda expressions, and how do they work?",
                "Can you explain the 'volatile' keyword in Java and how it relates to thread memory visibility?",
                "What is serialization in Java, and how does the 'transient' keyword work?"
            ],
            "C#": [
                "What is the difference between managed and unmanaged code in .NET?",
                "Can you explain the difference between value types (structs) and reference types (classes) in C#?",
                "What are the differences between abstract classes and interfaces in C#?",
                "How does garbage collection work in .NET, and what is the role of the IDisposable interface?",
                "What are delegates and events in C#, and how do they differ from multicast delegates?",
                "Can you explain the difference between the 'ref' and 'out' keywords in C#?",
                "How do async and await work under the hood in C#, and what is a Task?",
                "What is LINQ, and can you explain the difference between deferred execution and immediate execution?",
                "What is boxing and unboxing in C#, and what are their performance implications?",
                "Can you explain reflection in C#, and what are some common use-cases or trade-offs?"
            ],
            "SQL": [
                "What is the difference between INNER JOIN, LEFT JOIN, and outer joins?",
                "Can you explain database indexing, and how it improves query performance?",
                "What are database transactions, and what does the ACID property stand for?",
                "How do window functions work, and can you provide an example of using ROW_NUMBER()?",
                "What is database normalization, and what is the difference between 2NF and 3NF?",
                "What is the difference between WHERE and HAVING clauses in SQL?",
                "Can you explain the difference between a clustered and a non-clustered index?",
                "How do database locks work, and what is the difference between shared and exclusive locks?",
                "What is a CTE (Common Table Expression), and when would you use a recursive CTE?",
                "How do you optimize a slow-running SQL query, and what tools or commands do you use?"
            ],
            "JavaScript": [
                "What is the difference between let, const, and var, and how does hoisting affect them?",
                "Can you explain the event loop, call stack, callback queue, and microtask queue in JavaScript?",
                "What are closures in JavaScript, and can you provide a practical use-case for them?",
                "How does prototypical inheritance work, and how does it differ from classical class inheritance?",
                "What is the difference between == and ===, and what is implicit coercion?",
                "Can you explain the difference between Promise.all, Promise.allSettled, Promise.any, and Promise.race?",
                "How does the 'this' keyword behave in JavaScript, and how do call, apply, and bind affect it?",
                "What are arrow functions, and how do they differ from regular function expressions?",
                "Can you explain event bubbling and capturing, and how event delegation works?",
                "What is the difference between debounce and throttle, and when would you use each?"
            ],
            "Full Stack": [
                "What is RESTful API design, and what are the best practices for structuring API endpoints?",
                "How do you handle user authentication and session management securely in a web application?",
                "What is CORS (Cross-Origin Resource Sharing), and how do you resolve CORS errors?",
                "Can you explain the difference between client-side rendering (CSR) and server-side rendering (SSR)?",
                "How do WebSockets differ from standard HTTP requests, and when should you use them?",
                "What is database migration, and why is it important in team development environments?",
                "How do you handle API rate limiting and prevent abuse on your servers?",
                "What are the common web security vulnerabilities (e.g., XSS, CSRF, SQL Injection) and how do you prevent them?",
                "Can you explain caching strategies, such as Redis caching, for scaling web applications?",
                "What is the difference between Monolithic and Microservices architectures, and what are the trade-offs?"
            ],
            "Machine Learning": [
                "What is the difference between supervised and unsupervised learning, and can you give examples of each?",
                "Can you explain the bias-variance trade-off and how it relates to underfitting and overfitting?",
                "How does gradient descent work, and what are the differences between batch, stochastic, and mini-batch gradient descent?",
                "What is regularization (L1/L2 or Lasso/Ridge), and how does it prevent overfitting?",
                "How do you handle imbalanced datasets in machine learning classification tasks?",
                "Can you explain the difference between precision, recall, and F1-score, and when to prioritize each?",
                "What is a random forest, and how does the ensemble method improve model accuracy?",
                "How does a neural network backpropagation algorithm work?",
                "What is cross-validation, and why is it preferred over a simple train/test split?",
                "Can you explain what feature engineering is and why it is critical to model performance?"
            ],
            "Data Science": [
                "What is the difference between correlation and causation, and how do you test for causation?",
                "Can you explain the Central Limit Theorem and why it is fundamental to statistics?",
                "How do you handle missing or corrupted data in a large dataset before analysis?",
                "What is A/B testing, and how do you determine if the results of an A/B test are statistically significant?",
                "Can you explain what p-value means and how it is used in hypothesis testing?",
                "What is the difference between structured and unstructured data, and how do you analyze the latter?",
                "How does principal component analysis (PCA) work, and when is dimensionality reduction useful?",
                "What are the assumptions of linear regression, and how do you check if they are met?",
                "How do you identify and handle outliers in a dataset?",
                "Can you explain the difference between SQL and NoSQL databases, and when a data scientist would prefer one over the other?"
            ],
            "Customer Service": [
                "How do you handle an extremely angry or frustrated customer on the phone or chat?",
                "Describe a time when you went above and beyond to solve a customer's issue. What was the outcome?",
                "What does 'active listening' mean to you in the context of customer support, and how do you practice it?",
                "How do you handle a situation where you don't know the answer to a customer's technical or product question?",
                "What is the difference between SLA (Service Level Agreement) and customer satisfaction (CSAT), and how do you prioritize them?",
                "How do you manage stress and maintain a positive attitude during a high-volume shift with back-to-back inquiries?",
                "If a customer is demanding a refund that goes against company policy, how do you handle the situation tactfully?",
                "What customer service tools (CRM, ticketing systems, telephony software) are you most familiar with?",
                "How do you handle multiple customer issues or tickets simultaneously without compromising quality?",
                "Why is customer feedback important, and how do you communicate customer issues back to product or management teams?"
            ],
            "Marketing": [
                "What is the difference between inbound and outbound marketing, and when is each most effective?",
                "How do you design and execute a successful email marketing campaign, and what key metrics do you track?",
                "Can you explain the concept of a marketing funnel and how content differs at each stage (TOFU, MOFU, BOFU)?",
                "How do you perform keyword research for SEO, and what tools do you use?",
                "What is CAC (Customer Acquisition Cost) and LTV (Lifetime Value), and how do they influence marketing budget decisions?",
                "Describe a marketing campaign you managed that failed. What did you learn and how did you adjust your strategy?",
                "How do you utilize social media analytics to optimize engagement and reach?",
                "What is A/B testing in marketing, and can you provide an example of something you tested and its impact?",
                "How do you align marketing goals with sales teams to ensure high-quality lead generation?",
                "What is your approach to branding and maintaining a consistent brand voice across multiple channels?"
            ],
            "Sales": [
                "How do you handle the common objection, 'Your price is too high'?",
                "Can you describe your process for qualifying a new lead or prospect?",
                "What is the difference between transactional selling and consultative/relationship selling?",
                "Describe a time you lost a major sales deal. What did you learn, and what would you do differently?",
                "How do you structure a cold call or cold email to maximize response and meeting booking rates?",
                "What strategies do you use to build long-term trust and relationships with key stakeholders?",
                "How do you handle rejection or a dry spell in sales without losing motivation?",
                "What CRM tools are you familiar with, and how do you keep your pipeline organized and up to date?",
                "Describe a situation where you had to negotiate contract terms. How did you arrive at a win-win outcome?",
                "How do you research a prospect and their company before making the first contact or pitch?"
            ],
            "HR": [
                "Can you describe a time when you had a conflict with a team member and how you resolved it?",
                "How do you prioritize your tasks when working under tight deadlines and competing priorities?",
                "Describe a major technical mistake you made in the past. How did you handle it and what did you learn?",
                "Why do you want to join our company, and what unique value do you bring to the team?",
                "How do you handle receiving negative feedback or constructive criticism from your peers or manager?",
                "Describe a time when you had to work with a difficult stakeholder or client. How did you ensure a successful outcome?",
                "What is your approach to learning new technologies or staying up-to-date in your field?",
                "Tell me about a time you went above and beyond your standard job duties to complete a project.",
                "How do you handle stress and pressure in a high-intensity work environment?",
                "Where do you see yourself in five years, and how does this role align with your career goals?"
            ]
        }
        default_questions = [
            f"What are the core principles of {category} development?",
            f"How do you handle error management and debugging in {category}?",
            f"Can you explain how state management is handled in {category}?",
            f"What design patterns do you commonly apply when working with {category}?",
            f"How would you optimize performance in a scale-heavy application using {category}?"
        ]
        list_to_use = questions.get(category, default_questions)
        q_idx = index % len(list_to_use)
        return list_to_use[q_idx], difficulty

    def _mock_evaluation(self, question, answer):
        score = 82
        return {
            "technical_score": score,
            "communication_score": score,
            "completeness_score": score,
            "confidence_score": score,
            "grammar_score": 85,
            "professionalism_score": 90,
            "overall_score": score,
            "feedback_text": "The candidate provided a responsive answer addressing the primary elements of the question.",
            "suggestion_text": "Try to incorporate more specific technical terms and code architectural patterns in your explanation."
        }

    def _mock_report(self, category, experience, difficulty, QA_history):
        scores = [q["overall_score"] for q in QA_history if "overall_score" in q]
        avg_score = int(sum(scores) / len(scores)) if scores else 75
        recommendation = "Hire" if avg_score >= 70 else "Borderline"
        if avg_score >= 85:
            recommendation = "Strong Hire"
        elif avg_score < 60:
            recommendation = "No Hire"

        return {
            "overall_score": avg_score,
            "technical_score": avg_score - 2,
            "communication_score": avg_score + 3,
            "problem_solving_score": avg_score - 1,
            "confidence_score": avg_score + 2,
            "grammar_score": 85,
            "professionalism_score": 88,
            "strengths": [
                f"Demonstrated good conceptual understanding of {category}.",
                "Clear communication skills and articulation of technical workflows.",
                "Structured approach to answering questions."
            ],
            "weaknesses": [
                "Could go into deeper architectural implementation details.",
                "Sometimes uses general explanations rather than specific algorithms.",
                "Occasional grammatical pauses."
            ],
            "topics_to_improve": [
                f"Advanced architectural patterns in {category}",
                "Concurrency and asynchronous execution",
                "Memory optimization and benchmarking methods"
            ],
            "learning_path": [
                "Read official documentation regarding intermediate to advanced features.",
                "Build practical sandbox projects leveraging custom structures.",
                "Perform code optimization analysis and profiling."
            ],
            "hiring_recommendation": recommendation,
            "summary": f"The candidate completed the {category} interview designed for a {experience} level developer. Overall performance indicates solid fundamentals with potential to scale technical design skills under mentorship."
        }
