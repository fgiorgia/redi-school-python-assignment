import json
import os
import random
from typing import TypedDict


def green(str_to_color: str) -> str:
    __GREEN_CODE__ = "\033[92m"
    __END_CODE__ = "\033[0m"
    return f"{__GREEN_CODE__}{str_to_color}{__END_CODE__}"


class UserInormationDict(TypedDict):
    name: str
    age: int


class UserInformation:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    def get_user_information_dict(self) -> UserInormationDict:
        return {"name": self.name, "age": self.age}


class BaseQuizElement:
    def __init__(self, content: str) -> None:
        self.content = content

    def __str__(self) -> str:
        return self.content


class Question(BaseQuizElement):
    def __init__(self, content: str) -> None:
        super().__init__(content)


class Answer(BaseQuizElement):
    def __init__(self, content: str, is_correct: bool) -> None:
        super().__init__(content)
        self.is_correct = is_correct

    def get_is_correct(self):
        return self.is_correct


class UserAnswersDict(TypedDict):
    question: str
    answers: list[str]
    user_answer: str
    is_correct: bool


class UserDataDict(TypedDict):
    user_information: UserInormationDict
    user_answers: list[UserAnswersDict]
    user_score: int


class QuizItem:
    def __init__(self, question: Question, answers: list[Answer]) -> None:
        self.question = question
        self.answers = answers

    def get_question(self):
        return self.question

    def get_answers(self):
        return self.answers


class Quiz:
    def __init__(self) -> None:
        self.quiz_list: list[QuizItem] = []
        self.load_questions()
        self.user_answers: list[UserAnswersDict] = []
        self.user_score = 0

    def load_questions(self):
        quiz_list_file_path = "quiz_list.json"
        with open(quiz_list_file_path) as quiz_list_file:
            quiz_list_file_content = json.load(quiz_list_file)

        for quiz in quiz_list_file_content:
            question = Question(quiz["question"])
            answers: list[Answer] = []
            for indx, an_answer_option in enumerate(quiz["answer_options"]):
                an_answer = Answer(an_answer_option, indx == quiz["correct_answer"])
                answers.append(an_answer)

            quiz_item = QuizItem(question, answers)
            self.quiz_list.append(quiz_item)

    def is_valid_quiz_answer(self, user_input: str, n_answers: int) -> bool:
        if not user_input.isdigit():
            return False

        user_input_int = int(user_input)
        if user_input_int <= 0 or user_input_int > n_answers:
            return False

        return True

    def ask_user_information(self):
        name = input("Enter your name: ")
        age = input("Enter your age: ")
        age_int = 0

        while True:
            if age.isdigit():
                age_int = int(age)
                if 0 <= age_int <= 125:
                    break

            age = input("Invalid answer! Please, enter your age again: ")

        self.user_information = UserInformation(name, age_int)

    def add_user_answer(
        self, question: Question, answers: list[Answer], user_answer: Answer
    ):
        self.user_answers.append(
            {
                "question": str(question),
                "answers": [str(a) for a in answers],
                "user_answer": str(user_answer),
                "is_correct": user_answer.get_is_correct(),
            }
        )

    def save_user_answers(self):
        user_data_path = "users_data.json"
        file_exists = os.path.exists(user_data_path)
        if file_exists:
            with open(user_data_path, mode="r") as user_data_file:
                users_data: list[UserDataDict] = json.load(user_data_file)
        else:
            users_data: list[UserDataDict] = []

        with open(user_data_path, mode="w") as user_data_file:
            users_data.append(
                {
                    "user_information": self.user_information.get_user_information_dict(),
                    "user_answers": self.user_answers,
                    "user_score": self.user_score,
                }
            )
            json.dump(
                users_data,
                user_data_file,
                indent=2,
            )

    def run(self):
        print("\nWelcome to Online Quiz System\n")
        self.user_score = 0

        self.ask_user_information()
        print()

        random_quiz_list = random.sample(self.quiz_list, len(self.quiz_list))
        for indx_q, quiz_item in enumerate(random_quiz_list):
            print(f"{indx_q + 1}/{len(random_quiz_list)}")
            print(quiz_item.get_question())
            random_answers_list = random.sample(
                quiz_item.get_answers(), len(quiz_item.get_answers())
            )
            for indx, an_answer in enumerate(random_answers_list):
                print(indx + 1, an_answer)

            user_answer_input = input("Enter your answer: ")
            valid_input = False
            while not valid_input:
                valid_input = self.is_valid_quiz_answer(
                    user_answer_input, len(random_answers_list)
                )
                if not valid_input:
                    user_answer_input = input(
                        "Invalid answer! Please, enter your answer again: "
                    )

            indx_answer = int(user_answer_input) - 1
            user_answer = random_answers_list[indx_answer]

            if user_answer.get_is_correct():
                self.user_score += 1
                print("\nBravo! Your answer is correct!\n")
            else:
                correct_answer = [a for a in random_answers_list if a.get_is_correct()][
                    0
                ]
                print(
                    f"\nNope, the correct answer was '{str(correct_answer).capitalize()}'.",
                    "Now you know a new thing!\n",
                )

            self.add_user_answer(
                quiz_item.get_question(), random_answers_list, user_answer
            )

        self.save_user_answers()

        print(
            f"Correct answers: {self.user_score} out of {len(self.quiz_list)}",
            f"{round(self.user_score / len(self.quiz_list) * 100)}% of accuracy",
            f"Your total score is {green(str(self.user_score))}",
            sep="\n",
            end="\n\n",
        )


def main():
    quiz = Quiz()
    quiz.run()


if __name__ == "__main__":
    main()
