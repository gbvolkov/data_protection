from flask import Blueprint, render_template, request
#from anon import anonimize
from llm import generate_answer
from anonimizer import anonimizer_factory

main_bp = Blueprint('main', __name__)

anonimizer, deanonimizer = anonimizer_factory()

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
        data['system_prompt'] = request.form.get('system_prompt', '')
        data['user_request'] = request.form.get('user_request', '')

        # Always anonymize before further actions
        data['anonymized_request'], entities = anonimizer(data['user_request'])

        if action == 'go':
            def process_text(system_prompt, user_request):
                answer=generate_answer(system_prompt, user_request)
                dean_resp = deanonimizer(answer, entities)
                return dean_resp
            data['llm_response'], data['dean_response'] = process_text(
                data['system_prompt'], data['anonymized_request']
            )

    return render_template('index.html', **data)