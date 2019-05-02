from django.utils.crypto import get_random_string
import subprocess
from shutil import copyfile
import os


def request_input(question, options):
    print(f'{question} ({", ".join([option for option in options])})')
    while True:
        r = input()
        if r not in options:
            print('Digite uma resposta válida!')
        else:
            return r


def ask_user(name, title, required, default=None, next_questions={}):
    print()
    print(f'{title} {"(Opcional)" if not required else ""}')
    if list(next_questions.keys()) != []:
        print(f'Opções: {list(next_questions.keys())}')
    if default is not None:
        default = str(default)
        print(f'Não digite nada para escolher "{default}"')
    answer = input(f'{name}: ')
    if required and next_questions != {}:
        while answer not in list(next_questions.keys()):
            print(f'{answer} deve estar em {list(next_questions.keys())}!')
            answer = input(f'{name}: ')
        for question in next_questions[answer]:
            process_question(question)
    if required and answer == '':
        if default is not None:
            answer = default
        while answer == '':
            print(f'{name} é obrigatório!')
            answer = input(f'{name}: ')
    return answer


def process_question(question):
    name = question['name']
    title = question['title']
    default = question.get('default', None)
    ask = question.get('ask', True)
    required = question.get('required', False)
    next_questions = question.get('next', {})
    value = default
    if ask:
        value = ask_user(name, title, required, default, next_questions)
    env_string = f'\n# {title}\n{name}={value}\n'
    with open(".env-temp", "a") as file:
        file.write(env_string)


def process_questions(questions):
    with open(".env-temp", "w+") as file:
        file.write('# Environment Variables\n')
    for question in questions:
        process_question(question)


env = [
    {
        'name': 'DEBUG',
        'title': 'Ativar modo de debug',
        'default': True,
        'ask': False
    },
    {
        'name': 'SECRET_KEY',
        'title': 'Chave privada de encriptação usada pelo Django',
        'default': get_random_string(32),
        'ask': False,
    },
    {
        'name': 'EMAIL_ACCOUNT',
        'title': 'Endereço de email para envio de logs de erro',
        'ask': True,
        'required': True
    },
    {
        'name': 'EMAIL_PASSWORD',
        'title': 'Senha do endereço de email',
        'ask': True,
        'required': True
    },
    {
        'name': 'ADMIN_ACCOUNT',
        'title': 'Conta de admin para receber logs de erro',
        'default': 'gustavomaronato@gmail.com',
        'ask': True,
        'required': True
    },
    {
        'name': 'SHOW_TOOLBAR_CALLBACK',
        'title': 'Mostrar toolbar de debug do Django',
        'default': True,
        'ask': False,
        'required': True
    },
    {
        'name': 'DATABASE_URL',
        'title': 'URI para seu banco de dados Postgres',
        'default': 'postgresql://localhost/',
        'ask': False,
        'required': True
    }
]


def revert_changes():
    print('\n')
    print('Revertendo alterações...')
    os.remove('.env-temp')


def process_env():
    try:
        process_questions(env)
        r = request_input('Salvar alterações?', ['s', 'n'])
        if r == 's':
            print('Salvando...')
            copyfile('.env-temp', '.env')
            os.remove('.env-temp')
        else:
            revert_changes()
    except KeyboardInterrupt:
        revert_changes()


def process_db():
    r = request_input('Migrar banco de dados?', ['s', 'n'])
    if r == 's':
        print('Migrando banco de dados...')
        print(subprocess.check_output(['python', 'manage.py', 'migrate']).decode("utf-8"))


if __name__ == "__main__":
    ask_questions = True
    if os.path.isfile('.env'):
        print('Arquivo de variáveis de ambiente já existe')
        r = request_input('Deseja substituí-lo?', ['s', 'n'])
        if r == 'n':
            ask_questions = False
    if ask_questions:
        process_env()
    process_db()
