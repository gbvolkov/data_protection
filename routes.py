from flask import Blueprint, render_template, request, session, redirect, url_for
from llm import generate_answer
from anonimizer import TextProcessor, anonimizer_factory

main_bp = Blueprint('main', __name__)
#anonimizer, deanonimizer = anonimizer_factory()
processor = TextProcessor()

# Make sure you have set:
# app.secret_key = "a random secret string"

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    data = {
        'system_prompt': None,
        'user_request': None,
        'anonymized_request': None,
        'llm_response': None,
        'dean_response': None
    }

    if request.method == 'POST':
        action = request.form.get('action')
        data['system_prompt']       = request.form.get('system_prompt', '')
        data['user_request']        = request.form.get('user_request', '')
        data['anonymized_request']  = request.form.get('anonymized_request', '')

        if action == 'anonymize':
            # anonymize and stash the entities in the session
            anonymized_request = processor.anonimize(data['user_request'])
            data['anonymized_request'] = anonymized_request
            #session['anonymized_request'] = anonymized_request

        elif action == 'go':
            # fetch the stored entities
            anonymized_request = data['anonymized_request']
            if anonymized_request is None or anonymized_request == "":
                # nothing to de‐anonymize
                return redirect(url_for('main.index'))

            # call your LLM on the already-anonymized text
            answer = generate_answer(data['system_prompt'], anonymized_request)
            # de-anonymize using the same entity map
            dean_resp = processor.deanonimize(answer)

            data['llm_response']  = answer
            data['dean_response'] = dean_resp


    return render_template('index.html', **data)
