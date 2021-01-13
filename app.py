from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey as survey

# key names will use to store some things in the session;
# put here as constants so we're guaranteed to be consistent in
# our spelling of these

RESPONSES_KEY = "responses"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'blablabla123'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)


@app.route("/")
def show_survey_start():
    return render_template("survey_start.html", survey=survey)


@app.route("/begin", methods=["POST"])
def start_survey():
    """starting with zero responses"""
    session[RESPONSES_KEY] = []  # NOTE: starting with no responses
    return redirect("/questions/0")  # NOTE: go to the first question


@app.route("/answer", methods=["POST"])
def handle_question():
    """Save response and redirect to next question."""

    # get the response choice
    # NOTE: go to the first question and get the answer
    choice = request.form['answer']

    # add this response to the session
    # NOTE: declare a variable that is our session keys
    responses = session[RESPONSES_KEY]
    responses.append(choice)  # NOTE: add each choice to the list of responses
    session[RESPONSES_KEY] = responses  # NOTE: go to the first question

    if (len(responses) == len(survey.questions)):
        # They've answered all the questions! Thank them.
        # NOTE: redirecting to last thank you page
        return redirect("/complete")
    else:
        return redirect(f"/questions/{len(responses)}")


@app.route("/questions/<int:questID>")
def show_question(questID):
    """Display current question."""
    responses = session.get(RESPONSES_KEY)

    if (responses is None):
        return redirect("/")  # NOTE: trying to access question page too soon

    if (len(responses) == len(survey.questions)):
        # NOTE: complete page if they answered all questions
        return redirect("/complete")

    if (len(responses) != questID):
        # Trying to access questions out of order.
        flash(f"Invalid question id: {questID}.")
        return redirect(f"/questions/{len(responses)}")

    question = survey.questions[questID]
    return render_template(
        "question.html", question_num=questID, question=question)


@app.route("/complete")
def complete():
    """Survey complete. Show completion page."""

    return render_template("completion.html")
